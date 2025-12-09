# app/services/nlp_service.py

from typing import List, Optional
import re

from app.utils.text_utils import basic_clean_text
# <-- adjust if name differs


class NLPService:
    """
    Core NLP utilities for DocAI.

    - Text cleaning (uses utils/text_cleaner)
    - Summarization stub (rule-based)
    - Embedding stub (to be replaced with Gemini / Vertex AI)
    """

    def clean_text(self, text: str) -> str:
        """
        Run generic cleaning pipeline on raw OCR text.
        """
        if not text:
            return ""
        cleaned = basic_clean_text(text)
        # Extra normalization if needed
        cleaned = re.sub(r"\s+\n", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """
        Very simple heuristic summarizer.
        - Splits into sentences by punctuation.
        - Returns the first N sentences.

        TODO: Replace with Gemini / Vertex AI summarization.
        """
        if not text:
            return ""

        # Naive sentence split
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return ""

        return " ".join(sentences[:max_sentences])

    def bullet_points(self, text: str, max_points: int = 5) -> List[str]:
        """
        Simple bullet point extractor:
        - Splits text into lines and picks non-empty ones.
        - Truncates to max_points.

        TODO: Replace with smarter key point extraction using LLM.
        """
        if not text:
            return []

        lines = [ln.strip("-• \t") for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]
        return lines[:max_points]

    def get_embeddings(self, text: str, dim: int = 64) -> List[float]:
        """
        Embedding provider stub.

        CURRENT:
        - Returns a deterministic pseudo-embedding by hashing.
        - Only for development.

        TODO: Replace with:
        - Gemini embeddings
        - or Vertex AI Text Embedding models.
        """
        if not text:
            return [0.0] * dim

        # Simple, deterministic hash-based pseudo embedding
        import hashlib

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        floats: List[float] = []
        for b in digest:
            floats.append((b - 128) / 128.0)

        # Repeat/trim to required dim
        if len(floats) >= dim:
            return floats[:dim]
        else:
            reps = (dim + len(floats) - 1) // len(floats)
            extended = (floats * reps)[:dim]
            return extended


# Singleton-style instance you can import anywhere
nlp_service = NLPService()
