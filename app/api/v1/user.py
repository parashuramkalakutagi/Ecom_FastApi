from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.core.jwt_auth import verify_refresh_token, blacklist_refresh_token
from app.db.config import SessionDep, get_session
from app.models import User
from app.schemas.user import UserCreate, UserOut, UserResponse, LoginResponse, UserLogin, RefreshResponse, \
    ForgotPasswordResponse, ForgotPasswordSchema, ResetPasswordResponse, ResetPasswordSchema
from app.services.user import create_user
from app.utils.auth import verify_password, create_access_token, create_refresh_token, hash_password
from app.utils.otp import generate_otp, otp_expiry

router = APIRouter(prefix="/v1/users", tags=["Account"])




@router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)
async def register(db:SessionDep, user: UserCreate):
  return await create_user(db, user)


@router.get("/all_user", response_model=list[UserResponse])
async def get_users(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(User))
        return result.scalars().all()
    except Exception:
        raise HTTPException(status_code=404, detail="Users not found")





@router.post("/login",response_model=LoginResponse,status_code=status.HTTP_201_CREATED)
async def login(data: UserLogin, db: SessionDep):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "token_type": "access"})
    refresh_token = create_refresh_token({"sub": str(user.id), "token_type": "refresh"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=RefreshResponse, status_code=status.HTTP_201_CREATED)
async def get_refresh_token(data: dict = Depends(verify_refresh_token)):
    access_token = create_access_token({"sub": str(data["user_id"]), "token_type": "refresh"})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot_password",response_model=ForgotPasswordResponse,status_code=status.HTTP_201_CREATED)
async def forgot_password(data: ForgotPasswordSchema, db:SessionDep):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.otp = generate_otp()
    user.expires_at = otp_expiry()

    await db.commit()
    # 🔴 Replace this with SMS gateway
    print("OTP:", user.otp)
    return JSONResponse(content={"message": "OTP sent to registered phone number","data":None},status_code=201)


@router.post("/reset_password",response_model=ResetPasswordResponse,status_code=status.HTTP_201_CREATED)
async def reset_password(data: ResetPasswordSchema, db: SessionDep):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp != data.otp or user.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.hashed_password = hash_password(data.new_password)
    user.otp = None

    await db.commit()
    return {"message": "Password reset successfully"}




@router.post("/logout")
async def logout(refresh_token: str):
    try:
        await blacklist_refresh_token(refresh_token)
        return {"message": "Logged out successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )