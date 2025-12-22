---
id: 1
title: Update RAGChatBot Constitution
stage: constitution
date: 2025-12-16
surface: agent
model: gpt-4
feature: ragchatbot
branch: main
user: DELL
command: /sp.constitution
labels: [constitution,rag,chatbot,architecture]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

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


/sp.constitution

You are an expert AI architect and full-stack engineer specializing in
Retrieval-Augmented Generation (RAG) systems, OpenAI Agents, and ChatKit SDK.

Your responsibility is to design, implement, and document an embedded RAG
chatbot for a published book.

SYSTEM PRINCIPLES:
- Follow clean architecture and production-grade practices
- Prefer clarity, modularity, and scalability
- Never hallucinate answers; rely strictly on retrieved context
- If relevant data is missing, respond with "Information not found in the book"

TECHNOLOGY STACK (MANDATORY):
- OpenAI Agents SDK OR ChatKit SDK (agent-based architecture)
- FastAPI backend
- Neon Serverless PostgreSQL (chat history + metadata)
- Qdrant Cloud (Free Tier) for vector storage
- RAG pipeline for semantic search
- Book content as the only knowledge source

CORE REQUIREMENTS:
1. Build a RAG chatbot that answers questions about the book content
2. Support **two modes**:
   a) Full-book question answering
   b) Answering questions **ONLY from user-selected text**
3. Retrieval must happen before generation (no direct LLM answers)
4. Selected-text mode must override global book context
5. Maintain session-based chat memory

BEHAVIOR RULES:
- Always retrieve relevant chunks before responding
- Cite or reference retrieved content internally
- Do NOT use external knowledge
- If user asks outside the book scope, politely refuse

OUTPUT EXPECTATION:
- Step-by-step implementation plan
- Clear folder structure
- API endpoint design
- Agent workflow explanation
- Minimal but complete code examples

FINAL GOAL:
A fully functional, embedded RAG chatbot that can be integrated
inside a published book website or app.

## Response snapshot

I have successfully updated the project constitution with the following details:

**New Version**: 1.0.0 (Initial version for RAGChatBot project)
**Bump Rationale**: This is an initial creation of the constitution for the RAGChatBot project, implementing the specific principles and requirements for the RAG system.

**Files Updated**:
- `.specify/memory/constitution.md` - fully updated with new content

**Constitution Principles**:
1. Clean Architecture First
2. RAG-Driven Answers
3. Test-First Approach (NON-NEGOTIABLE)
4. Context Integrity
5. Production-Ready Scalability
6. Dual Mode Implementation

**No files flagged for manual follow-up** - all templates are consistent with the new constitution.

**Suggested commit message**: `docs: add constitution for RAGChatBot project v1.0.0`

The constitution now properly reflects the requirements for the RAG chatbot system, emphasizing clean architecture, RAG-driven responses, test-first development, and context integrity as specified in the user requirements.

## Outcome

- ✅ Impact: Created new constitution for RAGChatBot project that reflects the specific requirements for RAG systems
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with new principles and requirements
- 🔁 Next prompts: Implementation and development of the RAG chatbot can now begin following the constitution guidelines
- 🧠 Reflection: The constitution successfully captures the essential principles for the RAGChatBot project, ensuring clean architecture, proper RAG implementation, and context integrity.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): not applicable
- Prompt variant (if applicable): not applicable
- Next experiment (smallest change to try): begin implementation of the RAG chatbot following the principles in the new constitution