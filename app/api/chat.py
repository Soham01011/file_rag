from fastapi import APIRouter, Depends
from app.services.chat_service import process_chat
from app.api.dependencies import get_current_user
from app.schemas.chat import ChatRequest

router = APIRouter()

router = APIRouter(prefix="/chat", tags=["Auth"])

@router.post("/chat")
async def chat(request: ChatRequest, username: dict = Depends(get_current_user)):
    """
    API endpoint to handle user chats.
    """
    print("User Prompt:", request.user_message)
    print("Username:", username["username"])

    return await process_chat(username["username"], request.user_message)
