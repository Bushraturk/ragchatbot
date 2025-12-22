# Data Model: Integrated RAG Chatbot

## Core Entities

### Session
Represents a chat session with unique ID, creation time, and metadata

**Fields**:
- id: UUID (Primary Key)
- created_at: DateTime (timestamp when session was created)
- updated_at: DateTime (timestamp when session was last updated)
- metadata: JSON (additional session-specific data like mode settings)

**Relationships**:
- One-to-Many with Message (one session has many messages)

### Message
Represents a single message with sender type, content, timestamp, and context references

**Fields**:
- id: UUID (Primary Key)
- session_id: UUID (Foreign Key to Session)
- sender_type: Enum (USER or ASSISTANT)
- content: Text (the actual message content)
- timestamp: DateTime (when the message was created)
- context_references: JSON (references to source documents/chunks that influenced the response)

**Relationships**:
- Many-to-One with Session (many messages belong to one session)

### Document
Represents a book document or text selection with content, metadata, and vector embeddings

**Fields**:
- id: UUID (Primary Key)
- title: Text (title of the document)
- content: Text (full content of the document)
- source_type: Enum (BOOK_FULL or BOOK_SELECTION)
- metadata: JSON (additional document metadata like page numbers, chapter, etc.)
- created_at: DateTime
- updated_at: DateTime

**Relationships**:
- One-to-Many with DocumentChunk (one document has many chunks)

### DocumentChunk
Represents a smaller chunk of a document that is indexed in the vector store

**Fields**:
- id: UUID (Primary Key)
- document_id: UUID (Foreign Key to Document)
- content: Text (content of the chunk)
- embedding: Vector (the embedding vector stored in the database as reference, primarily in vector store)
- chunk_order: Integer (order of the chunk in the original document)
- metadata: JSON (additional chunk metadata like page numbers, etc.)

**Relationships**:
- Many-to-One with Document (many chunks belong to one document)

### User
Represents system user (for future extensibility)

**Fields**:
- id: UUID (Primary Key)
- email: Text (user's email)
- created_at: DateTime
- preferences: JSON (user-specific preferences)

**Relationships**:
- One-to-Many with Session (one user has many sessions)

## State Transitions

### Session States
- ACTIVE: Session is currently in progress and accepting new messages
- INACTIVE: Session is not currently active but preserved in history
- ARCHIVED: Session is preserved but not actively accessible (long-term storage)

### Document States
- PROCESSING: Document is being ingested and embeddings are being generated
- INDEXED: Document is fully processed and available for search
- UNINDEXED: Document is stored but not yet available for search
- ARCHIVED: Document is preserved for historical purposes but not actively searchable

## Validation Rules

### Session Validation
- A session must have a unique ID
- Timestamps must be in UTC
- Session metadata must be valid JSON

### Message Validation
- A message must belong to a valid session
- Content must not exceed predetermined length limits
- Sender type must be either USER or ASSISTANT
- Context references must be valid document chunks

### Document Validation
- Document content must be non-empty
- Title must be provided
- Source type must be either BOOK_FULL or BOOK_SELECTION
- Document must be properly formatted text

## Indexes

### Database Indexes
- Session table: Index on (id, created_at)
- Message table: Index on (session_id, timestamp)
- Document table: Index on (id, source_type)
- DocumentChunk table: Index on (document_id, chunk_order)

### Vector Store Indexes
- Document chunks indexed by their embedding vectors in Qdrant
- Payload includes document_id, chunk_order, and metadata for retrieval
- Collection configured with HNSW index for efficient similarity search