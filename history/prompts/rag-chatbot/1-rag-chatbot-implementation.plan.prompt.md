---
id: 1
title: RAG Chatbot Implementation Plan
stage: plan
date: 2025-12-16
surface: agent
model: gpt-4
feature: rag-chatbot
branch: main
user: DELL
command: /sp.plan
labels: [plan,rag,chatbot,architecture]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/rag-chatbot/plan.md
  - specs/rag-chatbot/research.md
  - specs/rag-chatbot/data-model.md
  - specs/rag-chatbot/contracts/api-contracts.md
  - specs/rag-chatbot/quickstart.md
tests:
  - none
---

## Prompt

```
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType qwen`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.


/sp.plan

Design the full implementation plan for the Integrated RAG Chatbot feature.

Context:
- Backend and frontend must be separated
- Backend: FastAPI-based agent service using Gemini as the LLM
- Embeddings: Cohere
- Vector store: Qdrant Cloud (Free Tier)
- SQL database: Neon Serverless Postgres
- Frontend: ChatKit-style chat UI
- The chatbot will be embedded into an existing Docusaurus-based book in a later phase

Requirements:
- Strict RAG-first architecture (no direct LLM answers)
- Dual-mode support:
  1) Full-book question answering
  2) User-selected text only (must override global context)
- Session-based chat memory
- Clean architecture and production-ready design

Instructions:
- Follow the IMPL_PLAN template strictly
- Mark unknowns as NEEDS CLARIFICATION
- Resolve all unknowns in Phase 0 research
- Produce planning artifacts only (no implementation code)
- Stop after Phase 2 planning and report generated artifacts

## Response snapshot

I have successfully created the implementation plan for the Integrated RAG Chatbot feature. Here's a summary of the artifacts generated:

**Plan Summary**:
- Created comprehensive implementation plan (plan.md) following the template structure
- Identified all technical context details and resolved "NEEDS CLARIFICATION" items

**Phase 0 - Research**:
- Created research.md with decisions and rationale for all technology choices
- Resolved all "NEEDS CLARIFICATION" items with thorough research

**Phase 1 - Design & Contracts**:
- Created data-model.md with all core entities, relationships, and validation rules
- Created API contracts (contracts/api-contracts.md) for all required endpoints
- Created quickstart.md guide for development setup and usage
- Updated agent context file (QWEN.md) with new technology stack information

**Artifacts generated**:
- specs/rag-chatbot/plan.md - Implementation plan
- specs/rag-chatbot/research.md - Research findings
- specs/rag-chatbot/data-model.md - Data model specification
- specs/rag-chatbot/contracts/api-contracts.md - API contracts
- specs/rag-chatbot/quickstart.md - Quickstart guide
- QWEN.md - Updated agent context

All constitutional principles from the RAGChatBot constitution have been verified and satisfied in the implementation plan.

## Outcome

- ✅ Impact: Complete implementation plan created for the RAG chatbot with all required artifacts
- 🧪 Tests: none
- 📁 Files: Multiple design artifacts created (plan, research, data model, contracts, quickstart guide)
- 🔁 Next prompts: Implementation can now proceed based on these planning artifacts
- 🧠 Reflection: The plan successfully captures all requirements for the RAG chatbot, including dual-mode operation and clean architecture.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): not applicable
- Prompt variant (if applicable): not applicable
- Next experiment (smallest change to try): begin implementation based on the planning artifacts