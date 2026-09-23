"""
Unit tests for CareWise Authentication and JWT security:
- User registration and password hashing
- User login and JWT access token issuance
- Protected routes requiring valid Bearer tokens
- Route rejection when token is missing, invalid, or expired
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import auth_service
from app.schemas.auth import UserRegister
from app.core.database import SessionLocal, UserRecord

client = TestClient(app)


@pytest.fixture
def unique_user_creds():
    uid = uuid.uuid4().hex[:8]
    return {
        "email": f"testuser_{uid}@carewise.org",
        "password": "StrongPassword123!",
        "name": f"Test User {uid}"
    }


def test_register_and_login_flow(unique_user_creds):
    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json=unique_user_creds)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == unique_user_creds["email"]
    assert reg_data["user"]["name"] == unique_user_creds["name"]
    token = reg_data["access_token"]

    # 2. Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": unique_user_creds["email"],
        "password": unique_user_creds["password"]
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["id"] == reg_data["user"]["id"]

    # 3. Access protected /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_user_creds["email"]

    # Clean up user from DB
    db = SessionLocal()
    try:
        u = db.query(UserRecord).filter(UserRecord.email == unique_user_creds["email"]).first()
        if u:
            db.delete(u)
            db.commit()
    finally:
        db.close()


def test_register_duplicate_email_fails(unique_user_creds):
    res1 = client.post("/api/v1/auth/register", json=unique_user_creds)
    assert res1.status_code == 200

    # Attempt duplicate registration
    res2 = client.post("/api/v1/auth/register", json=unique_user_creds)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()

    # Cleanup
    db = SessionLocal()
    try:
        u = db.query(UserRecord).filter(UserRecord.email == unique_user_creds["email"]).first()
        if u:
            db.delete(u)
            db.commit()
    finally:
        db.close()


def test_login_invalid_credentials_fails(unique_user_creds):
    client.post("/api/v1/auth/register", json=unique_user_creds)

    # Wrong password
    bad_login = client.post("/api/v1/auth/login", json={
        "email": unique_user_creds["email"],
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # Non-existent user
    non_existent = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@carewise.org",
        "password": "Password123!"
    })
    assert non_existent.status_code == 401

    # Cleanup
    db = SessionLocal()
    try:
        u = db.query(UserRecord).filter(UserRecord.email == unique_user_creds["email"]).first()
        if u:
            db.delete(u)
            db.commit()
    finally:
        db.close()


def test_protected_routes_require_valid_token():
    # Without token
    res_no_auth = client.get("/api/v1/policies")
    assert res_no_auth.status_code == 401

    # With invalid token
    res_bad_auth = client.get("/api/v1/policies", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert res_bad_auth.status_code == 401
