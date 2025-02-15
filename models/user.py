from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str = "staff"  # "admin", "commissioner", "staff"

class UserCreate(UserBase):
    password: str
    profile_image: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    role: Optional[str] = None

class UserInDB(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    password_hash: str
    profile_image: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(UserBase):
    id: str
    profile_image: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True