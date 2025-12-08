from fastapi import APIRouter, HTTPException
import os
from app.services.file_service import FileService
from app.detectors.document_classifier import DocumentClassifier

router = APIRouter()
file_service = FileService()
classifier = DocumentClassifier()


@router.post("/detect")
def detect_document(payload: dict):
    file_id = payload.get("file_id")

    if not file_id:
        raise HTTPException(status_code=400, detail="file_id is required")

    # Load file text
    file_path = file_service.get_file_path(file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    text = file_service.read_text(file_path)

    # Run classifier
    result = classifier.classify(text)

    doc_type = result["type"]
    confidence = result["confidence"]
    alternatives = result.get("alternatives", [])

    response = {
        "document_type": doc_type,
        "confidence": confidence,
        "alternatives": alternatives,
        "warning": None
    }

    if confidence < 0.60:
        response["warning"] = "Low confidence — document type may be incorrect."

    return response
