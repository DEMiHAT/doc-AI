# app/extractors/po_extractor.py

import re
from typing import List, Optional
from pydantic import BaseModel

from app.utils.text_utils import basic_clean_text


# --------------------------------------------
# Pydantic Models
# --------------------------------------------

class POLineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    total_price: Optional[str] = None


class POExtractionResult(BaseModel):
    vendor: Optional[str] = None
    po_number: Optional[str] = None
    date: Optional[str] = None
    line_items: List[POLineItem] = []
    raw_text: Optional[str] = None


# --------------------------------------------
# Extractor Class
# --------------------------------------------

class POExtractor:

    def extract(self, text: str) -> POExtractionResult:
        """
        Extracts purchase order fields from OCR text.
        """

        cleaned = basic_clean_text(text)

        # ------------------------------------------------------
        # 1. VENDOR NAME (simple heuristic)
        # Typically first uppercase line
        # ------------------------------------------------------
        vendor = None
        lines = cleaned.split("\n")

        for line in lines[:5]:
            if len(line.strip()) > 3 and re.search(r"[A-Za-z]", line):
                vendor = line.strip()
                break

        # ------------------------------------------------------
        # 2. PO NUMBER
        # ------------------------------------------------------
        po_number = None
        po_match = re.search(r"(PO|P\.O)\s*[:\-]?\s*(\w+)", cleaned, re.IGNORECASE)
        if po_match:
            po_number = po_match.group(2).strip()

        # ------------------------------------------------------
        # 3. DATE
        # ------------------------------------------------------
        date = None
        date_match = re.search(
            r"(\d{2}[\/\-]\d{2}[\/\-]\d{4})|(\d{4}[\/\-]\d{2}[\/\-]\d{2})",
            cleaned
        )
        if date_match:
            date = date_match.group(0)

        # ------------------------------------------------------
        # 4. LINE ITEMS (Regex block extraction)
        # ------------------------------------------------------
        line_items: List[POLineItem] = []

        # Basic heuristic: look for numerical patterns
        line_regex = re.compile(
            r"(?P<desc>[A-Za-z0-9 ,.\-/]+)\s+"
            r"(?P<qty>\d+(?:\.\d+)?)\s+"
            r"(?P<unit>\d+(?:\.\d+)?)\s+"
            r"(?P<total>\d+(?:\.\d+)?)"
        )

        for match in line_regex.finditer(cleaned):
            line_items.append(
                POLineItem(
                    description=match.group("desc").strip(),
                    quantity=match.group("qty"),
                    unit_price=match.group("unit"),
                    total_price=match.group("total"),
                )
            )

        return POExtractionResult(
            vendor=vendor,
            po_number=po_number,
            date=date,
            line_items=line_items,
            raw_text=cleaned,
        )


# Exported instance to match other extractors
po_extractor = POExtractor()
