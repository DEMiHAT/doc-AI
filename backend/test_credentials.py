from google.cloud import documentai_v1 as documentai
import os

print("Using credentials:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
print("Project:", os.getenv("GCP_PROJECT_ID"))

try:
    client = documentai.DocumentProcessorServiceClient()
    print("Client initialized successfully!")
except Exception as e:
    print("ERROR:", e)
