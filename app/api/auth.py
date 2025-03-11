from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserLogin, Token, UserRegister
from app.services.auth_service import authenticate_user, register_data
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    print("Login : ", user)
    db_user = await authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token_data = {"sub": db_user["username"]}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    # Call the registration service with the provided data
    registered_user = await register_data(user.username, user.email, user.password, user.conf_pass)
    
    # If registration fails (an error is returned), raise an HTTP exception
    if "error" in registered_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=registered_user["error"])
    
    # Create a token payload (e.g., using username as subject)
    token_data = {"sub": registered_user["username"]}
    access_token = create_access_token(token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}
