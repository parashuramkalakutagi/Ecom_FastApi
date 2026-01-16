
from datetime import datetime, timezone
from decouple import config
from jose import jwt, JWTError
# app/services/token_blacklist.py
from datetime import datetime, timezone
from jose import jwt
from app.core.Redis_auth import redis_client
from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Optional: token expiry check
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
