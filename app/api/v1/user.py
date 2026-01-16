from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette import status

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