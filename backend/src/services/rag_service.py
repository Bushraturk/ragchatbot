from typing import List, Dict, Any, Tuple
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
import cohere
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv
import litellm
from litellm import completion

from src.core.database import SessionLocal, ThreadDB, ThreadItemDB
from src.core.config import settings
from src.core.vector_store import vector_store

load_dotenv()

# Initialize external services
co = cohere.Client(settings.cohere_api_key)

# Configure LiteLLM - set API keys from environment
# LiteLLM automatically picks up GROQ_API_KEY, GEMINI_API_KEY from environment
import os
if os.getenv('GROQ_API_KEY'):
    os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
if os.getenv('GEMINI_API_KEY'):
    os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')

class RAGService:
    def __init__(self):
        self.collection_name = "book_content"
        self._initialized = False
        self.settings = settings
        # Use the shared vector store instance for consistency
        self.vector_store = vector_store

    def _ensure_initialized(self):
        """Lazily initialize by ensuring the vector store is initialized"""
        if not self._initialized:
            # Initialize the shared vector store instance
            self.vector_store._ensure_initialized()
            self._initialized = True

        # Initialize Cohere
        self.co = cohere.Client(settings.cohere_api_key)

    def _create_collection_if_not_exists(self):
        """Create the collection if it doesn't exist"""
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except:
            # Collection doesn't exist, create it
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            )

    def _chunk_document(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Split document content into chunks"""
        chunks = []
        start = 0
        
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
                chunks.append(chunk_text)
            
            start = end
        
        return chunks

    def add_document(self, doc_id: str, title: str, content: str, source_type: str = "BOOK_FULL") -> bool:
        """Add a document to the vector store"""
        try:
            self._ensure_initialized()

            # Chunk the document
            chunks = self._chunk_document(content)

            # Generate embeddings for chunks
            embeddings = self.co.embed(
                texts=chunks,
                model="embed-english-v3.0",
                input_type="search_document"
            )

            # Add each chunk to the vector store using the shared instance
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings.embeddings)):
                chunk_doc_id = f"{doc_id}_chunk_{i}"

                # Prepare metadata for the chunk
                chunk_metadata = {
                    "document_id": doc_id,
                    "chunk_id": chunk_doc_id,
                    "title": title,
                    "source_type": source_type,
                    "chunk_order": i
                }

                # Add to shared vector store
                self.vector_store.add_document(
                    doc_id=chunk_doc_id,
                    content=chunk_text,
                    embedding=embedding,
                    metadata=chunk_metadata
                )

            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False

    def retrieve_context(self, query: str, mode: str = "full_book", selected_text: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context based on mode"""
        if mode == "selected_text" and selected_text:
            # In selected text mode, return the selected text as context
            return [{
                "document_id": "selected_text",
                "content": selected_text,
                "metadata": {"source_type": "USER_SELECTION"},
                "similarity_score": 1.0
            }]
        else:
            # In full book mode, search in the vector store
            try:
                self._ensure_initialized()

                # Generate embedding for query
                query_embedding = self.co.embed(
                    texts=[query],
                    model="embed-english-v3.0",
                    input_type="search_query"
                ).embeddings[0]

                # Search in the shared vector store
                search_results = self.vector_store.search(
                    query_embedding=query_embedding,
                    limit=limit
                )

                context_items = []
                for result in search_results:
                    context_items.append({
                        "document_id": result.get("metadata", {}).get("document_id", ""),
                        "content": result.get("content", ""),
                        "metadata": {
                            "title": result.get("metadata", {}).get("title", ""),
                            "source_type": result.get("metadata", {}).get("source_type", ""),
                            "chunk_order": result.get("metadata", {}).get("chunk_order", 0)
                        },
                        "similarity_score": result.get("similarity_score", 0.0)
                    })

                return context_items
            except Exception as e:
                print(f"Error retrieving context: {e}")
                return []

    def generate_response(self, query: str, context_items: List[Dict[str, Any]], chat_history: List[Dict[str, str]] = None) -> str:
        """Generate response using Gemini with retrieved context"""
        try:
            # Combine context items into a single context string
            context_parts = []
            for item in context_items:
                content = item.get('content', '')
                if content:
                    context_parts.append(f"Context: {content}")

            combined_context = "\n\n".join(context_parts)

            # Create a prompt that includes the context and query
            system_prompt = f"""
            You are an assistant focused specifically on the Physical AI & Robotics course content.
            Answer the user's question based ONLY on the information provided in the context from the course materials.
            If the context does not contain relevant information to answer the question,
            please respond with "Information not found in the course content".
            If the question is not related to the course content, politely explain that you can only answer questions about the Physical AI & Robotics course.

            Context:
            {combined_context}
            """

            # Prepare messages for the model
            messages = [{"role": "system", "content": system_prompt}]

            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    messages.append({"role": role, "content": content})

            # Add the current query
            messages.append({"role": "user", "content": query})

            # Use LiteLLM to generate response
            response = litellm.completion(
                model=self.settings.llm_model,  # Using the model from settings
                messages=messages,
                temperature=0.1,  # Lower temperature for more consistent, factual responses
            )

            response_text = response.choices[0].message.content
            return response_text if response_text else "Information not found in the book"

        except Exception as e:
            error_str = str(e)
            print(f"Error generating response: {e}")

            # Handle rate limit errors
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "I'm currently experiencing high demand. Please try again in a few moments. (API rate limit reached)"

            # If we have context, return a summary of what we found
            if context_items:
                titles = [item.get('metadata', {}).get('title', '') for item in context_items[:3]]
                titles = [t for t in titles if t]
                if titles:
                    return f"I found relevant information in: {', '.join(titles)}. However, I couldn't generate a full response due to a temporary issue. Please try again."

            return "Information not found in the book"

    def process_query(self, query: str, mode: str = "full_book", selected_text: str = None, thread_id: str = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Process a query through the RAG pipeline"""
        # Retrieve relevant context
        context_items = self.retrieve_context(query, mode, selected_text)

        # Get chat history if thread is provided
        chat_history = []
        if thread_id:
            # This would load chat history from the database
            # Implementation would depend on the exact structure
            pass

        # Generate response using the retrieved context
        response = self.generate_response(query, context_items, chat_history)

        return response, context_items

    def process_request(self, session_id: str, message: str, mode: str = "full_book", selected_text: str = None) -> tuple:
        """
        Process a chat request through the RAG pipeline.

        Args:
            session_id: Unique identifier for the conversation session
            message: The user's query/message
            mode: Either 'full_book' or 'selected_text'
            selected_text: Text selected by the user when mode is 'selected_text'

        Returns:
            A tuple containing:
            - response (str): The generated response
            - context_references (list): List of context references in the expected format
        """
        # Use the existing process_query method with appropriate parameters
        response, context_items = self.process_query(
            query=message,
            mode=mode,
            selected_text=selected_text,
            thread_id=session_id
        )

        # Format context items to match the expected API response format
        context_references = []
        for item in context_items:
            context_references.append({
                "document_id": item.get("document_id", ""),
                "chunk_id": item.get("metadata", {}).get("chunk_id", ""),
                "content_snippet": item.get("content", "")[:200] + "..." if len(item.get("content", "")) > 200 else item.get("content", ""),
                "similarity_score": item.get("similarity_score", 0.0)
            })

        return response, context_references