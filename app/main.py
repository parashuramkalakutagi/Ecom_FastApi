from app.api.v1.user import router as UserRouter
from app.api.v1.email_verify import router as EmailVerifyRouter
from app.api.v1.products import router as ProductsRouter
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="Ecommerce  Backend")


app.include_router(UserRouter)
app.include_router(EmailVerifyRouter)
app.include_router(ProductsRouter)
app.mount("/media", StaticFiles(directory="media"), name="media")