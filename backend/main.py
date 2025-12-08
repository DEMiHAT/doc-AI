from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload_router import router as upload_router
from app.api.ocr_router import router as ocr_router
from app.api.detect_router import router as detect_router

app = FastAPI(title="DocAI Backend", version="1.0.0")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "DocAI Backend Running"}

# Routers MUST come after app is defined
app.include_router(upload_router, prefix="/api")
app.include_router(ocr_router, prefix="/api")
app.include_router(detect_router, prefix="/api")
