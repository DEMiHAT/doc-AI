# app/extractors/id_extractor.py

import re
from typing import Optional
from pydantic import BaseModel, Field


class IDExtractionResult(BaseModel):
    document_type: str = Field(default="id_card")
    id_type: Optional[str] = None
    full_name: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    address: Optional[str] = None
    raw_text: str = ""


class IDExtractor:
    """
    Rule-based ID card extractor.
    """

    def _find_first(self, patterns, text: str) -> Optional[str]:
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def extract(self, text: str) -> IDExtractionResult:
        if not text:
            return IDExtractionResult(raw_text="")

        # Very generic – you can add country-specific patterns
        id_number = self._find_first(
            [
                r"ID\s*No\.?[:\s]*([A-Z0-9\-]+)",
                r"ID\s*Number[:\s]*([A-Z0-9\-]+)",
                r"Number[:\s]*([A-Z0-9\-]{6,})",
            ],
            text,
        )

        full_name = self._find_first(
            [
                r"Name[:\s]*([^\n]+)",
                r"Full\s*Name[:\s]*([^\n]+)",
            ],
            text,
        )

        date_of_birth = self._find_first(
            [
                r"DOB[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
                r"Date\s*of\s*Birth[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
            ],
            text,
        )

        issue_date = self._find_first(
            [
                r"Issue\s*Date[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
                r"Issued\s*On[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
            ],
            text,
        )

        expiry_date = self._find_first(
            [
                r"Expiry\s*Date[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
                r"Valid\s*Till[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",
            ],
            text,
        )

        address = self._find_first(
            [
                r"Address[:\s]*([^\n]+)",
            ],
            text,
        )

        # Guess ID type
        id_type = None
        if re.search(r"Passport", text, re.IGNORECASE):
            id_type = "passport"
        elif re.search(r"Driving\s*Licence|Driver's\s*License", text, re.IGNORECASE):
            id_type = "driving_license"
        elif re.search(r"Aadhar|Aadhaar", text, re.IGNORECASE):
            id_type = "aadhaar"
        elif re.search(r"PAN\s*Card", text, re.IGNORECASE):
            id_type = "pan_card"

        return IDExtractionResult(
            id_type=id_type,
            full_name=full_name,
            id_number=id_number,
            date_of_birth=date_of_birth,
            issue_date=issue_date,
            expiry_date=expiry_date,
            address=address,
            raw_text=text,
        )


id_extractor = IDExtractor()
