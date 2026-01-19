from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette import status

from app.core.email_verification import create_email_token, decode_email_token, send_verification_email
from app.core.jwt_auth import verify_jwt_token
from app.db.config import SessionDep
from app.models import User

router = APIRouter(prefix="/v1/users", tags=["Account"])




@router.post("/send_verification_email", status_code=status.HTTP_200_OK)
async def send_verification_email_user(
    user: dict = Depends(verify_jwt_token),
):
    # SAFETY CHECK
    if not isinstance(user, dict):
        raise HTTPException(status_code=500, detail="Invalid user payload")

    user_email = user.get("email")

    if not user_email:
        raise HTTPException(status_code=400, detail="User email not found")

    token = create_email_token(user_email)
    await send_verification_email(user_email, token)

    return {"message": "Verification email sent"}



@router.get("/verify-email")
async def verify_email(token: str, db:SessionDep ):
    try:
        payload = decode_email_token(token)
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    user.is_verified = True
    user.is_admin = True
    await db.commit()

    return {"message": "Email verified successfully"}


