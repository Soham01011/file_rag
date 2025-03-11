from pydantic import BaseModel, EmailStr

class UserModel(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
