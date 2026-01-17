from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.jwt_auth import require_admin, blacklist_refresh_token
from app.db.config import SessionDep, get_session
from app.models import User
from app.schemas.user import UserCreate, UserOut, UserResponse, LoginResponse, UserLogin
from app.services.user import create_user
from app.utils.auth import verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/v1/users", tags=["Account"])




@router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)
async def register(db:SessionDep, user: UserCreate):
  return await create_user(db, user)


@router.get("/all_user", response_model=list[UserResponse])
async def get_users(session: AsyncSession = Depends(get_session),admin: User = Depends(require_admin)):
    try:
        result = await session.execute(select(User))
        return result.scalars().all()
    except Exception:
        raise HTTPException(status_code=404, detail="Users not found")


@router.get("/admin/dashboard")
async def admin_dashboard(
    admin: User = Depends(require_admin)
):
    return {"message": f"Welcome Admin {admin.name}"}





@router.post("/login",response_model=LoginResponse,status_code=status.HTTP_201_CREATED)
async def login(data: UserLogin, db: SessionDep):
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "email":user.email,"token_type": "access"})
    refresh_token = create_refresh_token({"sub": str(user.id), "email":user.email,"token_type": "refresh"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



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