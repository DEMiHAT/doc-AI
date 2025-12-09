# app/models/upload_response.py

from pydantic import BaseModel

class UploadResponse(BaseModel):
    file_id: str
    filename: str
