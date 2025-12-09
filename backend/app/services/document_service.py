# app/services/document_service.py

import os
import json
from typing import Optional


class DocumentService:
    """
    Handles file storage, OCR text caching, reading files,
    and providing safe access for extractors + classifiers.
    """

    def __init__(self):
        # Base uploads directory
        self.upload_dir = os.path.join(os.getcwd(), "uploads")

        # Folder to store OCR json cache
        self.ocr_cache_dir = os.path.join(self.upload_dir, "ocr_cache")

        # Ensure folders exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.ocr_cache_dir, exist_ok=True)

    # -----------------------------------------------------------------
    # FILE PATH HELPERS
    # -----------------------------------------------------------------
    def get_file_path(self, file_id: str) -> str:
        """
        Returns the path for a raw uploaded file.
        """
        return os.path.join(self.upload_dir, file_id)

    def get_ocr_cache_path(self, file_id: str) -> str:
        """
        The OCR cache file is stored as JSON: uploads/ocr_cache/<file_id>.json
        """
        return os.path.join(self.ocr_cache_dir, f"{file_id}.json")

    # -----------------------------------------------------------------
    # READ FILES
    # -----------------------------------------------------------------
    def read_file_bytes(self, file_id: str) -> bytes:
        """
        Returns raw file bytes. Raises FileNotFoundError if missing.
        """
        file_path = self.get_file_path(file_id)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_id}")

        with open(file_path, "rb") as f:
            return f.read()

    # -----------------------------------------------------------------
    # OCR CACHING
    # -----------------------------------------------------------------
    def save_ocr_text(self, file_id: str, text: str):
        """
        Stores OCR text safely into JSON cache.
        """

        cache_path = self.get_ocr_cache_path(file_id)

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump({"text": text}, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise RuntimeError(f"Failed to save OCR cache for {file_id}: {e}")

    def get_text(self, file_id: str) -> str:
        """
        Returns OCR text if available.
        Returns "" if missing (never crashes).
        """

        cache_path = self.get_ocr_cache_path(file_id)

        if not os.path.exists(cache_path):
            return ""

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("text", "")

        except Exception:
            return ""  # fail safe

    # -----------------------------------------------------------------
    # CLEAN DELETE (optional for API housekeeping)
    # -----------------------------------------------------------------
    def delete_file(self, file_id: str):
        """
        Deletes both the raw upload and OCR cache for a file.
        Useful for cleaning temp files in production.
        """
        raw_path = self.get_file_path(file_id)
        cache_path = self.get_ocr_cache_path(file_id)

        try:
            if os.path.exists(raw_path):
                os.remove(raw_path)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        except Exception:
            pass  # never crash app; safe cleanup

