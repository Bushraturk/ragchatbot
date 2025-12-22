# RAG ChatKit Gemini Backend API Documentation

## Table of Contents
- [Overview](#overview)
- [Current Implementation](#current-implementation)
- [Documented Architecture](#documented-architecture)
- [API Endpoints](#api-endpoints)
- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)

## Overview

This document describes both the current implementation and the documented architecture for the RAG ChatKit Gemini backend. There is a discrepancy between the documented architecture and the current implementation in main.py.

## Current Implementation

The current implementation in main.py uses the third-party `chatkit` library instead of the custom agent architecture documented below. The current system:

- Uses the `chatkit` library for conversation management
- Integrates with Google Gemini via LiteLLM using the `agents` library
- Stores conversation history in-memory using a custom `MemoryStore`
- Implements the ChatKit protocol for communication

## Documented Architecture

The documented architecture (in the src/ directory) implements a Retrieval-Augmented Generation (RAG) system using FastAPI. It integrates Cohere embeddings, Qdrant vector storage, and Google Gemini for document-based Q&A. The backend follows ChatKit-compatible API patterns while implementing an agent-based architecture for conversation processing.

## Current Architecture

### Core Components
- **FastAPI Application**: Main web server with RESTful API
- **ChatKit Library**: Third-party library for conversation management
- **Agents Library**: Third-party library for AI agent functionality
- **MemoryStore**: In-memory storage for conversation threads
- **GeminiChatKitServer**: Integration layer between ChatKit and Gemini
- **Middleware**: CORS handling and request processing

### Data Flow
1. Client sends message to `/chatkit` endpoint
2. GeminiChatKitServer processes the request using the ChatKit protocol
3. Conversations are handled by the agents library with LiteLLM
4. Response streamed back to client via the ChatKit protocol

## Documented Architecture

### Core Components
- **FastAPI Application**: Main web server with RESTful API
- **Agent-Based System**: Custom implementation with RAGAgent
- **Storage Layer**: Custom Store implementation with database persistence
- **RAG Service**: Document processing and retrieval pipeline
- **Middleware**: CORS handling and request processing

### Data Flow
1. Client sends message to `/chatkit` endpoint
2. AgentChatKitServer processes the request with RAGAgent
3. RAGAgent uses RAGTool to retrieve and generate responses
4. Response streamed back to client via SSE (Server-Sent Events)

## API Endpoints

### Current Implementation Endpoints

#### Chat Endpoint
```
POST /chatkit
```

##### Request Format
Uses the ChatKit protocol format, not a standard JSON body.

##### Response
Streaming response via the ChatKit protocol.

##### Behavior
- Handles chat requests using the ChatKit protocol
- Processes conversations using the agents library
- Stores thread history in-memory

### Documented Architecture Endpoints

#### Chat Endpoint
```
POST /chatkit
```

##### Request Body
```json
{
  "message": "string: the user message to process",
  "thread_id": "string (optional): ID of the conversation thread",
  "mode": "string: either 'full_book' or 'selected_text'",
  "selected_text": "string (optional): text to use in selected_text mode"
}
```

##### Response
Streaming response via Server-Sent Events (SSE) with format:
```
data: {response_chunk}
data: [DONE]
```

##### Behavior
- If no `thread_id` provided, generates a new thread
- Processes message based on selected `mode`
- Streams response in real-time using Server-Sent Events
- Persists conversation in the database

### Health Check
```
GET /health
```

#### Response
```json
{
  "status": "ok",
  "model": "gemini-2.0-flash"
}
```

### Debug Endpoints (Available in current implementation)
```
GET /debug/threads
```

#### Response
```json
{
  "threads": [
    // Thread objects with detailed information
  ],
  "count": "integer: number of threads"
}
```

### Documented Architecture Endpoints

#### Document Upload
```
POST /api/documents
```

#### Request
Form data with:
- `file`: Document file to upload
- `title` (optional): Title for the document

#### Response
```json
{
  "id": "string: document ID",
  "filename": "string: original filename",
  "title": "string: document title",
  "status": "uploaded"
}
```

#### Sessions Management
```
GET /api/sessions
```

#### Response
```json
{
  "sessions": [
    {
      "id": "string: session ID",
      "created_at": "datetime: session creation timestamp",
      "preview": [
        {
          "role": "string: message role",
          "content": "string: message preview content"
        }
      ],
      "message_count": "integer: number of messages in session"
    }
  ],
  "count": "integer: total number of sessions"
}
```

#### Session Detail
```
GET /api/chat/{session_id}
```

#### Response
```json
{
  "session_id": "string: session ID",
  "messages": [
    {
      "id": "string: message ID",
      "role": "string: message role (user/assistant)",
      "content": "string: message content",
      "timestamp": "datetime: message timestamp"
    }
  ]
}
```

#### Session Deletion
```
DELETE /api/sessions/{session_id}
```

#### Response
```json
{
  "message": "Session {session_id} deleted successfully"
}
```

## Core Classes

### Current Implementation Classes

#### GeminiChatKitServer
Main server class that handles ChatKit protocol requests and processes them with the third-party agent library.

##### Constructor
```python
def __init__(self, data_store: Store)
```

##### Methods
- `respond(thread, input, context)`: Process a message and return a streaming response via ChatKit protocol

#### MemoryStore
In-memory storage implementation adhering to the ChatKit Store interface.

##### Methods
- `load_thread(thread_id, context)`: Load a specific thread
- `load_thread_items(thread_id, after, limit, order, context)`: Load items from a thread
- `add_thread_item(thread_id, item, context)`: Add an item to a thread
- `delete_thread(thread_id, context)`: Delete a thread
- `generate_thread_id(context)`: Generate a new thread ID
- `generate_item_id(type, thread_id, context)`: Generate a new item ID

### Documented Architecture Classes

#### AgentChatKitServer
Main server class that handles ChatKit-style requests and processes them with the agent.

##### Constructor
```python
def __init__(self, data_store: Store)
```

##### Methods
- `respond(thread, input_item, request_context)`: Process a message and return a streaming response

#### RAGAgent
Specialized agent for RAG operations that extends the base Agent class.

##### Constructor
```python
def __init__(self, name: str = "RAG-Agent", system_prompt: str = None)
```

##### Methods
- `process(messages, context)`: Process a list of messages and return streaming events

#### AgentContext
Context container for agent operations.

##### Constructor
```python
def __init__(self, thread_id, session_metadata, agent_config, tools)
```

#### Store
Data storage abstraction layer.

##### Methods
- `load_thread(thread_id, context)`: Load a specific thread
- `load_thread_items(thread_id, after, limit, order, context)`: Load items from a thread
- `add_thread_item(thread_id, item, context)`: Add an item to a thread
- `delete_thread(thread_id, context)`: Delete a thread
- `generate_thread_id(context)`: Generate a new thread ID
- `generate_item_id(type, thread_id, context)`: Generate a new item ID

## Configuration

### Environment Variables (Current Implementation)
- `GEMINI_API_KEY`: Google Gemini API key

### Environment Variables (Documented Architecture)
- `DATABASE_URL`: PostgreSQL connection string (Neon)
- `QDRANT_URL`: Qdrant Cloud URL
- `QDRANT_API_KEY`: Qdrant API key
- `GEMINI_API_KEY`: Google Gemini API key
- `COHERE_API_KEY`: Cohere API key
- `LLM_MODEL`: LLM model identifier (default: gemini/gemini-2.0-flash)
- `EMBEDDING_MODEL`: Embedding model identifier (default: embed-english-v3.0)
- `DEBUG_MODE`: Enable debug endpoints when set to "true" (default: "false")

### Startup
The application initializes:
1. Database tables via `init_db()`
2. Store instance for data persistence
3. AgentChatKitServer with RAGAgent
4. CORS middleware for cross-origin requests

## Usage Examples

### Sending a Message (Full Book Mode)
```javascript
fetch('http://localhost:8000/chatkit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What is the main theme of this book?',
    mode: 'full_book'
  }),
})
.then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  return new ReadableStream({
    start(controller) {
      function push() {
        reader.read().then(({done, value}) => {
          if (done) {
            controller.close();
            return;
          }
          
          const chunk = decoder.decode(value, {stream: true});
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data && data !== '[DONE]') {
                console.log(data);
              }
            }
          }
          
          push();
        });
      }
      
      push();
    }
  });
});
```

### Sending a Message (Selected Text Mode)
```javascript
fetch('http://localhost:8000/chatkit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Can you explain this concept?',
    mode: 'selected_text',
    selected_text: 'The concept of artificial intelligence involves machines simulating human intelligence processes.'
  }),
})
// ... handle response similarly to previous example
```

### Uploading a Document
```javascript
const formData = new FormData();
formData.append('file', documentFile);
formData.append('title', 'My Book Title');

fetch('http://localhost:8000/api/documents', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(result => console.log(result));
```

### Getting Session History
```javascript
fetch('http://localhost:8000/api/chat/' + sessionId)
.then(response => response.json())
.then(data => console.log(data.messages));
```

## Error Handling

The API uses standard HTTP status codes:
- `200`: Success for GET/PUT/PATCH/DELETE requests
- `201`: Success for POST requests
- `400`: Bad request (malformed request body, validation failure)
- `404`: Resource not found
- `500`: Internal server error

Errors in the streaming response will appear as:
```
data: Error: {error_description}
data: [DONE]
```

## Testing the API

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Simple Message
```bash
curl -X POST http://localhost:8000/chatkit \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "mode": "full_book"}'
```

### Document Upload
```bash
curl -X POST http://localhost:8000/api/documents \
  -F "file=@/path/to/document.txt" \
  -F "title=Document Title"
```