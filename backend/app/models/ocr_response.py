# app/models/ocr_response.py

from pydantic import BaseModel

class OCRResponse(BaseModel):
    file_id: str
    text: str
