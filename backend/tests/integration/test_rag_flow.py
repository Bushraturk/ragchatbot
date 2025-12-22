import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.src.api.main import app
from backend.src.services.rag_service import RAGService

client = TestClient(app)

@patch('backend.src.services.rag_service.RAGService')
def test_full_book_question_answering(mock_rag_service):
    """Test full-book question answering flow"""
    # Mock the RAG service to return a test response
    mock_instance = MagicMock()
    mock_instance.process_request.return_value = (
        "This is a test response based on book content",
        [{"document_id": "doc1", "chunk_id": "chunk1", "content_snippet": "test content", "similarity_score": 0.9}]
    )
    mock_rag_service.return_value = mock_instance

    # Make a request to the chat endpoint
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session-123",
            "message": "What is the main topic of this book?",
            "mode": "full_book"
        }
    )
    
    # Check that the response was successful
    assert response.status_code == 200
    
    data = response.json()
    assert data["response"] == "This is a test response based on book content"
    assert len(data["context_references"]) == 1
    assert data["context_references"][0]["document_id"] == "doc1"
    
    # Verify that the RAG service was called with the correct parameters
    mock_instance.process_request.assert_called_once_with(
        session_id="test-session-123",
        message="What is the main topic of this book?",
        mode="full_book",
        selected_text=None
    )

@patch('backend.src.services.rag_service.RAGService')
def test_new_session_creation(mock_rag_service):
    """Test that a new session is created when no session_id is provided"""
    mock_instance = MagicMock()
    mock_instance.process_request.return_value = (
        "Test response",
        []
    )
    mock_rag_service.return_value = mock_instance

    # Make a request without session_id
    response = client.post(
        "/api/chat",
        json={
            "message": "What is this book about?",
            "mode": "full_book"
        }
    )
    
    # Check that the response was successful and includes a session_id
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] is not None
    assert data["response"] == "Test response"