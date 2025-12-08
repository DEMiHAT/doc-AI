import re

class DocumentClassifier:
    def __init__(self):
        pass  # No Gemini initialization for now

    def classify(self, text: str):
        text_lower = text.lower()

        # Invoice rules
        invoice_keywords = ["invoice", "bill to", "qty", "subtotal", "gst", "total amount"]
        if any(k in text_lower for k in invoice_keywords):
            return {"type": "invoice", "confidence": 0.90}

        # Receipt rules
        receipt_keywords = ["subtotal", "store", "cash", "pos", "thank you"]
        if any(k in text_lower for k in receipt_keywords):
            return {"type": "receipt", "confidence": 0.85}

        # Notes rules
        if len(text.split()) > 80 and not re.search(r"\d{1,3}\.\d{2}", text):
            return {"type": "notes", "confidence": 0.70}

        # PO rules
        if "purchase order" in text_lower or "po no" in text_lower:
            return {"type": "purchase_order", "confidence": 0.88}

        # ID card rules
        id_keywords = ["date of birth", "dob", "id no", "blood group"]
        if any(k in text_lower for k in id_keywords):
            return {"type": "id_card", "confidence": 0.80}

        # Default fallback
        return {"type": "unknown", "confidence": 0.40}
