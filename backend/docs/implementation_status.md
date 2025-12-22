# RAG ChatKit Gemini - Implementation Status

## Current Implementation

The current backend implementation uses the `chatkit` library as an external dependency, not the custom agent architecture that was documented in the project documentation.

### Current Architecture
- **Main Application**: `main.py` uses `chatkit` library for handling conversations
- **Storage**: In-memory `MemoryStore` implementation from `chatkit`
- **LLM**: Google Gemini via LiteLLM using the `agents` library
- **Endpoints**: 
  - `/chatkit` - Handles chat requests using ChatKit protocol
  - `/health` - Health check endpoint
  - `/debug/threads` - Debug endpoint showing stored threads

### Key Dependencies
- `chatkit` - Third-party library for chat functionality
- `agents` - Third-party library for agent functionality
- `agents.extensions.models.litellm_model` - For LLM integration

## Unconnected/Unused Files

The following files represent an alternative implementation that is currently not in use:

### Agent System (`src/agents/`)
- `rag_agent.py` - Custom RAG agent implementation
  - Extends the base Agent class
  - Integrates with RAGTool for document retrieval
  - Uses agent-based processing for conversations

### API Routes (`src/api/`)
- `api/main.py` - Alternative FastAPI implementation
- `api/routes/chat.py` - Custom chat endpoints with dual-mode support
- `api/routes/documents.py` - Document upload and management
- `api/routes/sessions.py` - Session management
- `api/middleware/auth.py` - Authentication middleware

### Core Components (`src/core/`)
- `vector_store.py` - Qdrant vector database integration
  - Handles adding, searching, and deleting documents
  - Supports both document and web content storage
  - Manages embeddings and metadata

### Database Models (`src/models/`)
- `database_models.py` - SQLAlchemy database models
  - Session model for conversation tracking
  - Message model for storing conversation history
  - Document and DocumentChunk models for RAG functionality
- `entities.py` - Pydantic models for API requests/responses

### Services (`src/services/`)
- `document_service.py` - Document processing and storage
  - Handles document creation, chunking, and embedding
  - Integrates with vector store for RAG functionality
- `embedding_service.py` - Cohere embedding generation
  - Creates embeddings for documents, queries, and web content
- `session_service.py` - Session management
  - Handles conversation history and metadata
- `rag_service.py` - Core RAG functionality
  - Manages document retrieval and response generation
  - Implements dual-mode operation (full-book vs selected-text)
- `rag_tool.py` - RAG tool for agent integration
  - Provides RAG capabilities to agents
  - Handles query processing and context retrieval

### Utilities (`src/utils/`)
- `sitemap_embedder.py` - Sitemap processing pipeline
  - Parses sitemaps and extracts URLs
  - Scrapes content from web pages
  - Generates embeddings and stores in vector database
- `sitemap_parser.py` - Sitemap URL extraction
- `web_scraper.py` - Web content scraping

## Documentation Mismatch

The documentation files previously created (`api_documentation.md`, `agent_system.md`, `architecture.md`, `deployment.md`) describe the unconnected implementation rather than the current implementation. These files document the intended RAG system architecture based on the custom agent system, but the current application uses the `chatkit` library instead.

## Synchronization Needed

To align the implementation with the documentation:

### Option 1: Switch to Custom Implementation
Update `main.py` to use the custom agent architecture:
- Replace chatkit dependency with custom RAGAgent
- Integrate with PostgreSQL database
- Use Qdrant vector store
- Implement RAG functionality

### Option 2: Update Documentation
Update all documentation to reflect the current chatkit-based implementation.

## Current Requirements

The current implementation requires additional dependencies not listed in the original requirements:
- `chatkit`
- `agents`
- `litellm`

These are not reflected in the existing `requirements.txt` file.

## Recommendation

To resolve this discrepancy, either:
1. Update the implementation to match the documented RAG architecture, or
2. Update the documentation to match the current chatkit-based implementation