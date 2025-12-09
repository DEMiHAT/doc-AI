# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.api.upload_router import router as upload_router
from app.api.detect_router import router as detect_router
from app.api.ocr_router import router as ocr_router
from app.api.extract_router import router as extract_router
from app.api.health_router import router as health_router


app = FastAPI(
    title="DocAI — Universal AI Document Ingestion System",
    description="Unified OCR + Classification + Extraction + NLP pipeline",
    version="1.0.0",
)

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set your domain here for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- ROUTES --------------------
app.include_router(upload_router)
app.include_router(detect_router)
app.include_router(ocr_router)
app.include_router(extract_router)  # NEW
app.include_router(health_router)


# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {"status": "DocAI backend running", "version": "1.0.0"}
