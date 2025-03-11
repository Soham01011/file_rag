from pydantic import BaseModel, Field, EmailStr

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=32)

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=32)
    conf_pass: str = Field(..., min_length=8, max_length=32)

class Token(BaseModel):
    access_token: str
    token_type: str
