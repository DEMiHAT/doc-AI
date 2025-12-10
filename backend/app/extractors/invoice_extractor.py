# app/extractors/invoice_extractor.py

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None


class InvoiceExtractionResult(BaseModel):
    document_type: str = Field(default="invoice")
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    subtotal_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    line_items: List[InvoiceItem] = []
    raw_text: str = ""


class InvoiceExtractor:
    """
    Rule-based invoice extractor.

    NOTE:
    - Uses simple regex + heuristics.
    - Safe to later augment with Gemini / LLM for better accuracy.
    """

    def __init__(self):
        # Basic money pattern
        self.money_pattern = re.compile(r"([A-Z]{3})?\s?(\d{1,3}(?:[,\d]{3})*(?:\.\d+)?)")

    def _find_first(self, patterns, text: str) -> Optional[str]:
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _find_amount(self, label_patterns, text: str) -> Optional[float]:
        for lbl in label_patterns:
            # capture label then number
            regex = rf"{lbl}[:\s]*([A-Z]{{3}})?\s?(\d{{1,3}}(?:[,\d]{{3}})*(?:\.\d+)?)"
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                num_str = match.group(2).replace(",", "")
                try:
                    return float(num_str)
                except ValueError:
                    continue
        return None

    def extract(self, text: str) -> InvoiceExtractionResult:
        if not text:
            return InvoiceExtractionResult(raw_text="")

        # Invoice number
        invoice_number = self._find_first(
            [
                r"Invoice\s*No\.?\s*[:#]\s*(\S+)",
                r"Invoice\s*Number\s*[:#]\s*(\S+)",
                r"INV\s*[:#]\s*(\S+)",
            ],
            text,
        )

        # Invoice date
        invoice_date = self._find_first(
            [
                r"Invoice\s*Date\s*[:]\s*([^\n]+)",
                r"Date\s*[:]\s*([^\n]+)",
            ],
            text,
        )

        # Due date
        due_date = self._find_first(
            [
                r"Due\s*Date\s*[:]\s*([^\n]+)",
                r"Payment\s*Due\s*[:]\s*([^\n]+)",
            ],
            text,
        )

        # Very naive vendor/customer heuristics
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        vendor_name = None
        customer_name = None

        for i, ln in enumerate(lines[:10]):  # top section for vendor
            if "invoice" in ln.lower():
                continue
            if len(ln.split()) >= 2:
                vendor_name = ln
                break

        # Look for "Bill To" or "Ship To" for customer
        for i, ln in enumerate(lines):
            if re.search(r"Bill To|Billed To", ln, re.IGNORECASE):
                if i + 1 < len(lines):
                    customer_name = lines[i + 1]
                break

        # Subtotal, tax, total
        subtotal_amount = self._find_amount([r"Sub\s*Total", r"Subtotal"], text)
        tax_amount = self._find_amount([r"Tax", r"GST", r"VAT"], text)
        total_amount = self._find_amount([r"Total\s*Amount", r"Total\s*Due", r"Amount\s*Due"], text)

        # Currency guess (look for INR, USD, EUR etc.)
        currency_match = re.search(r"\b(INR|USD|EUR|GBP|JPY|AUD|CAD)\b", text)
        currency = currency_match.group(1) if currency_match else None

        # TODO: parse line items (table parsing from DocAI structure)
        line_items: List[InvoiceItem] = []

        return InvoiceExtractionResult(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            vendor_name=vendor_name,
            customer_name=customer_name,
            subtotal_amount=subtotal_amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            currency=currency,
            line_items=line_items,
            raw_text=text,
        )


invoice_extractor = InvoiceExtractor()
