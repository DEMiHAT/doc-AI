# app/utils/text_utils.py

import re

def basic_clean_text(text: str) -> str:
    """
    Basic cleaning pipeline used by the NLP service.
    - Remove extra whitespace
    - Normalize newlines
    - Strip non-printable OCR characters
    """

    if not text:
        return ""

    # Remove form feed characters
    text = text.replace("\x0c", " ")

    # Normalize line endings
    text = text.replace("\r", "\n")

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove multiple blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    # Strip leading and trailing whitespace
    return text.strip()
