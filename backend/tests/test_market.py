import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.services.market_insight_service import market_insight_service
from app.core.database import SessionLocal, UserRecord

client = TestClient(app)

def test_market_insight_endpoint_and_cache():
    # Register a unique user to get a real token
    uid = uuid.uuid4().hex[:8]
    creds = {
        "email": f"market_test_{uid}@carewise.org",
        "password": "Password123!",
        "name": f"Market Tester {uid}"
    }
    reg_res = client.post("/api/v1/auth/register", json=creds)
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    mock_result = {
        "answer": "Most Indian health insurance plans for senior citizens offer ₹5L - ₹10L coverage with 10-20% mandatory co-payment.",
        "sources": [
            {"title": "IRDAI Health Insurance Guidelines", "url": "https://irdai.gov.in/health"}
        ]
    }

    try:
        # Test live/mock call through market_insight_service
        with patch.object(market_insight_service.llm, "call_claude_with_web_search", return_value=mock_result) as mock_claude:
            res = client.get("/api/v1/market/insight?query=senior%20citizen%20health%20plans", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert "answer" in data
            assert len(data["sources"]) == 1
            assert mock_claude.called

            # Second call with same query should hit cache without calling LLM again
            mock_claude.reset_mock()
            res_cached = client.get("/api/v1/market/insight?query=senior%20citizen%20health%20plans", headers=headers)
            assert res_cached.status_code == 200
            assert not mock_claude.called

        # Test unavailable (returns None)
        with patch.object(market_insight_service.llm, "call_claude_with_web_search", return_value=None):
            res_unavail = client.get("/api/v1/market/insight?query=unknown%20rare%20policy%20query%2099999", headers=headers)
            assert res_unavail.status_code == 503
            assert res_unavail.json()["detail"] == "Market insight temporarily unavailable."

    finally:
        # Cleanup test user
        db = SessionLocal()
        try:
            u = db.query(UserRecord).filter(UserRecord.email == creds["email"]).first()
            if u:
                db.delete(u)
                db.commit()
        finally:
            db.close()
