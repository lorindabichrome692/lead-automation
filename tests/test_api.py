"""
Phase 1 API tests — run with: pytest tests/test_api.py -v
Requires the server to be running: uvicorn app.main:app --reload
"""
import httpx
import pytest

BASE_URL = "http://localhost:8000"


def test_health_check():
    """GET /health should return status ok."""
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    print(f"Health check: {data}")


def test_submit_lead_web_form():
    """POST /api/lead should accept a valid lead and return a LeadResponse."""
    payload = {
        "name": "Alice Johnson",
        "email": "alice@techcorp.com",
        "phone": "+15551234567",
        "company": "TechCorp",
        "sector": "Technology",
        "message": "We need a CRM automation solution for our 30-person sales team.",
        "source": "web_form",
    }
    response = httpx.post(f"{BASE_URL}/api/lead", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "received"
    assert "id" in data
    assert "score" in data
    assert data["score"]["label"] in ("hot", "warm", "cold")
    print(f"Lead response: {data}")


def test_submit_lead_minimal():
    """POST /api/lead with only required fields should succeed."""
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "message": "Just curious about your services.",
    }
    response = httpx.post(f"{BASE_URL}/api/lead", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "received"
    print(f"Minimal lead response: {data}")


def test_submit_lead_invalid_email():
    """POST /api/lead with invalid email should return 422."""
    payload = {
        "name": "Charlie",
        "email": "not-an-email",
        "message": "Hello.",
    }
    response = httpx.post(f"{BASE_URL}/api/lead", json=payload)
    assert response.status_code == 422
    print(f"Validation error (expected): {response.status_code}")


def test_whatsapp_webhook():
    """POST /api/whatsapp-webhook with simulated WhatsApp payload should succeed."""
    payload = {
        "from": "+905551234567",
        "name": "John Doe",
        "message": "Hi, I'm interested in your automation services for my retail business.",
        "timestamp": "2024-01-15T10:30:00Z",
    }
    response = httpx.post(f"{BASE_URL}/api/whatsapp-webhook", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "received"
    print(f"WhatsApp webhook response: {data}")


if __name__ == "__main__":
    # Quick manual run: python tests/test_api.py
    print("=== Phase 1 API Tests ===\n")
    test_health_check()
    print("✓ Health check passed\n")
    test_submit_lead_web_form()
    print("✓ Web form lead submission passed\n")
    test_submit_lead_minimal()
    print("✓ Minimal lead submission passed\n")
    test_submit_lead_invalid_email()
    print("✓ Invalid email validation passed\n")
    test_whatsapp_webhook()
    print("✓ WhatsApp webhook passed\n")
    print("=== All tests passed ===")
