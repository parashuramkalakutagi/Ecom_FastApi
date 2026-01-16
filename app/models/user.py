from typing import List,Optional
import enum
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.orm import Mapped,MappedColumn,relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer,Enum
from datetime import datetime,timedelta,timezone
from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    others = "others"




class User(Base):

    __tablename__ = 'user'

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = MappedColumn(String(100), nullable=False)
    email: Mapped[str] = MappedColumn(String(255), nullable=True,default=None)
    phone: Mapped[str] = MappedColumn(String(15), unique=True, nullable=False)
    gender: Mapped[str] = MappedColumn(String(20),nullable=True, default=None)

    hashed_password: Mapped[str] = MappedColumn(String(255), nullable=False)
    otp: Mapped[Optional[str]] = MappedColumn(String(6))
    expires_at: Mapped[Optional[datetime]] = MappedColumn(DateTime(timezone=True))

    is_active: Mapped[bool] = MappedColumn(Boolean, default=True)
    is_admin: Mapped[bool] = MappedColumn(Boolean, default=False)
    is_superuser: Mapped[bool] = MappedColumn(Boolean, default=False)
    is_verified: Mapped[bool] = MappedColumn(Boolean, default=False)

    created_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

