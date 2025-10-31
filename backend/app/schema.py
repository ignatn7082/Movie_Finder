# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterIn(BaseModel):
    username: str
    password: str
    email: EmailStr

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    role: str
    is_active: bool

    class Config:
        orm_mode = True



class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr | None
    role: str

    class Config:
        orm_mode = True