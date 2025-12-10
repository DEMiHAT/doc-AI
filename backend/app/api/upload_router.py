from fastapi import APIRouter, UploadFile, File
from app.services.document_service import document_service

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("")
async def upload(file: UploadFile = File(...)):
    # Read raw bytes
    file_bytes = await file.read()

    # Save raw bytes into service
    file_id = document_service.save_file(file_bytes)

    return {
        "file_id": file_id,
        "filename": file.filename
    }
