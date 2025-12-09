# app/models/detect_response.py

from pydantic import BaseModel
from typing import Optional


class DetectResponse(BaseModel):
    file_id: str
    document_type: str
    confidence: float
