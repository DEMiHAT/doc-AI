from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
from app.services.file_service import FileService

router = APIRouter()
file_service = FileService()

@router.post("/")
async def upload_document(file: UploadFile = File(...)):

    # Read file bytes
    file_bytes = await file.read()

    # Generate unique ID
    file_id = str(uuid4())

    # Get original extension
    if "." in file.filename:
        ext = file.filename.split(".")[-1]
    else:
        ext = "bin"

    saved_name = f"{file_id}.{ext}"

    # Save file
    file_path = file_service.save_file(file_bytes, saved_name)

    return {
        "file_id": file_id,
        "filename": saved_name,
        "path": file_path
    }
