from pydantic import BaseModel

class DetectRequest(BaseModel):
    file_id: str

class DetectResponse(BaseModel):
    detected_type: str
    confidence: float
    alternatives: list[str]
