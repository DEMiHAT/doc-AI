import os
import json
from google import genai
from google.genai.types import GenerateContentConfig

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY environment variable")

        self.client = genai.Client(api_key=api_key)

        # ✅ USE ONLY VALID MODELS FROM YOUR LIST
        self.model = "models/gemini-2.5-flash"
        self.embed_model = "models/text-embedding-004"

    def classify_document(self, text: str) -> dict:
        prompt = f"""
        Classify this document into:
        - invoice
        - receipt
        - purchase_order
        - resume
        - report
        - unknown

        Respond ONLY in JSON including:
        {{
            "document_type": "...",
            "confidence": 0.xx
        }}

        TEXT:
        {text}
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt],
            config=GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        try:
            return json.loads(response.text)
        except:
            return {"document_type": "unknown", "confidence": 0.0}

    def summarize(self, text: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=[f"Summarize:\n{text}"]
        )
        return response.text

    def generate_embeddings(self, text: str):
        resp = self.client.models.embed_content(
            model=self.embed_model,
            contents=[text]
        )
        return resp.embeddings[0].values

    def extract_structured(self, text: str, doc_type: str):
            prompt = f"""
    Extract structured fields from this {doc_type} document.
    Return ONLY valid JSON. No explanations.

    Document:
    {text}
    """

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            try:
                return json.loads(response.text)
            except Exception:
                return {"raw_text": text}


gemini = GeminiClient()