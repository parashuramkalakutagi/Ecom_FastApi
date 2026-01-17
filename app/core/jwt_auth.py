
from datetime import datetime, timezone
from decouple import config
from jose import jwt, JWTError
# app/services/token_blacklist.py
from datetime import datetime, timezone
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.Redis_auth import redis_client
from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.config import SessionDep, get_session
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")



def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        user_email: str = payload.get("email")
        # print(payload.items())

        if not user_id or not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data",
            )

        # Optional: expiry check
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

        return {
            "user_id": int(user_id),
            "email": user_email,
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )




async def require_admin( user_payload: dict = Depends(verify_jwt_token),db: AsyncSession = Depends(get_session)):
    # Validate token payload
    if not isinstance(user_payload, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid token payload",
        )

    user_id = user_payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing user_id in token",
        )

    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Ensure user has admin role
    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only",
        )

    return user







def verify_refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Optional: token expiry check
        token_type = payload.get("token_type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="its not expired",
            )

        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

        return {
            "user_id": int(user_id),
            "email": payload.get("email"),
            "role": payload.get("role") or None,
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )




BLACKLIST_PREFIX = "blacklisted_refresh_token:"

async def blacklist_refresh_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp = payload.get("exp")

    if not exp:
        raise ValueError("Token has no expiry")

    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())

    if ttl > 0:
        await redis_client.setex(
            f"{BLACKLIST_PREFIX}{token}",
            ttl,
            "true"
        )
