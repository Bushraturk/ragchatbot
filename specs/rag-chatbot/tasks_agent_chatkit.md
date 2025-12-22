---

description: "Updated task list for the RAG Chatbot implementation with Agent SDK and ChatKit SDK"
---

# Tasks: Integrated RAG Chatbot with Agent SDK and ChatKit SDK

**Input**: Design documents from `/specs/rag-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as specified in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume web app structure based on plan.md

<!--
  ============================================================================
  IMPORTANT: The tasks below are based on the updated design with Agent SDK and ChatKit SDK integration
  ============================================================================

  The tasks are organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure with Agent SDK and ChatKit SDK

- [X] T001 Create project structure per implementation plan with backend/ and frontend/ directories
- [X] T002 Initialize backend Python project with FastAPI dependencies in backend/requirements.txt
- [X] T003 Initialize frontend React project with required dependencies in frontend/package.json
- [X] T004 [P] Configure linting and formatting tools for both backend (black, ruff) and frontend (ESLint, Prettier)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Setup database schema and migrations framework for Neon Postgres in backend/src/core/database.py
- [X] T006 [P] Configure Qdrant Cloud client and connection in backend/src/core/vector_store.py
- [X] T007 [P] Setup API routing and middleware structure in backend/src/api/main.py
- [X] T008 Create configuration management for API keys and service URLs in backend/src/core/config.py
- [X] T009 Setup error handling and logging infrastructure in backend/src/api/middleware/auth.py
- [X] T010 [P] Implement basic health check endpoint in backend/src/api/routes/chat.py
- [X] T011 Create base models/entities that all stories depend on in backend/src/models/entities.py
- [X] T012 Create session management service in backend/src/services/session_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: Agent SDK Implementation

**Purpose**: Core Agent SDK infrastructure for RAG processing

- [X] T013 Implement base Agent classes in backend/src/core/agent_base.py
- [X] T014 Create RAG Tool for agent integration in backend/src/services/rag_tool.py
- [X] T015 Implement RAG Agent with Agent SDK patterns in backend/src/agents/rag_agent.py
- [X] T016 Integrate Agent SDK with existing RAG service in backend/src/services/rag_service.py

**Checkpoint**: Agent SDK infrastructure ready

---

## Phase 4: ChatKit SDK Implementation

**Purpose**: Core ChatKit SDK infrastructure for frontend communication

- [X] T017 Create ChatKit service in frontend/src/services/chatkit.js
- [X] T018 Update API endpoints to follow ChatKit patterns in backend/main.py
- [X] T019 Update frontend components to use ChatKit SDK in frontend/src/components/
- [X] T020 Update ChatPage to use ChatKit service in frontend/src/pages/ChatPage.jsx

**Checkpoint**: ChatKit SDK infrastructure ready

---

## Phase 5: User Story 1 - Ask Questions About Book Content (Priority: P1) 🎯 MVP

**Goal**: Users can ask questions about the book content and receive accurate answers based on the book's information.

**Independent Test**: Can be fully tested by asking a question and verifying that the response is based on retrieved context from the book content.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US1] Contract test for POST /chatkit in backend/tests/contract/test_chat.py
- [X] T022 [P] [US1] Integration test for full-book question answering in backend/tests/integration/test_rag_flow.py

### Implementation for User Story 1

- [X] T023 [P] [US1] Create Message model in backend/src/models/database_models.py
- [X] T024 [P] [US1] Create Document and DocumentChunk models in backend/src/models/database_models.py
- [X] T025 [US1] Update RAG service to use Agent SDK in backend/src/services/rag_service.py (depends on T012)
- [X] T026 [US1] Implement embedding service in backend/src/services/embedding_service.py (depends on T006)
- [X] T027 [US1] Implement LLM service with Gemini in backend/src/services/llm_service.py (depends on T025)
- [X] T028 [US1] Implement document service in backend/src/services/document_service.py
- [X] T029 [US1] Implement chatkit endpoint with Agent processing in backend/main.py (depends on T025-T027)
- [X] T030 [US1] Add validation and error handling for RAG flow in backend/main.py
- [X] T031 [US1] Add logging for RAG operations in backend/src/services/rag_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 6: User Story 2 - Select Specific Text for Context (Priority: P2)

**Goal**: Users can select specific text from the book and ask questions that are answered only based on that selected text.

**Independent Test**: Can be fully tested by selecting text, asking a question, and verifying the response is based only on the selected text.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T032 [P] [US2] Contract test for document upload in backend/tests/contract/test_documents.py
- [X] T033 [P] [US2] Integration test for selected-text mode in backend/tests/integration/test_selected_text.py

### Implementation for User Story 2

- [X] T034 [P] [US2] Create document processing functionality in backend/src/services/document_service.py
- [X] T035 [US2] Implement dual-mode logic in RAG service with Agent in backend/src/services/rag_service.py
- [X] T036 [US2] Implement document endpoints in backend/main.py (depends on T034)
- [X] T037 [US2] Add selected text handling to chat endpoint in backend/main.py (depends on T035)
- [X] T038 [US2] Update session service to track mode settings in backend/src/services/session_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 7: User Story 3 - Maintain Conversation History (Priority: P3)

**Goal**: Users can have a coherent conversation with the chatbot that remembers context across multiple exchanges.

**Independent Test**: Can be fully tested by having a multi-turn conversation and verifying that the system remembers context from previous exchanges.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T039 [P] [US3] Contract test for session endpoints in backend/tests/contract/test_sessions.py
- [X] T040 [P] [US3] Integration test for conversation history in backend/tests/integration/test_conversation_history.py

### Implementation for User Story 3

- [X] T041 [P] [US3] Create session endpoints in backend/main.py (depends on T012)
- [X] T042 [US3] Implement session-based memory in RAG service with Agent in backend/src/services/rag_service.py (depends on T011, T023)
- [X] T043 [US3] Update message storage to maintain conversation context in backend/src/services/session_service.py
- [X] T044 [US3] Add session listing and management to frontend/src/services/chatkit.js

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Frontend Implementation with ChatKit

**Goal**: Implement the ChatKit-style UI for user interaction using proper ChatKit SDK

### Tests for Frontend Implementation (OPTIONAL - only if tests requested) ⚠️

- [X] T045 [P] Frontend unit tests for chat components in frontend/tests/unit/test_chat_components.jsx
- [ ] T046 [P] Frontend integration tests for chat flow in frontend/tests/integration/

### Implementation for Frontend

- [X] T047 Create ChatPage component using ChatKit SDK in frontend/src/pages/ChatPage.jsx
- [X] T048 Create ChatInterface component in frontend/src/components/ChatInterface.jsx
- [X] T049 Create Message component in frontend/src/components/Message.jsx
- [X] T050 Create DocumentSelector component in frontend/src/components/DocumentSelector.jsx
- [X] T051 Create SessionManager component in frontend/src/components/SessionManager.jsx
- [X] T052 Implement API service for frontend in frontend/src/services/api.js
- [X] T053 Connect frontend to backend API endpoints via ChatKit SDK

---

## Phase 9: API Modernization

**Goal**: Update API endpoints to follow best practices

- [X] T054 Update /api/chat endpoint to use session_id parameter pattern in backend/main.py
- [X] T055 Add conditional debug endpoints that only work in DEBUG_MODE in backend/main.py
- [X] T056 Update frontend to use new endpoint patterns in frontend/src/services/api.js
- [X] T057 Document streaming response mechanism via Server-Sent Events (SSE) in README.md

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Web Content Integration

**Goal**: Integrate web content from sitemap into the RAG system using Cohere embeddings and Qdrant storage

### New Feature Tasks

- [ ] T058 Create sitemap parser to extract URLs from https://bushraturk.github.io/my-website/sitemap.xml in backend/src/utils/sitemap_parser.py
- [ ] T059 Implement web scraper to fetch content from sitemap URLs in backend/src/utils/web_scraper.py
- [ ] T060 Integrate Cohere API for text embedding with provided API key in backend/src/services/embedding_service.py
- [ ] T061 Connect to Qdrant database using provided URL and API key in backend/src/core/vector_store.py
- [ ] T062 Store embeddings with proper metadata in Qdrant in backend/src/services/document_service.py
- [ ] T063 Create sitemap embedding pipeline script in backend/src/utils/sitemap_embedder.py
- [ ] T064 Create requirements.txt with all necessary dependencies for web scraping and embedding in backend/requirements_sitemap.txt
- [ ] T065 Create .env.example file with API key placeholders in backend/.env.example
- [ ] T066 Create comprehensive README.md with setup instructions for sitemap integration in backend/docs/sitemap_integration.md
- [ ] T067 Implement error handling and progress tracking in sitemap embedding pipeline in backend/src/utils/sitemap_embedder.py

---

## Phase N+1: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T068 [P] Documentation updates (TASKS_AND_DOCS.md) in docs/
- [X] T069 Code cleanup and refactoring
- [X] T070 [P] Additional unit tests in backend/tests/unit/ and frontend/tests/unit/
- [X] T071 Performance optimization across all stories
- [X] T072 Security hardening (rate limiting, input validation)
- [X] T073 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **Agent SDK (Phase 3)**: Depends on Foundational phase completion
- **ChatKit SDK (Phase 4)**: Depends on Agent SDK completion
- **User Stories (Phase 5+)**: All depend on Agent/ChatKit SDK completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Frontend Phase**: Depends on backend API endpoints being available
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Agent/ChatKit SDK - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Agent/ChatKit SDK - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Agent/ChatKit SDK - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Agent/ChatKit phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /chatkit in backend/tests/contract/test_chat.py"
Task: "Integration test for full-book question answering in backend/tests/integration/test_rag_flow.py"

# Launch all models for User Story 1 together:
Task: "Create Message model in backend/src/models/database_models.py"
Task: "Create Document and DocumentChunk models in backend/src/models/database_models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: Agent SDK Implementation
4. Complete Phase 4: ChatKit SDK Implementation
5. Complete Phase 5: User Story 1
6. **STOP and VALIDATE**: Test User Story 1 independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational + Agent/ChatKit → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational + Agent/ChatKit together
2. Once Agent/ChatKit is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence