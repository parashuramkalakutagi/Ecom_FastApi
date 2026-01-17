import uuid
from datetime import timedelta, datetime, timezone
import phonenumbers
from decouple import config
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from fastapi import HTTPException
from starlette import status

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.auth import normalize_indian_phone, hash_password, create_access_token, create_refresh_token

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")



async def create_user(db: AsyncSession, user: UserCreate):
    try:
        phone = normalize_indian_phone(user.phone)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    stmt = select(User).where(User.phone == phone)
    if await db.scalar(stmt):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="phone_number already registered",
        )

    # Create user
    new_user = User(
        name=user.name,
        email=str(user.email),
        phone=user.phone,
        gender=user.gender,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    access_token = create_access_token(data={"sub": str(new_user.id),"email":new_user.email, "token_type": "access"})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id),"email":new_user.email, "token_type": "access"})
    await db.refresh(new_user)

    return {
        "user_id": new_user.id,
        "email": new_user.email,
        "phone": new_user.phone,
        "gender": new_user.gender,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }