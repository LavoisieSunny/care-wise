"""
Unit tests for structure-preserving PII Redaction:
- Phone numbers (+91-9876543210)
- Emails (patient@hospital.org)
- Aadhaar numbers (12-digit)
- PAN cards (5-letter, 4-digit, 1-letter)
"""
from app.core.redaction import redact


def test_redact_phone_and_email():
    raw = "Please contact Ramesh at +919876543210 or email ramesh.care@example.com about pre-auth."
    safe, count = redact(raw)
    assert count == 2
    assert "+919876543210" not in safe
    assert "ramesh.care@example.com" not in safe
    assert "98XXXXXX10" in safe
    assert "patient@example.com" in safe


def test_redact_aadhaar_and_pan():
    raw = "Patient Aadhaar is 1234 5678 9012 and PAN card is ABCDE1234F."
    safe, count = redact(raw)
    assert count == 2
    assert "1234 5678 9012" not in safe
    assert "ABCDE1234F" not in safe
    assert "XXXX XXXX 1234" in safe
    assert "ABCXX1234X" in safe


def test_redact_clean_query():
    raw = "What is the room rent limit for twin sharing rooms?"
    safe, count = redact(raw)
    assert count == 0
    assert safe == raw
