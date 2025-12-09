# app/api/extract_router.py

from typing import Any, Dict, Optional, List, Literal

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

# Services
from app.services.nlp_service import nlp_service
from app.services.ocr_service import OCRService
from app.detectors.document_classifier import DocumentClassifier

# Extractors
from app.extractors.invoice_extractor import invoice_extractor, InvoiceExtractionResult
from app.extractors.receipt_extractor import receipt_extractor, ReceiptExtractionResult
from app.extractors.notes_extractor import notes_extractor, NotesExtractionResult
from app.extractors.po_extractor import po_extractor, POExtractionResult
from app.extractors.id_extractor import id_extractor, IDExtractionResult

router = APIRouter(prefix="/api", tags=["Extraction"])

ocr_service = OCRService()
document_classifier = DocumentClassifier()


# -------------------- MODELS --------------------

class ExtractionRequest(BaseModel):
    override_type: Optional[
        Literal["invoice", "receipt", "notes", "purchase_order", "id_card"]
    ] = None
    include_summary: bool = False
    include_embeddings: bool = False


class ExtractionResponse(BaseModel):
    file_id: str
    detected_type: Optional[str]
    used_type: Optional[str]
    detection_confidence: Optional[float]
    override_used: bool
    extraction: Dict[str, Any]
    summary: Optional[str] = None
    embeddings: Optional[List[float]] = None


# -------------------- HELPER --------------------

def _run_extractor(doc_type: str, text: str) -> Dict[str, Any]:
    doc_type = doc_type.lower()

    if doc_type == "invoice":
        return invoice_extractor.extract(text).dict()

    if doc_type == "receipt":
        return receipt_extractor.extract(text).dict()

    if doc_type == "notes":
        return notes_extractor.extract(text).dict()

    if doc_type in ("purchase_order", "po"):
        return po_extractor.extract(text).dict()

    if doc_type in ("id_card", "id"):
        return id_extractor.extract(text).dict()

    return notes_extractor.extract(text).dict()  # fallback


# -------------------- ENDPOINT --------------------

@router.post("/extract/{file_id}", response_model=ExtractionResponse)
async def extract_document(file_id: str, request: ExtractionRequest):
    """
    Main document extraction pipeline:
    1. OCR using Google Document AI
    2. Clean text
    3. Document Classification
    4. (Optional) Override type from frontend
    5. Run extractor
    6. Summary + Embeddings (optional)
    """

    # -------------------- STEP 1: OCR --------------------
    try:
        ocr_result = ocr_service.perform_ocr(file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    if isinstance(ocr_result, dict):
        raw_text = ocr_result.get("text", "")
    else:
        raw_text = getattr(ocr_result, "text", "")

    if not raw_text:
        raise HTTPException(status_code=400, detail="OCR failed: empty text output")

    # -------------------- STEP 2: CLEAN --------------------
    cleaned_text = nlp_service.clean_text(raw_text)

    # -------------------- STEP 3: CLASSIFY --------------------
    try:
        classification = document_classifier.classify(cleaned_text)
        if isinstance(classification, tuple):
            detected_type, confidence = classification
        else:
            detected_type = classification.get("doc_type")
            confidence = classification.get("confidence")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document classification failed: {str(e)}")

    used_type = detected_type
    override_used = False

    # -------------------- STEP 4: OVERRIDE --------------------
    if request.override_type:
        used_type = request.override_type
        override_used = True

    if not used_type:
        used_type = "notes"  # safe fallback

    # -------------------- STEP 5: EXTRACT --------------------
    extraction = _run_extractor(used_type, cleaned_text)

    # -------------------- STEP 6: SUMMARY / EMBEDDINGS --------------------
    summary = None
    embeddings = None

    if request.include_summary:
        summary = nlp_service.summarize_text(cleaned_text)

    if request.include_embeddings:
        embeddings = nlp_service.get_embeddings(cleaned_text)

    return ExtractionResponse(
        file_id=file_id,
        detected_type=detected_type,
        used_type=used_type,
        detection_confidence=confidence,
        override_used=override_used,
        extraction=extraction,
        summary=summary,
        embeddings=embeddings,
    )
