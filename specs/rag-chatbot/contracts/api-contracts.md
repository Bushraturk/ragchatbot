# API Contract: Integrated RAG Chatbot

## Chat Endpoints

### POST /api/chat
Initiate a new chat or continue an existing conversation

**Request Body**:
```json
{
  "session_id": "string (UUID, optional - if continuing existing session)",
  "message": "string (the user's message/question)",
  "mode": "string (optional - 'full_book' or 'selected_text', defaults to 'full_book')",
  "selected_text": "string (optional - text selected by user for 'selected_text' mode)"
}
```

**Response**:
```json
{
  "session_id": "string (UUID)",
  "response": "string (the chatbot's response)",
  "context_references": [
    {
      "document_id": "string (UUID)",
      "chunk_id": "string (UUID)",
      "content_snippet": "string (relevant text snippet)",
      "similarity_score": "number (cosine similarity score)"
    }
  ],
  "timestamp": "string (ISO 8601 datetime)"
}
```

**Error Responses**:
- 400: Invalid request parameters
- 404: Session not found
- 500: Internal server error during processing

### GET /api/chat/{session_id}
Retrieve chat history for a session

**Path Parameters**:
- session_id: "string (UUID)"

**Response**:
```json
{
  "session_id": "string (UUID)",
  "messages": [
    {
      "id": "string (UUID)",
      "sender_type": "string (USER or ASSISTANT)",
      "content": "string",
      "timestamp": "string (ISO 8601 datetime)",
      "context_references": "array of context reference objects"
    }
  ]
}
```

**Error Responses**:
- 404: Session not found
- 500: Internal server error

## Document Endpoints

### POST /api/documents
Upload and process a new book document

**Request Body**:
```json
{
  "title": "string (document title)",
  "content": "string (full text content of the document)",
  "source_type": "string ('BOOK_FULL' or 'BOOK_SELECTION', defaults to 'BOOK_FULL')"
}
```

**Response**:
```json
{
  "document_id": "string (UUID)",
  "status": "string (PROCESSING, INDEXED, or ERROR)",
  "message": "string (additional status information)"
}
```

**Error Responses**:
- 400: Invalid document format or missing fields
- 500: Internal server error during processing

### GET /api/documents/{document_id}
Retrieve information about a specific document

**Path Parameters**:
- document_id: "string (UUID)"

**Response**:
```json
{
  "document_id": "string (UUID)",
  "title": "string",
  "source_type": "string",
  "metadata": "object (additional document metadata)",
  "status": "string (PROCESSING, INDEXED, or ARCHIVED)",
  "created_at": "string (ISO 8601 datetime)"
}
```

**Error Responses**:
- 404: Document not found
- 500: Internal server error

## Session Endpoints

### GET /api/sessions
List all sessions for the user (future implementation with auth)

**Response**:
```json
{
  "sessions": [
    {
      "id": "string (UUID)",
      "title": "string (auto-generated from first message or custom)",
      "created_at": "string (ISO 8601 datetime)",
      "updated_at": "string (ISO 8601 datetime)",
      "metadata": "object (session metadata like mode settings)"
    }
  ]
}
```

### DELETE /api/sessions/{session_id}
Delete a specific session and its messages

**Path Parameters**:
- session_id: "string (UUID)"

**Response**: Empty body with 204 status

**Error Responses**:
- 404: Session not found
- 500: Internal server error

## Health Check Endpoint

### GET /health
Check the health status of the service

**Response**:
```json
{
  "status": "string (healthy or unhealthy)",
  "timestamp": "string (ISO 8601 datetime)",
  "services": {
    "database": "boolean",
    "vector_store": "boolean",
    "llm_provider": "boolean"
  }
}
```