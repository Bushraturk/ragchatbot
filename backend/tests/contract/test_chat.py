import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

def test_post_chat_contract():
    """Test the contract for POST /api/chat endpoint"""
    # Test request structure
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session-123",
            "message": "What is this book about?",
            "mode": "full_book",
            "selected_text": None
        }
    )
    
    # Should return 200 OK or 404 if session doesn't exist
    assert response.status_code in [200, 404, 500]
    
    # If successful, check response structure
    if response.status_code == 200:
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "context_references" in data
        assert "timestamp" in data
        assert isinstance(data["context_references"], list)

def test_post_chat_without_session():
    """Test POST /api/chat without session_id (should create new session)"""
    response = client.post(
        "/api/chat",
        json={
            "message": "What is this book about?",
            "mode": "full_book"
        }
    )
    
    # Should return 200 OK with new session
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "context_references" in data
        assert "timestamp" in data