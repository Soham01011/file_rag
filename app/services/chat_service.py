from datetime import datetime
from app.database.connection import chats_collection
from app.services.gemini_api import get_gemini_response
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from app.services.embedding import search_user_index, embed_text
from app.services.file_service import get_files_by_ext_ids

async def process_chat(username: str, user_message: str):
    """
    Handles chat messages, sends them to Gemini API with the last 10 messages as context, 
    and stores responses in the database.
    """
    # Fetch the last 10 chats of the user to use as context
    past_chats = await chats_collection.find({"username": username}).sort("timestamp", -1).limit(10).to_list(10)
    
    # Format past chats as context
    context = "\n".join([f"User: {chat['user_message']}\nBot: {chat['gemini_response']}" for chat in past_chats])

    query_embedding = embed_text(user_message)

    ext_ids = search_user_index(username, query_embedding, k=3)
    doc_texts = await get_files_by_ext_ids(username, ext_ids)
    doc_context = "\n".join([f"[Relevant Document {i+1}]\n{text}" 
                           for i, text in enumerate(doc_texts)])
    print("######## DOC CONTEXT : ",doc_context)
    # Send user message with context to Gemini API
    prompt = f"Document Context:\n{doc_context}Previous conversation:\n{context}\nNow, the user says: {user_message}\nRespond accordingly."
    gemini_response = await get_gemini_response(prompt)

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

    # Convert response to JSON-compatible format
    return jsonable_encoder(chat_entry)
