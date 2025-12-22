# RAG Chatbot Implementation Documentation

**Last Updated**: December 2024

## System Architecture

The RAG (Retrieval-Augmented Generation) chatbot system answers questions based on specific document content (Physical AI & Robotics course) rather than general knowledge.

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + ChatKit)               │
│  - @openai/chatkit-react v1.4.0                            │
│  - Vite + TypeScript                                        │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP/SSE
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + ChatKit SDK)            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.py - Unified Entry Point                       │  │
│  │  - RAGChatKitServer (ChatKitServer subclass)         │  │
│  │  - MemoryStore (thread/message storage)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         RAG Service (src/services/rag_service.py)    │  │
│  │  - Query Processing                                  │  │
│  │  - Context Retrieval from Qdrant                     │  │
│  │  - Response Generation via Gemini                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                ↙              ↓              ↘             │
│  ┌─────────────────┐ ┌──────────────────┐ ┌─────────────┐ │
│  │ Embedding       │ │ LLM Service      │ │ Vector      │ │
│  │ Service         │ │ (Gemini 2.0)     │ │ Store       │ │
│  │ (Cohere)        │ │                  │ │ (Qdrant)    │ │
│  └─────────────────┘ └──────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
           ↓                    ↓                    ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Cohere API       │ │ Google Gemini    │ │ Qdrant Cloud     │
│ embed-english-   │ │ gemini-2.0-flash │ │ 172 vectors      │
│ v3.0             │ │                  │ │ (78 docs)        │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Core Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React 18 + ChatKit SDK | Chat UI with streaming |
| Backend | FastAPI + openai-chatkit | API server with ChatKit protocol |
| LLM | Google Gemini 2.0 Flash | Response generation |
| Embeddings | Cohere embed-english-v3.0 | Document/query vectorization |
| Vector DB | Qdrant Cloud | Semantic search (172 vectors, 78 docs) |
| Database | Neon PostgreSQL | Conversation history (optional) |

---

## Current Implementation Status

### Completed Tasks

| Task | Status | Details |
|------|--------|---------|
| Sitemap scraping | ✅ Done | 47 URLs from bushraturk.github.io |
| Embedding generation | ✅ Done | All 78 documents embedded with Cohere |
| Qdrant storage | ✅ Done | 172 vectors stored in cloud |
| Sitemap re-fetch (Dec 22) | ✅ Done | 78 pages scraped from updated sitemap |
| ChatKit SDK integration | ✅ Done | Using openai-chatkit Python SDK |
| RAG pipeline | ✅ Done | Full query→embed→search→generate flow |
| Unified main.py | ✅ Done | Single entry point, deleted main_working.py |
| Environment config | ✅ Done | All API keys configured correctly |

### RAG Pipeline Flow
```
User Query
    ↓
Cohere Embedding (embed-english-v3.0)
    ↓
Qdrant Vector Search (top 5 results)
    ↓
Context Assembly
    ↓
Gemini LLM Generation (with context)
    ↓
Streaming Response to Frontend
```

---

## File Structure

```
backend/
├── main.py                      # Unified entry point (ChatKit + RAG)
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
├── generate_embeddings.py       # Script to embed sitemap data
├── scraped_sitemap_data.json    # 47 scraped documents
├── src/
│   ├── core/
│   │   ├── config.py            # Settings management
│   │   ├── vector_store.py      # Qdrant client wrapper
│   │   └── database.py          # PostgreSQL connection
│   ├── services/
│   │   ├── rag_service.py       # RAG orchestration
│   │   ├── embedding_service.py # Cohere embeddings
│   │   └── llm_service.py       # Gemini integration
│   └── api/
│       └── routes/              # Additional API routes
│
frontend/
├── src/
│   ├── App.tsx                  # Main React component with ChatKit
│   └── main.tsx                 # Entry point
├── package.json
└── vite.config.ts
```

---

## Configuration

### Environment Variables (.env)

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://...

# Qdrant Vector Database
QDRANT_URL=https://1ee7b94a-6dbd-4206-be0c-1445f5605150.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# AI Model API Keys
GEMINI_API_KEY=AIzaSy...
COHERE_API_KEY=4Mu1aq...

# Model Configuration
LLM_MODEL=gemini/gemini-2.0-flash
EMBEDDING_MODEL=embed-english-v3.0
```

### Key Configuration Notes
- **No quotes** around values in .env file
- **No leading spaces** before variable names
- Qdrant API key must be the **JWT token** (not cluster ID)
- LLM_MODEL uses **litellm format**: `gemini/gemini-2.0-flash`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chatkit` | POST | Main ChatKit endpoint (handles all SDK requests) |
| `/health` | GET | Health check with service status |
| `/debug/threads` | GET | View stored conversation threads |
| `/qdrant-data` | GET | Check Qdrant connection and document count |

