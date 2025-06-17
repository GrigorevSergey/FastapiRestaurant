from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    number_phone: str
    is_admin: bool = False
    is_phone_verified: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserInDB(User):
    hashed_password: str 