import os

class FileService:
    UPLOAD_DIR = "uploads"

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def save_file(self, file_bytes, filename):
        """Save uploaded file to disk."""
        path = os.path.join(self.UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path

    def get_file_path(self, file_id: str):
        """Find actual file path based on file_id."""
        for fname in os.listdir(self.UPLOAD_DIR):
            if file_id in fname:
                return os.path.join(self.UPLOAD_DIR, fname)
        raise FileNotFoundError("File not found")

    def read_text(self, file_path: str):
        """Return raw text content of file (for classifier only)."""
        try:
            with open(file_path, "rb") as f:
                return f.read().decode(errors="ignore")
        except Exception:
            return ""
