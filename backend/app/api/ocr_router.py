from fastapi import APIRouter, HTTPException
from app.services.ocr_service import OCRService
from app.services.file_service import FileService
import os
router = APIRouter()
ocr = OCRService()
file_service = FileService()

@router.get("/ocr/{file_id}")
def run_ocr(file_id: str):

    # Find file path from uploads directory
    upload_dir = "uploads"
    for filename in os.listdir(upload_dir):
        if filename.startswith(file_id):
            file_path = f"{upload_dir}/{filename}"
            break
    else:
        raise HTTPException(404, "File not found")

    # Run OCR
    result = ocr.extract_text(file_path)

    return {
        "file_id": file_id,
        "text": result["text"],
        "entities": result["entities"],
        "pages": result["pages"]
    }
