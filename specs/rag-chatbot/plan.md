# Implementation Plan: Integrated RAG Chatbot

**Branch**: `###-rag-chatbot` | **Date**: 2025-12-16 | **Spec**: [link to spec]
**Input**: Feature specification from `/specs/rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a RAG (Retrieval-Augmented Generation) chatbot that allows users to ask questions about book content. The system will use FastAPI backend with Gemini LLM, Cohere embeddings, Qdrant vector store, and Neon Postgres for chat history. The solution will support dual-mode operation: full-book question answering and user-selected text mode.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Cohere, Qdrant, Neon Postgres, Google Generative AI SDK, React
**Storage**: PostgreSQL for chat history, Qdrant Cloud for vector storage
**Testing**: pytest with unit, integration, and contract tests
**Target Platform**: Linux server (backend), cross-platform web frontend
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <5s response time, handle 100 concurrent users
**Constraints**: <200ms p95 retrieval time, rate limits for API calls, comply with book content licensing
**Scale/Scope**: Single book initially, extensible for multiple books, 5000+ pages support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on RAGChatBot Constitution:
- Clean Architecture First: ✅ Implemented layered architecture with clear separation (models, services, API, core)
- RAG-Driven Answers: ✅ All responses will be based on retrieved context before generation
- Test-First Approach: ✅ Tests will be implemented following TDD methodology
- Context Integrity: ✅ Responses will cite retrieved content and avoid hallucinations
- Production-Ready Scalability: ✅ Using production-ready technologies (FastAPI, Neon, Qdrant)
- Dual Mode Implementation: ✅ Both full-book and user-selected text modes implemented

**Post-Design Re-evaluation**: All constitutional principles satisfied with clean architecture implementation.

## Project Structure

### Documentation (this feature)

```text
specs/rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── entities.py
│   │   └── database_models.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── document_service.py
│   │   └── session_service.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── sessions.py
│   │   └── middleware/
│   │       └── auth.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── vector_store.py
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── contract/
│
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx
│   │   ├── Message.jsx
│   │   ├── DocumentSelector.jsx
│   │   └── SessionManager.jsx
│   ├── services/
│   │   └── api.js
│   ├── pages/
│   │   └── ChatPage.jsx
│   └── utils/
│       └── constants.js
├── public/
└── tests/
    └── unit/
```

**Structure Decision**: Web application with separate backend (FastAPI) and frontend (React with ChatKit-style UI) to allow independent scaling and maintenance.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |