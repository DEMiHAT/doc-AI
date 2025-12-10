import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable")

client = genai.Client(api_key=API_KEY)

print("\n=== AVAILABLE GEMINI MODELS ===\n")

for model in client.models.list():
    print(model.name)
