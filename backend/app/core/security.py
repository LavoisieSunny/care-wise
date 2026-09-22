from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-CareWise-Key", auto_error=False)


async def verify_demo_key(api_key: str = Security(api_key_header)) -> bool:
    """Validate shared demo API key header.

    If REQUIRE_AUTH is enabled, any missing or mismatched key is rejected with 401.
    If REQUIRE_AUTH is disabled (default development/hackathon mode), requests
    without a key are allowed with a warning, but invalid keys are rejected.
    """
    if not settings.REQUIRE_AUTH and not api_key:
        return True

    if api_key == settings.DEMO_API_KEY:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Invalid or missing X-CareWise-Key header for CareWise API.",
        headers={"WWW-Authenticate": "ApiKey"},
    )
