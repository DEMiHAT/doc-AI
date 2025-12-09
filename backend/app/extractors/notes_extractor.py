# app/extractors/notes_extractor.py

from typing import List, Optional
from pydantic import BaseModel, Field

from app.services.nlp_service import nlp_service


class NotesExtractionResult(BaseModel):
    document_type: str = Field(default="notes")
    title: Optional[str] = None
    key_points: List[str] = []
    summary: Optional[str] = None
    raw_text: str = ""


class NotesExtractor:
    """
    Extractor for unstructured notes, meeting minutes, etc.
    """

    def extract(self, text: str) -> NotesExtractionResult:
        if not text:
            return NotesExtractionResult(raw_text="")

        cleaned = nlp_service.clean_text(text)
        lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]

        title = lines[0] if lines else None
        summary = nlp_service.summarize_text(cleaned, max_sentences=3)
        key_points = nlp_service.bullet_points(cleaned, max_points=10)

        return NotesExtractionResult(
            title=title,
            key_points=key_points,
            summary=summary,
            raw_text=cleaned,
        )


notes_extractor = NotesExtractor()
