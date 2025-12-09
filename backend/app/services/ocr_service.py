# app/services/ocr_service.py

import os
from typing import Optional

from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()


class OCRService:
    def __init__(self):
        # 1. Load env vars
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("PROJECT_ID")
        location = os.getenv("LOCATION_ID", "us")
        processor_id = os.getenv("PROCESSOR_ID")

        missing = []
        if not credentials_path:
            missing.append("GOOGLE_APPLICATION_CREDENTIALS")
        if not project_id:
            missing.append("PROJECT_ID")
        if not processor_id:
            missing.append("PROCESSOR_ID")

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Google DocumentAI credentials not found at: {credentials_path}"
            )

        # 2. Create client
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )

        self.client = documentai.DocumentProcessorServiceClient(
            credentials=credentials
        )

        self.name = self.client.processor_path(project_id, location, processor_id)

        # 3. Uploads dir
        self.uploads_dir = os.path.join(os.getcwd(), "uploads")

        print(f"[OCRService] Initialized with processor: {self.name}")

    # ----------------------------------------------------------
    # OCR
    # ----------------------------------------------------------
    def perform_ocr(self, file_id: str) -> dict:
        """
        Perform OCR on uploaded file and return {"text": "..."}.
        Assumes PDFs for now (application/pdf).
        """

        file_path = os.path.join(self.uploads_dir, file_id)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found in uploads/: {file_id}")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        raw_document = documentai.RawDocument(
            content=file_bytes,
            mime_type=self._guess_mime(file_path),
        )

        request = documentai.ProcessRequest(
            name=self.name,
            raw_document=raw_document,
        )

        try:
            result = self.client.process_document(request=request)
        except Exception as e:
            raise RuntimeError(f"Document AI OCR failed: {e}")

        document = result.document
        ocr_text = document.text if document and document.text else ""

        return {"text": ocr_text}

    def _guess_mime(self, file_path: str) -> str:
        """
        For now, assume PDFs. This avoids 'Unsupported mime type' when
        files are saved without an extension (uploads/<uuid>).
        Later we can improve this by saving the original extension.
        """
        return "application/pdf"
