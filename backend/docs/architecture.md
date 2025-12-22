# System Architecture

## Overview

The RAG ChatKit Gemini system implements a modern RAG (Retrieval-Augmented Generation) architecture with an agent-based processing system. The system is built with FastAPI and designed to work with ChatKit-compatible clients while implementing advanced document-based Q&A capabilities.

## High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Frontend      │    │    Backend       │    │   External       │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   Services       │
│                 │    │                  │    │                  │
│ ChatInterface   │    │ AgentChatKit     │    │ Google Gemini    │
│ ChatKit Service │    │ Server           │    │                  │
│ SessionManager  │    │                  │    │ Qdrant Vector    │
└─────────────────┘    │ Agent System     │    │ DB               │
                       │ • RAGAgent       │    │                  │
                       │ • RAGTool        │    │ Cohere Embedding │
                       │ • AgentContext   │    │ Service          │
                       └──────────────────┘    │                  │
                                             │ Neon Postgres    │
                                             └──────────────────┘
```

## Component Breakdown

### Frontend Components
- **ChatKit Service**: Provides a ChatKit-compatible interface for frontend applications
- **ChatPage**: Main chat interface with dual-mode support
- **ChatInterface**: Message display and user interaction component
- **SessionManager**: Thread management and switching
- **Message Component**: Individual message rendering

### Backend Components
- **FastAPI Application**: Core web server with CORS and middleware
- **AgentChatKitServer**: Integration layer between API and agent system
- **RAGAgent**: Specialized agent for document-based Q&A
- **RAGTool**: Tool for retrieving and processing document context
- **Store**: Data persistence layer with thread management
- **RAGService**: Document processing and retrieval pipeline
- **Database Layer**: SQLAlchemy ORM with Neon Postgres

### External Services
- **Qdrant Cloud**: Vector database for semantic search
- **Cohere**: Embedding generation for documents and queries
- **Google Gemini**: Language model for response generation
- **Neon Postgres**: Persistent storage for conversation history

## Data Flow

### Message Processing Flow
1. **Client Request**: Frontend sends message to `/chatkit` endpoint
2. **Thread Loading**: Backend loads existing thread or creates new one
3. **Agent Context Creation**: Context is created with mode and selected text info
4. **Message Conversion**: Thread items are converted to agent messages
5. **Agent Processing**: RAGAgent processes messages using RAGTool
6. **Context Retrieval**: RAGTool retrieves relevant context from vector store
7. **Response Generation**: Gemini generates response based on context
8. **Streaming Response**: Response is streamed back via Server-Sent Events
9. **History Persistence**: Response is saved to conversation history

### Document Processing Flow
1. **Document Upload**: File uploaded via `/api/documents` endpoint
2. **Content Extraction**: Document content is extracted and validated
3. **Chunking**: Content is split into manageable chunks with sentence/paragraph boundaries
4. **Embedding**: Chunks are embedded using Cohere embedding service
5. **Storage**: Embeddings are stored in Qdrant vector database with metadata
6. **Indexing**: Content is indexed for efficient retrieval

## API Architecture

### ChatKit Compatibility
The system implements ChatKit-style endpoints while using an agent-based backend:
- `/chatkit` endpoint handles message streaming with SSE
- Session management through thread IDs
- Dual-mode operation support (full-book vs selected-text)

### Streaming Implementation
- Server-Sent Events (SSE) for real-time message streaming
- Asynchronous processing throughout the pipeline
- Chunked response delivery for large responses

### Session Management
- Thread-based conversation persistence
- Metadata storage with creation times
- Cross-session user support

## Agent-Based Design

### Benefits of Agent Architecture
- **Extensibility**: New tools and capabilities can be added easily
- **Modularity**: Clear separation between core logic and specialized functions
- **Scalability**: Agents can be parallelized and distributed
- **Maintainability**: Well-defined interfaces between components

### Tool System
- **RAG Tool**: Provides document retrieval capabilities
- **Future Extensibility**: Additional tools can be implemented for other functions
- **Context Awareness**: Tools have access to conversation context and metadata

## Data Storage Architecture

### Thread Storage
- Persistent conversation history in Neon Postgres
- Thread metadata with creation times and metadata
- Message content with role and timestamp information

### Vector Storage
- Document chunks stored in Qdrant with embeddings
- Metadata includes source, title, and chunk ordering
- Semantic search for relevant context retrieval

### Database Schema
- ThreadDB: Stores conversation thread metadata
- ThreadItemDB: Stores individual messages in threads
- Proper indexing for efficient query performance

## Mode Support

### Full-Book Mode
- Searches entire document corpus for relevant context
- Uses vector similarity search in Qdrant
- Best for general questions about uploaded documents

### Selected-Text Mode
- Uses only user-selected text as context
- Provides focused responses based on specific text
- Useful for detailed analysis of specific passages

## Error Handling and Resilience

### Error Handling Strategy
- Comprehensive error handling at each layer
- Graceful degradation when services are unavailable
- Clear error messages streamed via SSE to clients

### Circuit Breaker Pattern
- Implemented for external service calls
- Prevents cascade failures
- Improves system resilience

## Security Considerations

### API Security
- Environment variables for sensitive keys
- No hardcoded credentials in code
- Input validation for file uploads

### Data Privacy
- User data stored securely in Neon Postgres
- Document content stored with proper access controls
- Conversation history privacy maintained

## Performance Considerations

### Caching Strategy
- Potential for caching frequently accessed embeddings
- Session data caching to reduce database load
- Query result caching for repeated questions

### Asynchronous Processing
- Async/await throughout the codebase
- Non-blocking I/O operations
- Efficient resource utilization

### Scalability Points
- Stateless agent processing
- Distributed vector database
- Independent service scaling capabilities