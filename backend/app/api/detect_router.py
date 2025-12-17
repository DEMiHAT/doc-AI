# app/api/detect_router.py

from fastapi import APIRouter, Query, HTTPException
from app.services.document_service import document_service
from app.llm.gemini_client import GeminiClient

router = APIRouter(prefix="/api", tags=["Document Detection"])
gemini = GeminiClient()

@router.post("/detect")
async def detect_document(file_id: str = Query(...)):
    text = document_service.get_text(file_id)

    if not text:
        raise HTTPException(status_code=400, detail="OCR missing. Run /api/ocr first.")

    result = gemini.classify_document(text)

    return {
        "file_id": file_id,
        "document_type": result.get("document_type", "unknown"),
        "confidence": result.get("confidence", 0.0),
    }
