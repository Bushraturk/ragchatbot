---
title: RAG ChatKit Gemini
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
---

# RAG ChatKit Gemini

A Retrieval-Augmented Generation (RAG) chatbot that allows users to ask questions about Physical AI & Robotics course content. The system uses Google's Gemini API through LiteLLM, with Cohere embeddings, Qdrant vector storage, and Neon Postgres for conversation history.

## Features

- **RAG-based Architecture**: Answers based on retrieved book content rather than general knowledge
- **Dual-mode Operation**: 
  - Full-book question answering
  - Selected-text mode (answers only based on user-selected text)
- **Conversation History**: Maintains context across multiple exchanges using threads
- **Vector Storage**: Uses Qdrant for efficient semantic search
- **Persistent Storage**: Stores conversation threads in Postgres database

## Architecture

The application consists of:

- **Frontend**: React-based chat interface
- **Backend**: FastAPI server using the chatkit library
- **Storage**: In-memory storage (with potential for database integration)
- **AI Services**: Google Gemini via LiteLLM for responses
- **Agent System**: Third-party agents library for conversation processing

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
pip install -r requirements.txt
pip install chatkit agents  # Additional dependencies for current implementation
```

4. Set up environment variables in `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
# The following are for the documented RAG implementation but not used in current chatkit-based version:
# DATABASE_URL=your_neon_postgres_connection_string
# QDRANT_URL=your_qdrant_cloud_url
# QDRANT_API_KEY=your_qdrant_api_key
# COHERE_API_KEY=your_cohere_api_key
```

## Usage

1. Start the backend server:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. For the frontend, navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000 and will connect to the backend at http://localhost:8000.

## API Endpoints

- `POST /chatkit` - Process chat requests using the ChatKit protocol
  - Uses the third-party chatkit library for conversation management
  - Request and response format follows ChatKit protocol specification
- `GET /health` - Check the health status of the service
  - Response: `{ "status": "ok", "model": "gemini-2.0-flash" }`
- `GET /debug/threads` - Debug endpoint to view all stored threads
  - Response: Detailed information about all stored conversation threads

## Environment Variables

- `GEMINI_API_KEY`: API key for Google Gemini (required for current implementation)
- `DATABASE_URL`: Connection string for Neon Postgres (for the documented RAG implementation)
- `QDRANT_URL`: URL for Qdrant Cloud instance (for the documented RAG implementation)
- `QDRANT_API_KEY`: API key for Qdrant Cloud (for the documented RAG implementation)
- `COHERE_API_KEY`: API key for Cohere (for the documented RAG implementation)

## Running Tests

Tests are not currently included but can be added using pytest:

```bash
# From backend directory
pip install pytest httpx
pytest
```

## How the Current System Works

The current implementation uses the third-party `chatkit` library:

1. Chat requests are processed through the ChatKit protocol
2. Conversations are managed using the agents library
3. Google Gemini generates responses via LiteLLM
4. Conversation history is stored in an in-memory store
5. The system doesn't currently implement RAG functionality with document embeddings

## How RAG Would Work (Documented Implementation)

The documented architecture supports RAG functionality:

1. When a document is added, it's chunked and embeddings are generated using Cohere
2. These embeddings are stored in Qdrant vector database
3. When a user asks a question, embeddings are generated for the query
4. Qdrant finds the most similar document chunks based on semantic similarity
5. These relevant chunks are provided as context to the Gemini model
6. The model generates a response based only on the provided context
7. If the context doesn't contain relevant information, the system responds with "Information not found in the book"

## Current System Capabilities

The current implementation using `chatkit` provides:

- Basic conversation management
- Thread-based conversation history
- Integration with Google Gemini

## Documented Dual-mode Support

The documented architecture supports two modes of operation:

1. **Full-book mode**: Searches across the entire book content for relevant information
2. **Selected-text mode**: Answers questions based only on user-selected text

The mode would be specified when sending a message to the API in the documented implementation.

## Thread-based Conversations

In the current implementation:
- Conversations are organized into threads using the chatkit library
- Thread history is maintained in-memory
- Each thread has a unique ID

In the documented architecture:
- Conversations would be organized into threads with persistent storage
- Thread history would be stored in a database
- Each thread would have a unique ID and metadata