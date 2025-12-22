import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

@patch('backend.src.services.rag_service.RAGService')
def test_selected_text_mode(mock_rag_service):
    """Test selected-text mode functionality"""
    # Mock the RAG service to return a test response
    mock_instance = MagicMock()
    mock_instance.process_request.return_value = (
        "This is a response based on selected text",
        [{"document_id": "selected_text", "chunk_id": "temp_chunk", "content_snippet": "selected content", "similarity_score": 1.0}]
    )
    mock_rag_service.return_value = mock_instance

    # Make a request to the chat endpoint in selected_text mode
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-session-123",
            "message": "What does this selected text mean?",
            "mode": "selected_text",
            "selected_text": "This is the text the user has selected for context."
        }
    )
    
    # Check that the response was successful
    assert response.status_code == 200
    
    data = response.json()
    assert data["response"] == "This is a response based on selected text"
    assert len(data["context_references"]) == 1
    assert data["context_references"][0]["document_id"] == "selected_text"
    
    # Verify that the RAG service was called with the correct parameters for selected_text mode
    mock_instance.process_request.assert_called_once_with(
        session_id="test-session-123",
        message="What does this selected text mean?",
        mode="selected_text",
        selected_text="This is the text the user has selected for context."
    )

@patch('backend.src.services.rag_service.RAGService')
def test_mode_switching(mock_rag_service):
    """Test switching between full-book and selected-text modes"""
    mock_instance = MagicMock()
    mock_instance.process_request.return_value = (
        "Test response",
        []
    )
    mock_rag_service.return_value = mock_instance

    # First request in full-book mode
    response1 = client.post(
        "/api/chat",
        json={
            "session_id": "test-session-123",
            "message": "General question about the book?",
            "mode": "full_book"
        }
    )
    assert response1.status_code == 200
    
    # Second request in selected-text mode using the same session
    response2 = client.post(
        "/api/chat",
        json={
            "session_id": "test-session-123",
            "message": "What does this specific text mean?",
            "mode": "selected_text",
            "selected_text": "Specific text selected by user."
        }
    )
    assert response2.status_code == 200
    
    # Verify RAG service was called twice with different modes
    assert mock_instance.process_request.call_count == 2
    # Check that it was called once with full_book and once with selected_text
    calls = mock_instance.process_request.call_args_list
    modes_used = [call[1]['mode'] for call in calls]
    assert 'full_book' in modes_used
    assert 'selected_text' in modes_used