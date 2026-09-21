import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import jwt
from app.main import app

client = TestClient(app)

def create_mock_jwt(email: str = "developer@example.com", sub: str = "1234567890") -> str:
    """Generates an unverified dummy JWT for testing header decoding."""
    payload = {"email": email, "sub": sub, "iss": "https://accounts.google.com"}
    return jwt.encode(payload, "a_very_secret_32_byte_key_test!!", algorithm="HS256")

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_unauthenticated_request_rejected():
    response = client.post("/v1/generate", json={"prompt": "Hello"})
    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]

def test_invalid_auth_header_format():
    response = client.post(
        "/v1/generate",
        json={"prompt": "Hello"},
        headers={"Authorization": "Basic invalid123"},
    )
    assert response.status_code == 401
    assert "Invalid Authorization header format" in response.json()["detail"]

@patch("app.main.gemini_client.generate_content")
@patch("app.main.db.record_usage")
def test_successful_generate_with_iam_token(mock_record_usage, mock_generate_content):
    mock_generate_content.return_value = {
        "text": "Gemini response text",
        "usage": {
            "prompt_tokens": 12,
            "candidates_tokens": 25,
            "total_tokens": 37,
        },
        "model": "gemini-3.8-flash",
    }

    mock_token = create_mock_jwt(email="engineer@example.com")

    response = client.post(
        "/v1/generate",
        json={"prompt": "What is Cloud Run?", "thinking_level": "MEDIUM"},
        headers={"Authorization": f"Bearer {mock_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Gemini response text"
    assert data["user_id"] == "engineer@example.com"
    assert data["model"] == "gemini-3.8-flash"
    assert data["usage"]["prompt_tokens"] == 12
    assert data["usage"]["candidates_tokens"] == 25
    assert data["usage"]["total_tokens"] == 37

    # Verify usage was persisted to DB
    mock_record_usage.assert_called_once_with(
        user_id="engineer@example.com",
        input_tokens=12,
        output_tokens=25,
        model="gemini-3.8-flash",
    )

@patch("app.main.gemini_client.generate_content")
@patch("app.main.db.record_usage")
def test_iap_authenticated_user_email_header(mock_record_usage, mock_generate_content):
    mock_generate_content.return_value = {
        "text": "Response via IAP",
        "usage": {"prompt_tokens": 5, "candidates_tokens": 10, "total_tokens": 15},
        "model": "gemini-3.8-flash",
    }

    response = client.post(
        "/v1/generate",
        json={"prompt": "Test prompt"},
        headers={"X-Goog-Authenticated-User-Email": "accounts.google.com:alice@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == "alice@example.com"
    mock_record_usage.assert_called_once_with(
        user_id="alice@example.com",
        input_tokens=5,
        output_tokens=10,
        model="gemini-3.8-flash",
    )

def test_empty_prompt_validation():
    mock_token = create_mock_jwt()
    response = client.post(
        "/v1/generate",
        json={"prompt": ""},
        headers={"Authorization": f"Bearer {mock_token}"},
    )
    assert response.status_code == 422
