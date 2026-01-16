import uuid
from datetime import datetime, date
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum

from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette import status


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    others = "others"


class UserBase(BaseModel):
  email: str
  is_active: bool = True
  is_admin: bool = False
  is_verified: bool = False

class UserCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: Optional[str] = None
    phone: str
    gender: Optional[str] = None
    password: str = Field(...)


class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: str
    gender: Optional[str] = None
    is_active: bool
    is_admin: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
  phone: str
  password: str

class UserOut(BaseModel):
    user_id: int
    email: Optional[str] = None
    phone: str
    gender: Optional[str] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"