from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.file_service import save_file, record_file_metadata, get_user_files
from app.services.web_scraper import scrape_web_page
from app.api.dependencies import get_current_user
from app.schemas.file import FileUpload, Myfiles
from bson import ObjectId
from typing import List
from app.database.connection import files_collection
import os 

router = APIRouter(prefix="/files", tags=["Files"])

ALLOWED_FILE_TYPES = {
    "text/plain",      # .txt
    "application/pdf", # .pdf
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "text/csv"  # .csv
}

@router.post("/upload")
async def upload_file(
    file: UploadFile = None,
    link: str = None,
    current_user: dict = Depends(get_current_user)
):
    if file and link:
        raise HTTPException(status_code=400, detail="Provide either a file or a URL, not both.")
    
    if file:
        # Validate file type
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type. Only TXT, PDF, DOC, DOCX, and CSV files are allowed.")
        
        # Save the uploaded file
        file_path = await save_file(file)

        # Record file metadata
        metadata = await record_file_metadata(file.filename, current_user["username"], file_path)
    
    elif link:
    # Scrape web page and get the saved file path
        file_path = await scrape_web_page(link)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="No content found on the provided URL.")

        # Get the actual filename from the file path
        filename = os.path.basename(file_path)

        # Save metadata correctly
        metadata = await record_file_metadata(filename, current_user["username"], file_path)
    
    else:
        raise HTTPException(status_code=400, detail="Either a file or a URL is required.")

    return {"message": "Data processed successfully", "metadata": metadata}


@router.get("/metadata/{file_id}", response_model=FileUpload)
async def get_file_metadata(file_id: str, current_user: dict = Depends(get_current_user)):
    # Retrieve file metadata from MongoDB.
    file_data = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Allow access only to the owner.
    if file_data["username"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="You are not authorized to access this file")
    
    file_data["id"] = str(file_data["_id"])
    return file_data

@router.get("/myfiles", response_model=List[Myfiles])
async def get_my_files(user: dict = Depends(get_current_user)):
    user_files = await get_user_files(user["username"])  # Await the async function
    return user_files



