import os 
from datetime import datetime
from fastapi import UploadFile
import aiofiles
from app.database.connection import files_collection  
from typing import List
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

async def save_file(uploaded_file: UploadFile) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename =  f"{timestamp}_{uploaded_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await uploaded_file.read()  # Read file content
        await out_file.write(content)
    
    return file_path  

async def record_file_metadata(filename: str, username: str, filelocation: str) -> dict:
    """
    Records file metadata in MongoDB, associating the file with its owner.
    Returns:
        dict: The stored metadata, including the generated file ID.
    """
    file_data = {
        "filename": filename,
        "username": username,
        "filelocation": filelocation,
        "uploaded_at": datetime.utcnow()
    }

    print(f"📌 Inserting File Metadata: {file_data}")

    result = await files_collection.insert_one(file_data)
    file_data["_id"] = str(result.inserted_id)

    return file_data

async def get_user_files(username: str) -> List[dict]:
    files_cursor = files_collection.find({"username": username})
    files = await files_cursor.to_list(length=None)  
    return files