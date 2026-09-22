"""
Unit tests for CareWise demo API key security:
- Valid header authentication
- Rejection of invalid API keys
"""
import asyncio
import pytest
from fastapi import HTTPException
from app.core.security import verify_demo_key
from app.core.config import settings


def test_verify_demo_key_valid():
    """Verify that providing the valid demo key succeeds."""
    result = asyncio.run(verify_demo_key(api_key=settings.DEMO_API_KEY))
    assert result is True


def test_verify_demo_key_invalid():
    """Verify that providing a bad key raises 401 Unauthorized."""
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(verify_demo_key(api_key="bad-malicious-token"))
    assert exc_info.value.status_code == 401


def test_verify_demo_key_missing_in_dev():
    """When REQUIRE_AUTH is False, missing key is allowed."""
    settings.REQUIRE_AUTH = False
    result = asyncio.run(verify_demo_key(api_key=None))
    assert result is True
