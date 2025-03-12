from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

class ChatEntry(BaseModel):
    id: ObjectId
    username: str
    user_message: str
    gemini_response: str
    timestamp: datetime
