import numpy as np
from datetime import datetime
from app.database.connection import chats_collection
from app.services.gemini_api import get_gemini_response
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from app.services.embedding import search_user_index, embed_text
from app.services.file_service import get_files_by_ext_ids
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_chat(username: str, user_message: str):
    """
    Handles chat messages, sends them to Gemini API with the last 10 messages as context,
    and stores responses in the database.
    """
    logger.info(f"Processing chat for user: {username}")
    
    # Fetch the last 10 chats of the user to use as context
    past_chats = await chats_collection.find({"username": username}).sort("timestamp", -1).limit(10).to_list(10)
    
    # Format past chats as context
    context = "\n".join([f"User: {chat['user_message']}\nBot: {chat['gemini_response']}" for chat in past_chats[::-1]])
    
    try:
        # Search for relevant documents using the original text
        ext_ids = search_user_index(username, user_message, k=3)
        doc_texts = await get_files_by_ext_ids(username, ext_ids)
        doc_context = "\n".join([f"[Relevant Document {i+1}]\n{text}" for i, text in enumerate(doc_texts)])
        print(doc_context)
        logger.info(f"Retrieved {len(doc_texts)} relevant documents")
    except Exception as e:
        logger.error(f"Error retrieving relevant documents: {str(e)}")
        doc_context = ""
    
    # Send user message with context to Gemini API
    prompt = f"Document Context:\n{doc_context}\n\nPrevious conversation:\n{context}\n\nNow, the user says: {user_message}\n\nRespond accordingly."
    
    try:
        gemini_response = await get_gemini_response(prompt)
        logger.info("Successfully received response from Gemini API")
    except Exception as e:
        logger.error(f"Error getting Gemini response: {str(e)}")
        gemini_response = "I'm sorry, I encountered an error processing your request. Please try again."
    
    # Store the chat in the database
    chat_entry = {
        "username": username,
        "user_message": user_message,
        "gemini_response": gemini_response,
        "timestamp": datetime.utcnow()
    }
    
    result = await chats_collection.insert_one(chat_entry)
    
    # Add `_id` as a string for JSON compatibility
    chat_entry["_id"] = str(result.inserted_id)
    
    # Maintain only the last 10 messages per user
    user_chat_count = await chats_collection.count_documents({"username": username})
    if user_chat_count > 10:
        oldest_chat = await chats_collection.find({"username": username}).sort("timestamp", 1).limit(1).to_list(1)
        if oldest_chat:
            await chats_collection.delete_one({"_id": oldest_chat[0]["_id"]})
            logger.info(f"Removed oldest chat for user: {username}")
    
    return jsonable_encoder(chat_entry)