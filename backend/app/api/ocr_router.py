# app/api/ocr_router.py

from fastapi import APIRouter, HTTPException
from app.services.ocr_service import OCRService
from app.services.document_service import DocumentService
from app.models.ocr_response import OCRResponse

router = APIRouter(prefix="/api", tags=["OCR"])

ocr = OCRService()
document_service = DocumentService()


@router.post("/ocr/{file_id}", response_model=OCRResponse)
async def perform_ocr(file_id: str):
    """
    Send the file to Google Document AI → get text → save to cache → return text.
    """

    # 1. Ensure file exists
    try:
        raw_bytes = document_service.read_file_bytes(file_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    # 2. Perform OCR using Google Document AI
    try:
        result = ocr.perform_ocr(file_id)
        text = result.get("text", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Save OCR text to cache so /detect + /extract can use it
    try:
        document_service.save_ocr_text(file_id, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save OCR cache: {e}")

    # 4. Return clean response
    return OCRResponse(
        file_id=file_id,
        text=text
    )
