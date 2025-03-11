from pydantic import BaseModel
from datetime import datetime

class FileUpload(BaseModel):
    filename: str
    username: str
    filelocation: str
    uploaded_at: datetime
