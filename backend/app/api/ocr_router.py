from fastapi import APIRouter, HTTPException
from app.services.ocr_service import ocr_service
from app.services.document_service import document_service
from app.models.ocr_response import OCRResponse

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

@router.post("/{file_id}", response_model=OCRResponse)
async def perform_ocr(file_id: str):

    try:
        raw_bytes = document_service.read_file_bytes(file_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        text = ocr_service.extract_text(raw_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document AI OCR failed: {str(e)}"
        )

    document_service.save_text(file_id, text)

    return OCRResponse(file_id=file_id, text=text)
