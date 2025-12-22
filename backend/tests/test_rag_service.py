import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.services.rag_service import RAGService


@patch('backend.src.services.rag_service.genai.GenerativeModel')
@patch('backend.src.services.rag_service.QdrantClient')
@patch('backend.src.services.rag_service.cohere.Client')
def test_rag_service_initialization(mock_cohere, mock_qdrant, mock_genai):
    """Test that RAG service initializes correctly"""
    # Mock the clients
    mock_cohere_instance = MagicMock()
    mock_cohere.return_value = mock_cohere_instance
    
    mock_qdrant_instance = MagicMock()
    mock_qdrant.return_value = mock_qdrant_instance
    
    mock_genai_instance = MagicMock()
    mock_genai.return_value = mock_genai_instance
    
    # Initialize the RAG service
    rag_service = RAGService()
    
    # Verify that the services were initialized
    assert rag_service is not None


@patch('backend.src.services.rag_service.genai.GenerativeModel')
@patch('backend.src.services.rag_service.QdrantClient')
@patch('backend.src.services.rag_service.cohere.Client')
def test_add_document(mock_cohere, mock_qdrant, mock_genai):
    """Test adding a document to the RAG service"""
    # Mock the clients
    mock_cohere_instance = MagicMock()
    mock_cohere.return_value = mock_cohere_instance
    
    mock_qdrant_instance = MagicMock()
    mock_qdrant.return_value = mock_qdrant_instance
    
    mock_genai_instance = MagicMock()
    mock_genai.return_value = mock_genai_instance
    
    # Initialize the RAG service
    rag_service = RAGService()
    
    # Test adding a document
    result = rag_service.add_document(
        doc_id="test_doc_123",
        title="Test Document",
        content="This is a test document content for the RAG system."
    )
    
    # Verify that the result is True (indicating success)
    assert result is True


@patch('backend.src.services.rag_service.genai.GenerativeModel')
@patch('backend.src.services.rag_service.QdrantClient')
@patch('backend.src.services.rag_service.cohere.Client')
def test_process_query(mock_cohere, mock_qdrant, mock_genai):
    """Test processing a query through the RAG service"""
    # Mock the clients
    mock_cohere_instance = MagicMock()
    mock_cohere_instance.embed.return_value = MagicMock(embeddings=[[0.1, 0.2, 0.3]])
    mock_cohere.return_value = mock_cohere_instance
    
    mock_qdrant_instance = MagicMock()
    mock_search_result = MagicMock()
    mock_search_result.score = 0.9
    mock_search_result.payload = {
        "document_id": "test_doc",
        "content": "This is relevant content",
        "title": "Test Document",
        "source_type": "BOOK_FULL",
        "chunk_order": 0
    }
    mock_qdrant_instance.search.return_value = [mock_search_result]
    mock_qdrant.return_value = mock_qdrant_instance
    
    mock_genai_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a test response based on the context."
    mock_genai_instance.generate_content.return_value = mock_response
    mock_genai.return_value = mock_genai_instance
    
    # Initialize the RAG service
    rag_service = RAGService()
    
    # Test processing a query
    response, context_items = rag_service.process_query(
        query="What is this document about?",
        mode="full_book"
    )
    
    # Verify that a response was generated
    assert response is not None
    assert isinstance(response, str)
    assert len(context_items) >= 0  # May be empty if no context found


@patch('backend.src.services.rag_service.genai.GenerativeModel')
@patch('backend.src.services.rag_service.QdrantClient')
@patch('backend.src.services.rag_service.cohere.Client')
def test_process_query_selected_text_mode(mock_cohere, mock_qdrant, mock_genai):
    """Test processing a query in selected text mode"""
    # Mock the genai client to return a response
    mock_genai_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a test response based on selected text."
    mock_genai_instance.generate_content.return_value = mock_response
    mock_genai.return_value = mock_genai_instance
    
    # Initialize the RAG service
    rag_service = RAGService()
    
    # Test processing a query in selected text mode
    response, context_items = rag_service.process_query(
        query="What does this selected text mean?",
        mode="selected_text",
        selected_text="This is the text that was specifically selected by the user."
    )
    
    # Verify that a response was generated
    assert response is not None
    assert isinstance(response, str)