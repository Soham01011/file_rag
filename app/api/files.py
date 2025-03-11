from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.file_service import save_csv_file, record_file_metadata
from app.api.dependencies import get_current_user
from app.schemas.file import FileUpload
from bson import ObjectId
from app.database.connection import files_collection

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Validate that the uploaded file is a CSV.
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
    # Save the CSV file.
    file_path = await save_csv_file(file)
    
    # Record file metadata with the owner's username.
    metadata = await record_file_metadata(file.filename, current_user["username"], file_path)
    
    return {"message": "File uploaded successfully", "file_metadata": metadata}

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
