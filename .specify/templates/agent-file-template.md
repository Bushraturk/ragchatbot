<!-- AGENT CONTEXT START - DO NOT REMOVE OR MODIFY -->
# Agent Context for RAG Chatbot Implementation

## Technologies Used

- **Backend Framework**: FastAPI (Python 3.11)
- **LLM**: Google Gemini
- **Embeddings**: Cohere
- **Vector Store**: Qdrant Cloud
- **Database**: Neon Serverless Postgres
- **Frontend**: React with ChatKit-style UI

## Architecture Principles

- Clean Architecture with separation of concerns
- RAG-first approach: retrieval before generation
- Dual-mode support: full-book and selected-text modes
- Session-based conversation management

## Key Components

- **RAG Service**: Orchestrates retrieval and generation
- **Embedding Service**: Handles document and query vectorization
- **LLM Service**: Interfaces with Gemini for response generation
- **Document Service**: Manages document ingestion and storage
- **Session Service**: Manages conversation state

## API Endpoints

- `/api/chat` - Main chat interface with session management
- `/api/documents` - Document upload and management
- `/api/sessions` - Session listing and management

## Database Models

- **Session**: Chat session with metadata
- **Message**: Individual chat messages
- **Document**: Book content with metadata
- **DocumentChunk**: Vector-indexed document segments

## Environment Variables

- `GEMINI_API_KEY`
- `COHERE_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `DATABASE_URL`

<!-- AGENT CONTEXT END - DO NOT REMOVE OR MODIFY -->