<!-- SYNC IMPACT REPORT
- Version change: n/a → 1.0.0
- Added sections: All principles and sections as specified for RAGChatBot
- Templates requiring updates:
  - ✅ plan-template.md: Constitution Check aligns with new principles
  - ✅ spec-template.md: Requirements align with new principles
  - ✅ tasks-template.md: Task categorization reflects new principles
- Follow-up TODOs: none
-->
# RAGChatBot Constitution

## Core Principles

### Clean Architecture First
Every component follows clean architecture principles; Layers must be independently testable, with clear separation between presentation, domain, and infrastructure; Dependencies must flow inward toward business logic

### RAG-Driven Answers
All responses must be based on retrieved context from the book content; Direct LLM generation without retrieval is prohibited; The retrieval step is mandatory for all responses

### Test-First Approach (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced for all components including retrieval and generation pipelines

### Context Integrity
Responses must cite or reference retrieved content internally; Never hallucinate answers; If user asks outside the book scope, respond with 'Information not found in the book'

### Production-Ready Scalability
Design for modularity and scalability from the start; Leverage FastAPI for high-performance API serving; Vector storage optimized for low-latency retrieval

### Dual Mode Implementation
Support both full-book question answering and user-selected text mode; Selected-text mode must override global book context when active; Session-based memory maintained throughout conversations

## Technology Stack Requirements

Mandatory technology stack: OpenAI Agents SDK OR ChatKit SDK (agent-based architecture), FastAPI backend, Neon Serverless PostgreSQL (chat history + metadata), Qdrant Cloud (Free Tier) for vector storage, RAG pipeline for semantic search, Book content as the only knowledge source

## Development Workflow

Implement step-by-step approach: Data ingestion → Vector indexing → Retrieval pipeline → Generation pipeline → API endpoints → Frontend integration; Maintain clear folder structure and API documentation throughout development

## Governance
All pull requests must verify compliance with RAG-first principle; Code reviews must check for proper retrieval before generation; Complexity must be justified with performance benchmarks

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
