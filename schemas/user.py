from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Model for creating a new user."""
    email: EmailStr
    password: str
    connection: str = "Username-Password-Authentication"
    name: Optional[str] = None
    nickname: Optional[str] = None


class UserUpdate(BaseModel):
    """Model for updating a user."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
