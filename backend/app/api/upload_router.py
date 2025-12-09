# app/api/upload_router.py

from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.models.upload_response import UploadResponse

router = APIRouter(prefix="/api", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return UploadResponse(
        file_id=file_id,
        filename=file.filename
    )
