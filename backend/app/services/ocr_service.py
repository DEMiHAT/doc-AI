import os
from dotenv import load_dotenv
from google.cloud import documentai_v1 as documentai

load_dotenv()

class OCRService:
    def __init__(self):
        # Load environment variables
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION")
        self.processor_id = os.getenv("GCP_PROCESSOR_ID")

        print(f"[OCR DEBUG] PROJECT = {self.project_id}")
        print(f"[OCR DEBUG] LOCATION = {self.location}")
        print(f"[OCR DEBUG] PROCESSOR = {self.processor_id}")

        if not self.project_id or not self.processor_id:
            raise RuntimeError("Missing GCP_PROJECT_ID or GCP_PROCESSOR_ID")

        self.client = documentai.DocumentProcessorServiceClient()

        self.processor_path = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

    # ✨ NEW — The function your router expects
    def extract_text(self, file_bytes: bytes) -> str:
        """
        Sends a document to Google Document AI and returns extracted text.
        """

        try:
            raw_document = documentai.RawDocument(
                content=file_bytes,
                mime_type="application/pdf"
            )

            request = documentai.ProcessRequest(
                name=self.processor_path,
                raw_document=raw_document
            )

            result = self.client.process_document(request=request)
            document = result.document

            text = document.text if document.text else ""

            print("[OCR DEBUG] Extracted text:")
            print(text[:500])

            return text

        except Exception as e:
            raise RuntimeError(f"Document AI OCR failed: {e}")

# Export singleton
ocr_service = OCRService()
