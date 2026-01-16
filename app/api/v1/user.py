from fastapi import APIRouter
from starlette import status

from app.db.config import SessionDep
from app.schemas.user import UserCreate, UserOut
from app.services.user import create_user

router = APIRouter(prefix="/v1/users", tags=["Account"])




@router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)
async def register(db:SessionDep, user: UserCreate):
  return await create_user(db, user)