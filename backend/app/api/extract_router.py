# app/api/extract_router.py

from fastapi import APIRouter, HTTPException
from app.services.document_service import document_service
from app.llm.gemini_client import GeminiClient
from app.services.nlp_service import nlp_service

router = APIRouter(prefix="/api", tags=["Extraction"])
gemini = GeminiClient()

@router.post("/extract/{file_id}")
async def extract_document(
    file_id: str,
    override_type: str | None = None,
    include_summary: bool = False,
    include_embeddings: bool = False
):
    # 1. Get OCR text
    text = document_service.get_text(file_id)
    if not text:
        raise HTTPException(status_code=400, detail="OCR missing. Run /api/ocr first.")

    # 2. Detect type using Gemini
    detected = gemini.classify_document(text)
    detected_type = detected.get("document_type")
    confidence = detected.get("confidence", 0.0)

    # Use override only if provided
    used_type = override_type or detected_type

    # 3. Extract structured information
    extraction = gemini.extract_structured(text, used_type)

    # 4. Summary
    summary = gemini.summarize(text) if include_summary else None

    # 5. Embeddings
    embeddings = nlp_service.embed_text(text) if include_embeddings else None

    return {
        "file_id": file_id,
        "detected_type": detected_type,
        "used_type": used_type,
        "override_used": override_type is not None,
        "detection_confidence": confidence,
        "extraction": extraction,
        "summary": summary,
        "embeddings": embeddings,
    }