### ChatKit Request Flow
The ChatKit SDK sends requests in a specific binary/JSON protocol. The backend uses `openai-chatkit` Python SDK to handle:
1. Thread creation/loading
2. Message storage
3. Response streaming (SSE)

---

## Key Changes Made

### 1. Unified main.py
**Before**: Two files (main.py, main_working.py) with different implementations
**After**: Single `main.py` using official ChatKit SDK

```python
# Key classes in main.py
class MemoryStore(Store[dict]):     # Thread/message storage
class RAGChatKitServer(ChatKitServer[dict]):  # RAG + ChatKit integration
```

### 2. Fixed Qdrant Integration
**Issue**: Qdrant Cloud requires UUID format for point IDs
**Fix**: Added `_generate_uuid()` method in vector_store.py

```python
def _generate_uuid(self, doc_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))
```

### 3. Environment Variables
**Fixed Issues**:
- Removed leading space from `GEMINI_API_KEY`
- Removed quotes from all values
- Updated Qdrant API key to correct JWT token

### 4. Generated Embeddings
**Script**: `generate_embeddings.py`
**Result**: 78 documents embedded and stored in Qdrant (172 total vectors)

---

## Running the Application

### Backend
```bash
cd backend
python main.py
```

Output:
```
============================================================
RAG ChatBot Server (ChatKit SDK)
============================================================
Model: gemini/gemini-2.0-flash
Qdrant: Configured
Cohere: Configured
Gemini: Configured
============================================================
Server: http://localhost:8000
API Docs: http://localhost:8000/docs
============================================================
```

### Frontend
```bash
cd frontend
npm run dev
```

### Re-generate Embeddings (if needed)
```bash
cd backend
python generate_embeddings.py
```

---

## Troubleshooting

### Issue: 400 Bad Request on /chatkit
**Cause**: ChatKit SDK sends specific protocol, not simple JSON
**Solution**: Use `openai-chatkit` Python SDK (already implemented)

### Issue: Qdrant ID format error
**Cause**: Qdrant Cloud requires UUID or integer IDs
**Solution**: Use `uuid.uuid5()` to generate valid UUIDs from string IDs

### Issue: Empty responses from RAG
**Cause**: No embeddings in Qdrant
**Solution**: Run `python generate_embeddings.py`

### Issue: API key not working
**Check**:
1. No quotes in .env values
2. No leading/trailing spaces
3. Correct API key format (Qdrant uses JWT)

---

## Dependencies

### Backend (requirements.txt)
```
fastapi
uvicorn
openai-chatkit
qdrant-client
cohere
litellm
python-dotenv
pydantic-settings
```

### Frontend (package.json)
```json
{
  "@openai/chatkit-react": "^1.4.0",
  "react": "^18.3.1",
  "vite": "^6.0.0"
}
```

---

## Content Indexed

The system has indexed **78 documents** (172 vectors) from the Physical AI & Robotics course:

**Sitemap URL**: `https://bushraturk.github.io/my-website/sitemap.xml`

| Module | Documents |
|--------|-----------|
| ROS 2 | Introduction, Week 1-2, Week 3, Labs, Quiz, Assignment, Conclusion |
| Gazebo/Unity | Introduction, Week 4-5, Week 6, Labs, Quiz, Assignment, Conclusion |
| NVIDIA Isaac | Introduction, Week 7-8, Week 9, Labs, Quiz, Assignment, Conclusion |
| VLA | Introduction, Week 10-11, Week 12, Week 13, Labs, Quiz, Assignments, Final Project |
| Instructor Guide | Assessment Rubrics, Hardware, Intro, Lesson Plans, Offline Access, Pedagogical Notes, Troubleshooting |
| Tutorials | Create Document, Create Page, Blog Post, Deploy, Markdown Features, Manage Versions, Translate |
| Guides | Accessibility, AI Integration, Deployment, Documentation, Internationalization, Performance Optimization, Testing Strategy |
| Translations | Adding Translations, Feature Migration, Process Guide, Validation Test |
| Other | Home, Conclusion, Hardware Guides, MDX Components, User Profile, Sign In/Up |

### Latest Data Fetch (December 22, 2024)
- **Pages Scraped**: 78
- **Embeddings Generated**: 78 (Cohere embed-english-v3.0)
- **Total Vectors in Qdrant**: 172
- **Vector Dimension**: 1024
- **Distance Metric**: Cosine

---

## Sample Queries

Try these questions with the chatbot:
- "What is ROS 2?"
- "Explain the NVIDIA Isaac module"
- "What are VLA models?"
- "How do I set up Gazebo simulation?"
- "What topics are covered in Week 1-2?"

---

## Future Improvements

- [ ] Persistent conversation storage (PostgreSQL)
- [ ] Multi-user support with authentication
- [ ] Document chunking for better retrieval
- [ ] Hybrid search (keyword + semantic)
- [ ] Response caching for common queries
