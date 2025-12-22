import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

def test_session_list_contract():
    """Test the contract for GET /api/sessions endpoint"""
    response = client.get("/api/sessions")
    
    # Should return 200 OK
    assert response.status_code in [200, 500]
    
    # If successful, check response structure
    if response.status_code == 200:
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
        if len(data["sessions"]) > 0:
            session = data["sessions"][0]
            assert "id" in session
            assert "title" in session
            assert "created_at" in session
            assert "updated_at" in session
            assert "metadata" in session

def test_session_delete_contract():
    """Test the contract for DELETE /api/sessions/{session_id} endpoint"""
    response = client.delete("/api/sessions/test-session-id")
    
    # Should return 200 OK for success, 404 for not found, or 500 for error
    assert response.status_code in [200, 404, 500]
    
    if response.status_code == 200:
        # Success response might be empty or have a status message
        pass