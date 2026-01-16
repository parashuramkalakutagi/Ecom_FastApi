from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession,AsyncAttrs

class Base(AsyncAttrs,DeclarativeBase):
    pass