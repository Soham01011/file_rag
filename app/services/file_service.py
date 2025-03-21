import os 
from datetime import datetime
from fastapi import UploadFile
import aiofiles
from app.database.connection import files_collection  
from typing import List
from app.services.document_loaders import extract_text_from_file
from app.services.embedding import add_text_to_user_index 
from textwrap import wrap

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
    """Stores file metadata and adds content to FAISS."""
    
    # Generate ext_id before inserting into MongoDB
    ext_id = abs(hash(f"{username}_{filename}")) % (10**12)

    file_data = {
        "filename": filename,
        "username": username,
        "filelocation": filelocation,
        "uploaded_at": datetime.utcnow(),
        "ext_id": ext_id  # Store ext_id directly
    }

    # Insert metadata into MongoDB (with ext_id already set)
    result = await files_collection.insert_one(file_data)

    # Extract text safely
    
    try:
        raw_text = extract_text_from_file(filelocation)
        
        if raw_text.strip():  # Ensure the file isn't empty
            words = raw_text.split()  # Split text into words
            chunk_size = 1000  # Define chunk size
            
            # Create chunks of 1000 words
            chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            
            for chunk in chunks:
                await add_text_to_user_index(username, chunk, ext_id)
        else:
            print(f"Warning: No text extracted from {filelocation}")
    except Exception as e:
        print(f"Error extracting text: {e}")

    # Convert _id for JSON response
    file_data["_id"] = str(result.inserted_id)

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
