import os 
from datetime import datetime
from fastapi import UploadFile
import aiofiles
from app.database.connection import files_collection  
from typing import List
from app.services.document_loaders import extract_text_from_file
from app.services.embedding import add_text_to_user_index  # from vector_store.py

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

async def save_file(uploaded_file: UploadFile) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{uploaded_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await uploaded_file.read()  # Read file content
        await out_file.write(content)
    
    return file_path  

# file_service.py (updated)
async def record_file_metadata(filename: str, username: str, filelocation: str) -> dict:
    file_data = {
        "filename": filename,
        "username": username,
        "filelocation": filelocation,
        "uploaded_at": datetime.utcnow()
    }

    # Insert document into MongoDB
    result = await files_collection.insert_one(file_data)
    file_id = result.inserted_id  # Get the MongoDB ObjectId

    # Generate ext_id from the ObjectId
    ext_id = abs(hash(str(file_id))) % (10**12)

    # Update the document to store ext_id
    await files_collection.update_one(
        {"_id": file_id}, 
        {"$set": {"ext_id": ext_id}}
    )

    # Extract text and add to FAISS index
    raw_text = extract_text_from_file(filelocation)
    add_text_to_user_index(username, raw_text, ext_id)

    return file_data

async def get_user_files(username: str) -> List[dict]:
    files_cursor = files_collection.find({"username": username})
    files = await files_cursor.to_list(length=None)  
    return files

# file_service.py (new method)
async def get_files_by_ext_ids(username: str, ext_ids: List[int]) -> List[str]:
    docs = await files_collection.find(
        {"username": username, "ext_id": {"$in": ext_ids}}
    ).to_list(length=None)
    return [extract_text_from_file(doc["filelocation"]) for doc in docs]
