import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.src.api.main import app
import json

client = TestClient(app)

def test_conversation_history():
    """Test that conversations maintain context across multiple exchanges"""
    # Start a conversation with a first question
    first_response = client.post(
        "/api/chat",
        json={
            "message": "What is the main topic of this book?",
            "mode": "full_book"
        }
    )
    
    assert first_response.status_code == 200
    first_data = first_response.json()
    session_id = first_data["session_id"]
    assert session_id is not None
    
    # Ask a follow-up question in the same session
    second_response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "message": "Can you elaborate on that topic?",
            "mode": "full_book"
        }
    )
    
    assert second_response.status_code == 200
    second_data = second_response.json()
    
    # Verify that the session ID is the same
    assert second_data["session_id"] == session_id
    
    # Get the conversation history
    history_response = client.get(f"/api/chat/{session_id}")
    assert history_response.status_code == 200
    history_data = history_response.json()
    
    # Verify the history contains both messages
    assert "messages" in history_data
    assert len(history_data["messages"]) >= 2  # At least the two messages we sent
    
    # Check that both user messages and assistant responses are in history
    user_messages = [msg for msg in history_data["messages"] if msg["sender_type"] == "USER"]
    assistant_messages = [msg for msg in history_data["messages"] if msg["sender_type"] == "ASSISTANT"]
    
    assert len(user_messages) >= 1
    assert len(assistant_messages) >= 1

def test_multiple_sessions():
    """Test that different sessions maintain separate histories"""
    # Create first session
    first_session_response = client.post(
        "/api/chat",
        json={
            "message": "What is this book about?",
            "mode": "full_book"
        }
    )
    assert first_session_response.status_code == 200
    first_session_data = first_session_response.json()
    first_session_id = first_session_data["session_id"]
    
    # Create second session
    second_session_response = client.post(
        "/api/chat",
        json={
            "message": "What are the main points?",
            "mode": "full_book"
        }
    )
    assert second_session_response.status_code == 200
    second_session_data = second_session_response.json()
    second_session_id = second_session_data["session_id"]
    
    # Verify sessions are different
    assert first_session_id != second_session_id
    
    # Add more messages to each session
    client.post(
        "/api/chat",
        json={
            "session_id": first_session_id,
            "message": "Can you summarize chapter 1?",
            "mode": "full_book"
        }
    )
    
    client.post(
        "/api/chat",
        json={
            "session_id": second_session_id,
            "message": "What does the author say about technology?",
            "mode": "full_book"
        }
    )
    
    # Get history for each session
    first_history_response = client.get(f"/api/chat/{first_session_id}")
    second_history_response = client.get(f"/api/chat/{second_session_id}")
    
    assert first_history_response.status_code == 200
    assert second_history_response.status_code == 200
    
    first_history = first_history_response.json()["messages"]
    second_history = second_history_response.json()["messages"]
    
    # Verify that the histories are independent
    first_user_messages = [msg["content"] for msg in first_history if msg["sender_type"] == "USER"]
    second_user_messages = [msg["content"] for msg in second_history if msg["sender_type"] == "USER"]
    
    assert "What is this book about?" in first_user_messages
    assert "What is this book about?" not in second_user_messages
    
    assert "What are the main points?" in second_user_messages
    assert "What are the main points?" not in first_user_messages