import uuid
from datetime import timedelta, datetime, timezone
import phonenumbers
from decouple import config
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from fastapi import HTTPException
import random
from datetime import timedelta, datetime, timezone
from decouple import config
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import  User
from fastapi import HTTPException
from sqlalchemy import select
import bcrypt
import hashlib
from app.models.user import User
from app.schemas.user import UserLogin

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")



JWT_SECRET_KEY = config("SECRET_KEY")
JWT_ALGORITHM = config("ALGORITHM")


def _prehash(password: str) -> bytes:
    """
    SHA-256 pre-hash to avoid bcrypt 72-byte limit
    """
    return hashlib.sha256(password.encode("utf-8")).digest()

def hash_password(password: str) -> str:
    prehashed = _prehash(password)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prehashed, salt)
    return hashed.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    prehashed = _prehash(password)
    return bcrypt.checkpw(
        prehashed,
        hashed_password.encode("utf-8")
    )






async def authenticate_user(session: AsyncSession, user_login: UserLogin):
    stmt = select(User).where(User.phone == user_login.phone_number)
    result = await session.scalars(stmt)
    user = result.first()

    if not user or not user_login.password == verify_password(user.hashed_password):
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def normalize_indian_phone(phone: str) -> str:
    parsed = phonenumbers.parse(phone, "IN")
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")
    national_number = str(parsed.national_number)
    if len(national_number) != 10:
        raise ValueError("Phone number must be 10 digits")
    return national_number