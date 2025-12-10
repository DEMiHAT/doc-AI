import os
import uuid
from typing import Optional

class DocumentService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.cache_dir = "cache"

        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    # ------------------------------------------
    # SAVE FILE
    # ------------------------------------------
    def save_file(self, file) -> str:
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"

        path = os.path.join(self.upload_dir, filename)

        with open(path, "wb") as f:
            f.write(file)

        return file_id

    # ------------------------------------------
    # READ RAW BYTES FOR OCR
    # ------------------------------------------
    def read_file_bytes(self, file_id: str) -> bytes:
        path = os.path.join(self.upload_dir, f"{file_id}.pdf")

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found in uploads/: {file_id}")

        with open(path, "rb") as f:
            return f.read()

    # ------------------------------------------
    # SAVE OCR TEXT TO CACHE
    # ------------------------------------------
    def save_text(self, file_id: str, text: str):
        path = os.path.join(self.cache_dir, f"{file_id}.txt")

        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    # ------------------------------------------
    # GET OCR TEXT FROM CACHE
    # ------------------------------------------
    def get_text(self, file_id: str) -> Optional[str]:
        path = os.path.join(self.cache_dir, f"{file_id}.txt")

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return f.read()


# Singleton instance
document_service = DocumentService()
