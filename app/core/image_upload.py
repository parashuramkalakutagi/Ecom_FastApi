from pathlib import Path
from fastapi import UploadFile, HTTPException
import uuid

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_file(file: UploadFile, content: bytes):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, WEBP images are allowed"
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5MB limit"
        )
    return ext

PRODUCT_UPLOAD_DIR = Path("media/products")
PRODUCT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_product_image(file: UploadFile) -> str:
    content = await file.read()
    ext = validate_file(file, content)

    filename = f"{uuid.uuid4()}.{ext}"
    file_path = PRODUCT_UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(content)

    return f"/media/products/{filename}"


BANNER_UPLOAD_DIR = Path("media/banners")
BANNER_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_banner_image(file: UploadFile) -> str:
    content = await file.read()
    ext = validate_file(file, content)

    filename = f"{uuid.uuid4()}.{ext}"
    file_path = BANNER_UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(content)

    return f"/media/banners/{filename}"
