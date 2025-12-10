from dotenv import load_dotenv
load_dotenv()   # <-- MUST BE FIRST

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload_router import router as upload_router
from app.api.detect_router import router as detect_router
from app.api.ocr_router import router as ocr_router
from app.api.extract_router import router as extract_router
from app.api.health_router import router as health_router

app = FastAPI(title="DocAI — Universal Document Ingestion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload_router)
app.include_router(detect_router)
app.include_router(ocr_router)
app.include_router(extract_router)
app.include_router(health_router)

@app.get("/")
def root():
    return {"status": "DocAI backend running"}
