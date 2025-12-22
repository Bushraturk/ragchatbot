# Feature Specification: Integrated RAG Chatbot

**Feature Branch**: `###-rag-chatbot`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Design the full implementation plan for the Integrated RAG Chatbot feature."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask Questions About Book Content (Priority: P1)

Users can ask questions about the book content and receive accurate answers based on the book's information.

**Why this priority**: This is the core functionality that users expect from a RAG chatbot.

**Independent Test**: Can be fully tested by asking a question and verifying that the response is based on retrieved context from the book content.

**Acceptance Scenarios**:

1. **Given** user has loaded the book content, **When** user asks a question about the book, **Then** the system retrieves relevant context and provides an accurate response
2. **Given** user has loaded the book content, **When** user asks a question not found in the book, **Then** the system responds with "Information not found in the book"

---

### User Story 2 - Select Specific Text for Context (Priority: P2)

Users can select specific text from the book and ask questions that are answered only based on that selected text.

**Why this priority**: Provides more focused, precise answers when users want to restrict the context scope.

**Independent Test**: Can be fully tested by selecting text, asking a question, and verifying the response is based only on the selected text.

**Acceptance Scenarios**:

1. **Given** user has selected specific text, **When** user asks a question, **Then** the system responds based only on the selected text (ignoring the broader book context)
2. **Given** user has selected specific text and asked a question, **When** user clears the selection, **Then** the system returns to full-book question answering

---

### User Story 3 - Maintain Conversation History (Priority: P3)

Users can have a coherent conversation with the chatbot that remembers context across multiple exchanges.

**Why this priority**: Essential for natural conversation flow and improved user experience.

**Independent Test**: Can be fully tested by having a multi-turn conversation and verifying that the system remembers context from previous exchanges.

**Acceptance Scenarios**:

1. **Given** user has started a session, **When** user has multiple exchanges, **Then** the system maintains context across the conversation
2. **Given** user has multiple sessions, **When** user switches between them, **Then** the system maintains separate conversation histories

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store chat history in Neon Serverless Postgres database
- **FR-002**: System MUST retrieve relevant content from Qdrant Cloud vector store before generating responses
- **FR-003**: System MUST use Cohere embeddings for document and query vectorization
- **FR-004**: System MUST use Gemini as the LLM for response generation
- **FR-005**: System MUST support dual-mode operation: full-book and user-selected text modes
- **FR-006**: System MUST ensure user-selected text mode overrides global context when active
- **FR-007**: System MUST implement session-based chat memory
- **FR-008**: System MUST follow clean architecture principles with clear separation of layers
- **FR-009**: System MUST not generate responses without first retrieving relevant context
- **FR-010**: System MUST properly cite or reference retrieved content internally

### Key Entities *(include if feature involves data)*

- **Session**: Represents a chat session with unique ID, creation time, and metadata
- **Message**: Represents a single message with sender type, content, timestamp, and context references
- **Document**: Represents a book document or text selection with content, metadata, and vector embeddings
- **User**: Represents system user (for future extensibility)
- **ChatHistory**: Represents the collection of messages for a session

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can ask questions and receive responses based on book content in under 5 seconds
- **SC-002**: Users can switch between full-book and selected-text modes without losing conversation context
- **SC-003**: System achieves at least 95% accuracy in retrieving relevant context for user queries
- **SC-004**: System properly handles context switching between different modes (full-book vs selected text)
- **SC-005**: 90% of users can successfully ask a question and receive a relevant response on first attempt

---

## Implementation Status *(Updated: December 22, 2024)*

### Data Pipeline - COMPLETED

| Task | Status | Details |
|------|--------|---------|
| Sitemap Fetch | ✅ Done | 78 pages from `https://bushraturk.github.io/my-website/sitemap.xml` |
| Web Scraping | ✅ Done | All 78 pages scraped with content extraction |
| Embedding Generation | ✅ Done | Cohere `embed-english-v3.0` (1024 dimensions) |
| Qdrant Storage | ✅ Done | 172 vectors stored in cloud collection `book_content` |

### Technical Configuration

| Component | Configuration |
|-----------|---------------|
| Sitemap URL | `https://bushraturk.github.io/my-website/sitemap.xml` |
| Embedding Model | Cohere `embed-english-v3.0` |
| Vector Dimension | 1024 |
| Vector Store | Qdrant Cloud |
| Collection Name | `book_content` |
| Distance Metric | Cosine |
| Total Vectors | 172 |
| LLM | Google Gemini 2.0 Flash |

### Content Indexed

**78 Documents** covering:
- Course Modules: ROS 2, Gazebo/Unity, NVIDIA Isaac, VLA
- Instructor Guides: Assessment Rubrics, Hardware, Lesson Plans, Troubleshooting
- Tutorials: Document creation, Deployment, Markdown features
- Guides: Accessibility, AI Integration, Performance Optimization
- Translation features and validation pages

### Scripts Used

```bash
# Fetch sitemap data
cd backend && python fetch_sitemap_data.py

# Generate embeddings and store in Qdrant
python generate_embeddings.py
```

### Output Files
- `backend/scraped_sitemap_data.json` - 78 scraped documents
- `backend/sitemap_summary.json` - Fetch summary with metadata