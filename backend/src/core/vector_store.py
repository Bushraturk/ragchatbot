import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import logging
import uuid

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # Use configuration from settings rather than environment directly
        from src.core.config import settings
        self.settings = settings
        self.client = None
        self._initialized = False
        self.collection_name = "book_content"  # Using the same collection as RAG service

    def _ensure_initialized(self):
        """Lazily initialize the client when first needed"""
        if not self._initialized:
            try:
                if not self.settings.qdrant_url or not self.settings.qdrant_api_key:
                    logger.warning("Qdrant URL or API Key not set, initializing in local mode")
                    # Initialize with local Qdrant storage
                    self.client = QdrantClient(":memory:")  # Use in-memory storage for fallback
                else:
                    self.client = QdrantClient(
                        url=self.settings.qdrant_url,
                        api_key=self.settings.qdrant_api_key,
                        https=True  # Use proper HTTPS configuration
                    )

                # Test the client by attempting to get collections
                try:
                    self.client.get_collection(self.collection_name)
                except:
                    # Collection doesn't exist, create it
                    try:
                        self.client.create_collection(
                            collection_name=self.collection_name,
                            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
                        )
                    except:
                        # For in-memory client, this might not be necessary
                        pass

                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant cloud: {e}")
                logger.warning("Falling back to local Qdrant storage")
                # Initialize with local Qdrant storage as fallback
                self.client = QdrantClient(":memory:")  # Use in-memory storage for fallback
                self._initialized = True

    def _create_collection_if_not_exists(self):
        """Create the collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} already exists")
        except:
            try:
                # Collection doesn't exist, create it
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
                )
                logger.info(f"Created new collection: {self.collection_name}")
            except Exception as e:
                # This might happen with in-memory client, which auto-creates collections
                logger.info(f"Collection {self.collection_name} setup complete (in-memory or pre-existing)")

    def _generate_uuid(self, doc_id: str) -> str:
        """Generate a valid UUID from a document ID string"""
        # Use uuid5 with a namespace to generate consistent UUIDs from string IDs
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))

    def add_document(self, doc_id: str, content: str, embedding: List[float], metadata: dict = None):
        """Add a document to the vector store"""
        if metadata is None:
            metadata = {}

        self._ensure_initialized()

        # Convert doc_id to valid UUID format for Qdrant
        point_id = self._generate_uuid(doc_id)

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "content": content,
                            "metadata": metadata,
                            "original_doc_id": doc_id
                        }
                    )
                ]
            )
            logger.info(f"Successfully added document {doc_id} to vector store")
        except Exception as e:
            logger.error(f"Error adding document {doc_id} to vector store: {e}")
            # Don't raise the exception to allow graceful degradation

    def add_web_content(self, doc_id: str, title: str, content: str, embedding: List[float],
                        url: str, scraped_at: str = None, metadata: dict = None):
        """Add web content to the vector store with additional web-specific metadata"""
        if metadata is None:
            metadata = {}

        self._ensure_initialized()

        # Convert doc_id to valid UUID format for Qdrant
        point_id = self._generate_uuid(doc_id)

        # Add web-specific metadata
        web_metadata = {
            **metadata,
            "url": url,
            "title": title,
            "source_type": "web_content",
            "original_doc_id": doc_id
        }

        if scraped_at:
            web_metadata["scraped_at"] = scraped_at

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "content": content,
                            "metadata": web_metadata
                        }
                    )
                ]
            )
            logger.info(f"Successfully added web content {doc_id} from {url} to vector store")
        except Exception as e:
            logger.error(f"Error adding web content {doc_id} from {url} to vector store: {e}")
            # Don't raise the exception to allow graceful degradation

    def search(self, query_embedding: List[float], limit: int = 10) -> List[dict]:
        """Search for similar documents to the query"""
        self._ensure_initialized()
        try:
            # Use query_points (newer Qdrant client API)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit
            )

            return [
                {
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "metadata": point.payload.get("metadata", {}),
                    "similarity_score": point.score
                }
                for point in results.points
            ]
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            # Return empty results instead of raising an exception
            return []

    def delete_document(self, doc_id: str):
        """Delete a document from the vector store"""
        self._ensure_initialized()
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[doc_id])
            )
            logger.info(f"Successfully deleted document {doc_id} from vector store")
        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from vector store: {e}")
            # Don't raise the exception to allow graceful degradation

    def delete_all_web_content(self):
        """Delete all web content from the vector store"""
        self._ensure_initialized()
        try:
            # Get all points in collection
            all_points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust based on expected number of documents
            )

            if all_points:
                point_ids = [point.id for point in all_points]
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=point_ids)
                )
                logger.info(f"Successfully deleted all {len(point_ids)} web content documents from vector store")
            else:
                logger.info("No web content documents to delete")
        except Exception as e:
            logger.error(f"Error deleting all web content from vector store: {e}")
            # Don't raise the exception to allow graceful degradation


# Global instance (not initialized until first use)
vector_store = VectorStore()