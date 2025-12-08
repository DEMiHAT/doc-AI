from dotenv import load_dotenv
load_dotenv()
import os
from google.cloud import documentai_v1 as documentai

class OCRService:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "us")
        self.processor_id = os.getenv("GCP_PROCESSOR_ID")

        # Client initialization
        self.client = documentai.DocumentProcessorServiceClient()

        # Processor name format
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

    def extract_text(self, file_path: str):
        # Read file bytes
        with open(file_path, "rb") as f:
            content = f.read()

        raw_document = documentai.RawDocument(
            content=content,
            mime_type="application/pdf"  # PDF-only OCR for now
        )

        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=raw_document
        )

        result = self.client.process_document(request=request)

        document = result.document

        return {
            "text": document.text,
            "entities": [e.type_ for e in document.entities],
            "pages": len(document.pages)
        }
