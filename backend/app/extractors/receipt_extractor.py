# app/extractors/receipt_extractor.py

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None


class ReceiptExtractionResult(BaseModel):
    document_type: str = Field(default="receipt")
    merchant_name: Optional[str] = None
    merchant_address: Optional[str] = None
    receipt_date: Optional[str] = None
    receipt_time: Optional[str] = None
    payment_method: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    items: List[ReceiptItem] = []
    raw_text: str = ""


class ReceiptExtractor:
    """
    Rule-based receipt extractor.
    """

    def __init__(self):
        self.money_pattern = re.compile(r"(\d{1,3}(?:[,\d]{3})*(?:\.\d+)?)")

    def _find_first(self, patterns, text: str) -> Optional[str]:
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def extract(self, text: str) -> ReceiptExtractionResult:
        if not text:
            return ReceiptExtractionResult(raw_text="")

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        merchant_name = lines[0] if lines else None

        # Date & time
        receipt_date = self._find_first(
            [
                r"Date[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
                r"([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
            ],
            text,
        )

        receipt_time = self._find_first(
            [
                r"Time[:\s]*([0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?\s*(?:AM|PM)?)",
                r"([0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?\s*(?:AM|PM)?)",
            ],
            text,
        )

        # Payment method
        payment_method = self._find_first(
            [
                r"Payment\s*Method[:\s]*([A-Za-z ]+)",
                r"(CASH|CARD|UPI|DEBIT|CREDIT)",
            ],
            text,
        )

        # Total amount
        total_amount = None
        total_match = re.search(
            r"Total\s*(?:Amount)?[:\s]*([A-Z]{3})?\s?(\d{1,3}(?:[,\d]{3})*(?:\.\d+)?)",
            text,
            re.IGNORECASE,
        )
        currency = None
        if total_match:
            currency = total_match.group(1)
            try:
                total_amount = float(total_match.group(2).replace(",", ""))
            except ValueError:
                total_amount = None

        if not currency:
            c_match = re.search(r"\b(INR|USD|EUR|GBP|JPY|AUD|CAD)\b", text)
            currency = c_match.group(1) if c_match else None

        # TODO: parse items – for now we leave as empty.
        items: List[ReceiptItem] = []

        return ReceiptExtractionResult(
            merchant_name=merchant_name,
            receipt_date=receipt_date,
            receipt_time=receipt_time,
            payment_method=payment_method,
            total_amount=total_amount,
            currency=currency,
            items=items,
            raw_text=text,
        )


receipt_extractor = ReceiptExtractor()
