from pydantic import BaseModel

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    mime_type: str
    saved_path: str
