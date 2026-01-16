from app.api.v1.user import router as UserRouter
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="Ecommerce  Backend")


app.include_router(UserRouter)
