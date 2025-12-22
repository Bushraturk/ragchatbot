# Quickstart Guide: Integrated RAG Chatbot

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development)
- Access to Google Gemini API
- Access to Cohere API
- Qdrant Cloud account
- Neon Serverless Postgres account

### Environment Setup
1. Clone the repository
2. Create a `.env` file in the backend directory with the following:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   COHERE_API_KEY=your_cohere_api_key
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   DATABASE_URL=your_neon_postgres_connection_string
   ```
3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

### Backend
1. Start the database migrations:
   ```bash
   cd backend
   python -m src.core.database setup
   ```
2. Run the backend server:
   ```bash
   cd backend
   uvicorn src.api.main:app --reload --port 8000
   ```

### Frontend (separate terminal)
1. From the frontend directory:
   ```bash
   cd frontend
   npm start
   ```

## API Usage Examples

### Starting a New Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main theme of this book?",
    "mode": "full_book"
  }'
```

### Continuing a Session
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "existing-session-uuid",
    "message": "Can you elaborate on that point?",
    "mode": "full_book"
  }'
```

### Using Selected Text Mode
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does this selected text mean?",
    "mode": "selected_text",
    "selected_text": "This is the text the user has selected..."
  }'
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Key Architecture Components

1. **RAG Service** (`src/services/rag_service.py`): Orchestrates the retrieval and generation process
2. **Embedding Service** (`src/services/embedding_service.py`): Handles document and query vectorization
3. **LLM Service** (`src/services/llm_service.py`): Interfaces with Gemini for response generation
4. **Document Service** (`src/services/document_service.py`): Manages document ingestion and storage
5. **Session Service** (`src/services/session_service.py`): Manages conversation state

## Configuration

All configuration is managed in `src/core/config.py` and environment variables. Key settings include:
- API keys for external services
- Vector store connection parameters
- Database connection settings
- Model parameters for Gemini