---

description: "Task list for the RAG Chatbot implementation"
---

# Tasks: Integrated RAG Chatbot

**Input**: Design documents from `/specs/rag-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as specified in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume web app structure based on plan.md

<!--
  ============================================================================
  IMPORTANT: The tasks below are based on the actual design artifacts for the RAG Chatbot project
  ============================================================================

  The tasks are organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan with backend/ and frontend/ directories
- [X] T002 Initialize backend Python project with FastAPI dependencies in backend/requirements.txt
- [X] T003 Initialize frontend React project with required dependencies in frontend/package.json
- [X] T004 [P] Configure linting and formatting tools for both backend (black, ruff) and frontend (ESLint, Prettier)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

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

## Phase 3: User Story 1 - Ask Questions About Book Content (Priority: P1) 🎯 MVP

**Goal**: Users can ask questions about the book content and receive accurate answers based on the book's information.

**Independent Test**: Can be fully tested by asking a question and verifying that the response is based on retrieved context from the book content.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Contract test for POST /api/chat in backend/tests/contract/test_chat.py
- [X] T014 [P] [US1] Integration test for full-book question answering in backend/tests/integration/test_rag_flow.py

### Implementation for User Story 1

- [X] T015 [P] [US1] Create Message model in backend/src/models/database_models.py
- [X] T016 [P] [US1] Create Document and DocumentChunk models in backend/src/models/database_models.py
- [X] T017 [US1] Implement RAG service in backend/src/services/rag_service.py (depends on T012)
- [X] T018 [US1] Implement embedding service in backend/src/services/embedding_service.py (depends on T006)
- [X] T019 [US1] Implement LLM service with Gemini in backend/src/services/llm_service.py (depends on T017)
- [X] T020 [US1] Implement document service in backend/src/services/document_service.py
- [X] T021 [US1] Implement chat endpoint in backend/src/api/routes/chat.py (depends on T017-T019)
- [X] T022 [US1] Add validation and error handling for RAG flow in backend/src/api/routes/chat.py
- [X] T023 [US1] Add logging for RAG operations in backend/src/services/rag_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Select Specific Text for Context (Priority: P2)

**Goal**: Users can select specific text from the book and ask questions that are answered only based on that selected text.

**Independent Test**: Can be fully tested by selecting text, asking a question, and verifying the response is based only on the selected text.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T024 [P] [US2] Contract test for document upload in backend/tests/contract/test_documents.py
- [X] T025 [P] [US2] Integration test for selected-text mode in backend/tests/integration/test_selected_text.py

### Implementation for User Story 2

- [X] T026 [P] [US2] Create document processing functionality in backend/src/services/document_service.py
- [X] T027 [US2] Implement dual-mode logic in RAG service in backend/src/services/rag_service.py
- [X] T028 [US2] Implement document endpoints in backend/src/api/routes/documents.py (depends on T026)
- [X] T029 [US2] Add selected text handling to chat endpoint in backend/src/api/routes/chat.py (depends on T027)
- [X] T030 [US2] Update session service to track mode settings in backend/src/services/session_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Maintain Conversation History (Priority: P3)

**Goal**: Users can have a coherent conversation with the chatbot that remembers context across multiple exchanges.

**Independent Test**: Can be fully tested by having a multi-turn conversation and verifying that the system remembers context from previous exchanges.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T031 [P] [US3] Contract test for session endpoints in backend/tests/contract/test_sessions.py
- [X] T032 [P] [US3] Integration test for conversation history in backend/tests/integration/test_conversation_history.py

### Implementation for User Story 3

- [X] T033 [P] [US3] Create session endpoints in backend/src/api/routes/sessions.py (depends on T012)
- [X] T034 [US3] Implement session-based memory in RAG service in backend/src/services/rag_service.py (depends on T011, T015)
- [X] T035 [US3] Update message storage to maintain conversation context in backend/src/services/session_service.py
- [X] T036 [US3] Add session listing and management to frontend/src/services/api.js

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Frontend Implementation

**Goal**: Implement the ChatKit-style UI for user interaction

### Tests for Frontend Implementation (OPTIONAL - only if tests requested) ⚠️

- [X] T037 [P] Frontend unit tests for chat components in frontend/tests/unit/test_chat_components.jsx
- [ ] T038 [P] Frontend integration tests for chat flow in frontend/tests/integration/

### Implementation for Frontend

- [X] T039 Create ChatPage component in frontend/src/pages/ChatPage.jsx
- [X] T040 Create ChatInterface component in frontend/src/components/ChatInterface.jsx
- [X] T041 Create Message component in frontend/src/components/Message.jsx
- [X] T042 Create DocumentSelector component in frontend/src/components/DocumentSelector.jsx
- [X] T043 Create SessionManager component in frontend/src/components/SessionManager.jsx
- [X] T044 Implement API service for frontend in frontend/src/services/api.js
- [X] T045 Connect frontend to backend API endpoints

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Web Content Integration

**Goal**: Integrate web content from sitemap into the RAG system using Cohere embeddings and Qdrant storage

### New Feature Tasks

- [ ] T052 Create sitemap parser to extract URLs from https://bushraturk.github.io/my-website/sitemap.xml in backend/src/utils/sitemap_parser.py
- [ ] T053 Implement web scraper to fetch content from sitemap URLs in backend/src/utils/web_scraper.py
- [ ] T054 Integrate Cohere API for text embedding with provided API key in backend/src/services/embedding_service.py
- [ ] T055 Connect to Qdrant database using provided URL and API key in backend/src/core/vector_store.py
- [ ] T056 Store embeddings with proper metadata in Qdrant in backend/src/services/document_service.py
- [ ] T057 Create sitemap embedding pipeline script in backend/src/utils/sitemap_embedder.py
- [ ] T058 Create requirements.txt with all necessary dependencies for web scraping and embedding in backend/requirements_sitemap.txt
- [ ] T059 Create .env.example file with API key placeholders in backend/.env.example
- [ ] T060 Create comprehensive README.md with setup instructions for sitemap integration in backend/docs/sitemap_integration.md
- [ ] T061 Implement error handling and progress tracking in sitemap embedding pipeline in backend/src/utils/sitemap_embedder.py

---

## Phase N+1: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T062 [P] Documentation updates in docs/
- [ ] T063 Code cleanup and refactoring
- [ ] T064 Performance optimization across all stories
- [ ] T065 [P] Additional unit tests in backend/tests/unit/ and frontend/tests/unit/
- [ ] T066 Security hardening (rate limiting, input validation)
- [ ] T067 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Frontend Phase**: Depends on backend API endpoints being available
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /api/chat in backend/tests/contract/test_chat.py"
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
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Phase N: Agent SDK and ChatKit SDK Integration

**Goal**: Integrate Agent SDK architecture and ChatKit SDK for proper chat functionality

### New Feature Tasks

- [X] T062 Implement base Agent classes in backend/src/core/agent_base.py
- [X] T063 Create RAG Tool for agent integration in backend/src/services/rag_tool.py
- [X] T064 Implement RAG Agent with Agent SDK patterns in backend/src/agents/rag_agent.py
- [X] T065 Integrate Agent SDK with existing RAG service in backend/src/services/rag_service.py
- [X] T066 Create ChatKit service in frontend/src/services/chatkit.js
- [X] T067 Update API endpoints to follow ChatKit patterns in backend/main.py
- [X] T068 Update frontend components to use ChatKit SDK in frontend/src/components/
- [X] T069 Update ChatPage to use ChatKit service in frontend/src/pages/ChatPage.jsx
- [X] T070 Update /api/chat endpoint to use session_id parameter pattern in backend/main.py
- [X] T071 Add conditional debug endpoints that only work in DEBUG_MODE in backend/main.py
- [X] T072 Update frontend to use new endpoint patterns in frontend/src/services/api.js
- [X] T073 Document streaming response mechanism via Server-Sent Events (SSE) in README.md

---

## Phase N+1: Web Content Integration

**Goal**: Integrate web content from sitemap into the RAG system using Cohere embeddings and Qdrant storage

### New Feature Tasks

- [ ] T074 Create sitemap parser to extract URLs from https://bushraturk.github.io/my-website/sitemap.xml in backend/src/utils/sitemap_parser.py
- [ ] T075 Implement web scraper to fetch content from sitemap URLs in backend/src/utils/web_scraper.py
- [ ] T076 Integrate Cohere API for text embedding with provided API key in backend/src/services/embedding_service.py
- [ ] T077 Connect to Qdrant database using provided URL and API key in backend/src/core/vector_store.py
- [ ] T078 Store embeddings with proper metadata in Qdrant in backend/src/services/document_service.py
- [ ] T079 Create sitemap embedding pipeline script in backend/src/utils/sitemap_embedder.py
- [ ] T080 Create requirements.txt with all necessary dependencies for web scraping and embedding in backend/requirements_sitemap.txt
- [ ] T081 Create .env.example file with API key placeholders in backend/.env.example
- [ ] T082 Create comprehensive README.md with setup instructions for sitemap integration in backend/docs/sitemap_integration.md
- [ ] T083 Implement error handling and progress tracking in sitemap embedding pipeline in backend/src/utils/sitemap_embedder.py

---

## Phase N+2: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T084 [P] Documentation updates in docs/TASKS_AND_DOCS.md
- [X] T085 Code cleanup and refactoring
- [X] T086 [P] Additional unit tests in backend/tests/unit/ and frontend/tests/unit/
- [X] T087 Performance optimization across all stories
- [X] T088 [P] Additional unit tests in backend/tests/unit/ and frontend/tests/unit/
- [X] T089 Security hardening (rate limiting, input validation)
- [X] T090 Run quickstart.md validation
- [ ] T091 Remove non-working main.py file that has unavailable dependencies
- [ ] T092 Consolidate all requirements files into a single requirements.txt
- [ ] T093 Update main.py to use working implementation from main_working.py
- [ ] T094 Update documentation to reflect simplified project structure

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence