import uuid
from typing import Tuple, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import sys
import os
# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import SessionLocal
from src.models.database_models import Document as DocumentModel, DocumentChunk as DocumentChunkModel
from src.services.embedding_service import EmbeddingService
from src.core.vector_store import vector_store


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.db = SessionLocal()
        self.embedding_service = EmbeddingService()

    def __del__(self):
        self.db.close()

    def create_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        source_type: str = "BOOK_FULL"
    ) -> Tuple[str, str]:
        """
        Create a new document and process it for RAG

        Args:
            doc_id: The ID for the document
            title: Title of the document
            content: Content of the document
            source_type: Type of source ('BOOK_FULL' or 'BOOK_SELECTION')

        Returns:
            A tuple of (status, message)
        """
        try:
            # Create document record in database
            db_document = DocumentModel(
                id=doc_id,
                title=title,
                content=content,
                source_type=source_type,
                metadata_={}
            )
            self.db.add(db_document)
            self.db.commit()

            # Chunk the document content
            chunks = self._chunk_document(content, doc_id)

            # Generate embeddings for chunks and store in vector database
            chunk_texts = [chunk['content'] for chunk in chunks]
            embeddings = self.embedding_service.embed_documents(chunk_texts)

            for i, chunk in enumerate(chunks):
                # Save chunk to database
                db_chunk = DocumentChunkModel(
                    id=chunk['id'],
                    document_id=doc_id,
                    content=chunk['content'],
                    chunk_order=chunk['order'],
                    metadata_={'source_type': source_type}
                )
                self.db.add(db_chunk)

                # Add chunk to vector store
                vector_store.add_document(
                    doc_id=chunk['id'],
                    content=chunk['content'],
                    embedding=embeddings[i],
                    metadata={'document_id': doc_id, 'chunk_order': chunk['order']}
                )

            self.db.commit()
            return "INDEXED", f"Document '{title}' successfully processed and indexed"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating document: {e}")
            return "ERROR", f"Error processing document: {str(e)}"

    def get_document(self, doc_id: str) -> dict:
        """
        Retrieve a document by ID

        Args:
            doc_id: The ID of the document to retrieve

        Returns:
            Document data as a dictionary or None if not found
        """
        try:
            document = self.db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()

            if document:
                return {
                    'id': str(document.id),
                    'title': document.title,
                    'content': document.content,
                    'source_type': document.source_type,
                    'metadata': document.metadata_ or {},
                    'status': 'INDEXED',  # For simplicity, assuming all stored docs are indexed
                    'created_at': document.created_at.isoformat() if document.created_at else None
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            return None

    def _chunk_document(self, content: str, doc_id: str, chunk_size: int = 1000) -> list:
        """
        Split document content into chunks of specified size

        Args:
            content: The document content to chunk
            doc_id: The document ID to associate with chunks
            chunk_size: Size of each chunk in characters

        Returns:
            List of chunk dictionaries
        """
        chunks = []
        start = 0
        chunk_order = 0

        while start < len(content):
            end = start + chunk_size

            # Try to break at sentence boundary if possible
            if end < len(content):
                # Look for a sentence ending near the chunk boundary
                for i in range(end, min(end + 200, len(content))):
                    if content[i] in '.!?':
                        end = i + 1
                        break
                # If no sentence ending found, look for a paragraph boundary
                else:
                    for i in range(end, min(end + 200, len(content))):
                        if content[i] == '\n' and content[i-1] == '\n':  # Paragraph break
                            end = i + 1
                            break

            chunk_text = content[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunk = {
                    'id': str(uuid.uuid4()),
                    'document_id': doc_id,
                    'content': chunk_text,
                    'order': chunk_order
                }
                chunks.append(chunk)
                chunk_order += 1

            start = end

        return chunks

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its chunks

        Args:
            doc_id: The ID of the document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all chunks for this document
            chunks = self.db.query(DocumentChunkModel).filter(
                DocumentChunkModel.document_id == doc_id
            ).all()

            # Delete chunks from vector store
            for chunk in chunks:
                vector_store.delete_document(str(chunk.id))

            # Delete chunks from database
            for chunk in chunks:
                self.db.delete(chunk)

            # Delete document from database
            document = self.db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
            if document:
                self.db.delete(document)
                self.db.commit()
                return True

            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting document: {e}")
            return False

    def add_web_content(self, title: str, content: str, url: str, scraped_at: str = None, metadata: Dict = None) -> bool:
        """
        Add web content from sitemap to the vector store

        Args:
            title: Title of the web page
            content: Content of the web page
            url: URL of the web page
            scraped_at: Time when content was scraped
            metadata: Additional metadata to store with the content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a document ID based on URL and timestamp
            doc_id = f"web_{uuid.uuid4().hex[:12]}"

            # Chunk the content
            chunks = self._chunk_document(content, doc_id)

            # Create metadata for web content
            web_metadata = {
                "url": url,
                "source_type": "web_content",
                "title": title,
                "scraped_at": scraped_at or str(datetime.now()),
                **(metadata or {})
            }

            # Process chunks and generate embeddings
            for i, chunk_data in enumerate(chunks):
                chunk_text = chunk_data['content']

                # Generate embedding for this chunk using web content method
                embedding = self.embedding_service.embed_web_content({
                    "title": title,
                    "content": chunk_text
                })

                # Create chunk ID
                chunk_id = f"{doc_id}_chunk_{i}"

                # Add to vector store using the web content method
                vector_store.add_web_content(
                    doc_id=chunk_id,
                    title=title,
                    content=chunk_text,
                    embedding=embedding,
                    url=url,
                    scraped_at=scraped_at,
                    metadata=web_metadata
                )

            logger.info(f"Successfully added web content from {url} with {len(chunks)} chunks")
            return True
        except Exception as e:
            logger.error(f"Error adding web content from {url}: {e}")
            return False

    def process_sitemap_content(self, sitemap_content_list: List[Dict[str, Any]]) -> bool:
        """
        Process a list of sitemap content items and add them to the vector store

        Args:
            sitemap_content_list: List of dictionaries containing web content from sitemap

        Returns:
            True if all items processed successfully, False otherwise
        """
        try:
            success_count = 0
            total_count = len(sitemap_content_list)

            for i, content_item in enumerate(sitemap_content_list):
                logger.info(f"Processing sitemap content {i+1}/{total_count}: {content_item.get('url', 'unknown')}")

                success = self.add_web_content(
                    title=content_item.get('title', 'No Title'),
                    content=content_item.get('content', ''),
                    url=content_item.get('url', ''),
                    scraped_at=content_item.get('scraped_at'),
                    metadata=content_item.get('metadata', {})
                )

                if success:
                    success_count += 1
                else:
                    logger.error(f"Failed to process content from {content_item.get('url', 'unknown')}")

            logger.info(f"Successfully processed {success_count}/{total_count} sitemap content items")
            return success_count == total_count
        except Exception as e:
            logger.error(f"Error processing sitemap content: {e}")
            return False