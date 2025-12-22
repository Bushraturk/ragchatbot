# Skills Documentation - RAG Chatbot Project

## Overview
Ye folder project mein use ki gayi saari technologies aur skills ki documentation contain karta hai. Har skill ki alag file hai jismein implementation details, common mistakes, aur solutions documented hain.

## Skills Index

| # | Skill | File | Description |
|---|-------|------|-------------|
| 01 | ChatKit SDK | [01_chatkit_sdk.md](./01_chatkit_sdk.md) | OpenAI ChatKit integration for chat UI |
| 02 | Neon PostgreSQL | [02_neon_postgresql.md](./02_neon_postgresql.md) | Serverless database for conversation storage |
| 03 | Qdrant Vector Store | [03_qdrant_vector_store.md](./03_qdrant_vector_store.md) | Vector database for semantic search |
| 04 | Cohere Embeddings | [04_cohere_embeddings.md](./04_cohere_embeddings.md) | Text to vector embeddings |
| 05 | RAG Pipeline | [05_rag_pipeline.md](./05_rag_pipeline.md) | Retrieval-Augmented Generation flow |
| 06 | Web Scraping | [06_web_scraping_sitemap.md](./06_web_scraping_sitemap.md) | Sitemap parsing & content scraping |
| 07 | LiteLLM | [07_litellm_multi_provider.md](./07_litellm_multi_provider.md) | Multi-provider LLM integration |

## Project Architecture

```
                                    +------------------+
                                    |    Frontend      |
                                    |  (React + ChatKit)|
                                    +--------+---------+
                                             |
                                             v
+------------------+              +----------+-----------+
|   Web Scraper    |              |      FastAPI         |
|  (Sitemap URLs)  |              |    (ChatKit Server)  |
+--------+---------+              +----------+-----------+
         |                                   |
         v                                   v
+--------+---------+              +----------+-----------+
|     Cohere       |              |     RAG Service      |
|   Embeddings     |<------------>|   (Query + Generate) |
+--------+---------+              +----------+-----------+
         |                                   |
         v                                   v
+--------+---------+              +----------+-----------+
|     Qdrant       |              |     LiteLLM         |
|  Vector Store    |              |  (Gemini/Groq)      |
+------------------+              +----------+-----------+
                                             |
                                             v
                                  +----------+-----------+
                                  |  Neon PostgreSQL     |
                                  |  (Conversations)     |
                                  +----------------------+
```

## Quick Start

### 1. Environment Setup
```bash
cd backend
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Populate Vector Store
```bash
python fetch_sitemap_data.py
python generate_embeddings.py
```

### 4. Start Server
```bash
python main.py
```

## Common Mistakes Summary

### Database Issues
| Problem | Solution | Skill File |
|---------|----------|------------|
| UUID type mismatch | Use VARCHAR(100) instead of UUID | [02_neon_postgresql.md](./02_neon_postgresql.md) |
| Connection timeout | Add connection pooling | [02_neon_postgresql.md](./02_neon_postgresql.md) |

### Vector Store Issues
| Problem | Solution | Skill File |
|---------|----------|------------|
| Invalid point ID | Convert string to UUID5 | [03_qdrant_vector_store.md](./03_qdrant_vector_store.md) |
| Vector size mismatch | Match embedding model dimensions | [03_qdrant_vector_store.md](./03_qdrant_vector_store.md) |

### Embedding Issues
| Problem | Solution | Skill File |
|---------|----------|------------|
| Wrong input type | Use search_document vs search_query correctly | [04_cohere_embeddings.md](./04_cohere_embeddings.md) |
| Rate limiting | Batch requests, add delays | [04_cohere_embeddings.md](./04_cohere_embeddings.md) |

### RAG Issues
| Problem | Solution | Skill File |
|---------|----------|------------|
| Empty responses | Check if vector store has data | [05_rag_pipeline.md](./05_rag_pipeline.md) |
| Irrelevant results | Add similarity threshold | [05_rag_pipeline.md](./05_rag_pipeline.md) |

### Scraping Issues
| Problem | Solution | Skill File |
|---------|----------|------------|
| 403 Forbidden | Add User-Agent header | [06_web_scraping_sitemap.md](./06_web_scraping_sitemap.md) |
| Rate limiting | Add delays between requests | [06_web_scraping_sitemap.md](./06_web_scraping_sitemap.md) |

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Vector Store
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=your_key

# Embeddings
COHERE_API_KEY=your_key
EMBEDDING_MODEL=embed-english-v3.0

# LLM
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
LLM_MODEL=gemini/gemini-2.0-flash
```

## File Structure

```
backend/
├── main.py                    # FastAPI + ChatKit Server
├── .env                       # Environment variables
├── .env.example              # Template
├── requirements.txt          # Dependencies
├── fetch_sitemap_data.py     # Scraping script
├── generate_embeddings.py    # Embedding script
└── src/
    ├── core/
    │   ├── config.py         # Settings
    │   ├── database.py       # SQLAlchemy models
    │   └── vector_store.py   # Qdrant client
    ├── services/
    │   ├── rag_service.py    # RAG pipeline
    │   ├── embedding_service.py
    │   └── document_service.py
    └── utils/
        ├── sitemap_parser.py
        ├── web_scraper.py
        └── sitemap_embedder.py
```

## Learning Path

1. **Start with**: [05_rag_pipeline.md](./05_rag_pipeline.md) - Understand the overall flow
2. **Then learn**: [04_cohere_embeddings.md](./04_cohere_embeddings.md) - How embeddings work
3. **Next**: [03_qdrant_vector_store.md](./03_qdrant_vector_store.md) - Vector storage
4. **Database**: [02_neon_postgresql.md](./02_neon_postgresql.md) - Conversation persistence
5. **Frontend**: [01_chatkit_sdk.md](./01_chatkit_sdk.md) - Chat interface
6. **Data ingestion**: [06_web_scraping_sitemap.md](./06_web_scraping_sitemap.md)
7. **LLM options**: [07_litellm_multi_provider.md](./07_litellm_multi_provider.md)

## Contributing

Agar koi nayi mistake mile ya solution dhundhein, toh relevant skill file mein add kar dein.
