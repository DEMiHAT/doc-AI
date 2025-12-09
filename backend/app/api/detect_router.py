from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.document_service import DocumentService
from app.detectors.document_classifier import DocumentClassifier
from app.models.detect_response import DetectResponse

router = APIRouter(prefix="/api", tags=["Document Detection"])

document_service = DocumentService()
classifier = DocumentClassifier()


@router.post("/detect", response_model=DetectResponse)
async def detect_document(file_id: str):
    """
    Detect the document type using the rule-based classifier.
    """

    # Load text from the stored OCR result or raw file
    text = document_service.get_text(file_id)
    if not text:
        raise HTTPException(status_code=400, detail="No text found for this file_id")

    # Classification
    try:
        doc_type, confidence = classifier.classify(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    return DetectResponse(
        file_id=file_id,
        document_type=doc_type,
        confidence=confidence,
    )
