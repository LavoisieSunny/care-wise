"""
Lightweight PII redaction for text sent to external LLM APIs.

This is a deterministic, regex-based stand-in for a real de-identification
pipeline (e.g. Microsoft Presidio with NER models). It is NOT clinically
rigorous and should not be presented as HIPAA/DPDP-grade de-identification
on its own -- it exists to (a) catch the most common accidental leaks in a
chat box (phone numbers, emails, Aadhaar-style 12-digit IDs, PAN numbers)
and (b) demonstrate the *pattern* of structure-preserving substitution:
replacing a detected value with a same-shaped placeholder rather than a
single generic token, so the sentence stays grammatically legible to the
LLM instead of collapsing into "[REDACTED] said [REDACTED]".
"""
import re
from typing import Tuple, Dict

_PATTERNS: Dict[str, re.Pattern] = {
    "PHONE": re.compile(r"\b(\+?91[-\s]?)?[6-9]\d{9}\b"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "AADHAAR": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
}

_PLACEHOLDERS = {
    "PHONE": "98XXXXXX10",
    "EMAIL": "patient@example.com",
    "AADHAAR": "XXXX XXXX 1234",
    "PAN": "ABCXX1234X",
}


def redact(text: str) -> Tuple[str, int]:
    """Return (redacted_text, number_of_replacements)."""
    redacted = text
    count = 0
    for label, pattern in _PATTERNS.items():
        redacted, n = pattern.subn(_PLACEHOLDERS[label], redacted)
        count += n
    return redacted, count
