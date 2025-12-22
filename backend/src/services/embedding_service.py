import cohere
from typing import List, Dict, Any
import sys
import os
# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.co = cohere.Client(settings.cohere_api_key)
        self.model = settings.embedding_model

    def embed_text(self, text: str, input_type: str = "search_query") -> List[float]:
        """
        Generate embeddings for a text using Cohere

        Args:
            text: The text to embed
            input_type: The type of input for embedding (search_query, search_document, etc.)

        Returns:
            A list of floats representing the embedding
        """
        try:
            response = self.co.embed(
                texts=[text],
                model=self.model,
                input_type=input_type
            )
            return response.embeddings[0]  # Return the first (and only) embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 1024  # Assuming 1024-dimensional embeddings

    def embed_documents(self, documents: List[str], input_type: str = "search_document") -> List[List[float]]:
        """
        Generate embeddings for multiple documents

        Args:
            documents: List of documents to embed
            input_type: The type of input for embedding (search_query, search_document, etc.)

        Returns:
            A list of embedding vectors
        """
        try:
            response = self.co.embed(
                texts=documents,
                model=self.model,
                input_type=input_type
            )
            return response.embeddings
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 1024 for _ in range(len(documents))]

    def embed_web_content(self, content: Dict[str, Any]) -> List[float]:
        """
        Generate embeddings for web content with additional context

        Args:
            content: Dictionary containing web content with title, content, and metadata

        Returns:
            A list of floats representing the embedding
        """
        try:
            # Combine title and content for better embedding context
            text_to_embed = f"Title: {content.get('title', '')}\n\nContent: {content.get('content', '')}"

            response = self.co.embed(
                texts=[text_to_embed],
                model=self.model,
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating web content embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 1024  # Assuming 1024-dimensional embeddings