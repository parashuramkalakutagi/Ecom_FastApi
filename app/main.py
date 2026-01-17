from app.api.v1.user import router as UserRouter
from app.api.v1.email_verify import router as EmailVerifyRouter
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="Ecommerce  Backend")


app.include_router(UserRouter)
app.include_router(EmailVerifyRouter)
