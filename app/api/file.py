from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import save_csv_file

router = APIRouter(prefix="/files",tags=["Files"])

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if file.content_type !="text/csv":
        raise HTTPException(status_code=400, detail="Invalid File Type. Only CSV are allowed.")
    
    file_path = await save_csv_file(file)

    return{"message": "File uploaded successfully"}