# Qdrant Vector Store

## Overview
Qdrant ek vector database hai jo embeddings store karta hai aur similarity search enable karta hai. RAG applications mein documents ko search karne ke liye use hota hai.

## Setup

### 1. Qdrant Cloud Account
1. [https://cloud.qdrant.io](https://cloud.qdrant.io) pe jao
2. Sign up karo
3. Free cluster create karo
4. API key aur URL copy karo

### 2. Environment Variables
```env
QDRANT_URL=https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your_api_key_here
```

## Installation

```bash
pip install qdrant-client
```

## Basic Implementation

### Vector Store Class
```python
# backend/src/core/vector_store.py

from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

class VectorStore:
    def __init__(self):
        self.client = None
        self._initialized = False
        self.collection_name = "book_content"

    def _ensure_initialized(self):
        if not self._initialized:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                https=True
            )

            # Create collection if not exists
            try:
                self.client.get_collection(self.collection_name)
            except:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1024,  # Cohere embedding size
                        distance=models.Distance.COSINE
                    ),
                )

            self._initialized = True
```

### Adding Documents
```python
def add_document(self, doc_id: str, content: str, embedding: List[float], metadata: dict = None):
    self._ensure_initialized()

    # Generate valid UUID from string ID
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))

    self.client.upsert(
        collection_name=self.collection_name,
        points=[
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata,
                    "original_doc_id": doc_id
                }
            )
        ]
    )
```

### Searching Documents
```python
def search(self, query_embedding: List[float], limit: int = 10) -> List[dict]:
    self._ensure_initialized()

    results = self.client.query_points(
        collection_name=self.collection_name,
        query=query_embedding,
        limit=limit
    )

    return [
        {
            "id": point.id,
            "content": point.payload.get("content", ""),
            "metadata": point.payload.get("metadata", {}),
            "similarity_score": point.score
        }
        for point in results.points
    ]
```

## Common Mistakes & Solutions

### Mistake 1: Invalid Point ID Format
**Problem:** Qdrant requires UUID format for point IDs.

**Error:**
```
Invalid point id: "web_content_abc123"
```

**Solution:** String IDs ko UUID mein convert karo:

```python
def _generate_uuid(self, doc_id: str) -> str:
    """Generate valid UUID from any string ID"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))

# Usage
point_id = self._generate_uuid("web_content_abc123")
# Output: "550e8400-e29b-41d4-a716-446655440000"
```

### Mistake 2: Wrong Vector Size
**Problem:** Collection vector size doesn't match embedding size.

**Error:**
```
Vector size mismatch: expected 1024, got 768
```

**Solution:** Check embedding model's output size:

| Model | Size |
|-------|------|
| Cohere embed-english-v3.0 | 1024 |
| OpenAI text-embedding-ada-002 | 1536 |
| Sentence Transformers | 384/768 |

```python
# Create collection with correct size
self.client.create_collection(
    collection_name=self.collection_name,
    vectors_config=models.VectorParams(
        size=1024,  # Match your embedding model
        distance=models.Distance.COSINE
    ),
)
```

### Mistake 3: HTTPS Configuration
**Problem:** Qdrant Cloud requires HTTPS.

**Error:**
```
Connection refused / SSL error
```

**Solution:**
```python
self.client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
    https=True  # Important!
)
```

### Mistake 4: Empty Search Results
**Problem:** Search returns empty even with data.

**Possible Causes:**
1. Collection empty hai
2. Wrong collection name
3. Query embedding format wrong

**Debug Script:**
```python
# Check collection status
collection_info = client.get_collection("book_content")
print(f"Points count: {collection_info.points_count}")

# Check if data exists
points, _ = client.scroll(
    collection_name="book_content",
    limit=5
)
for p in points:
    print(f"ID: {p.id}, Content: {p.payload.get('content', '')[:50]}...")
```

### Mistake 5: API Key Not Set
**Problem:** Requests fail with authentication error.

**Solution:** Check environment variables:

```python
import os
print(f"QDRANT_URL: {os.getenv('QDRANT_URL', 'NOT SET')}")
print(f"QDRANT_API_KEY: {os.getenv('QDRANT_API_KEY', 'NOT SET')[:10]}...")
```

## Web Content Storage

```python
def add_web_content(self, doc_id: str, title: str, content: str,
                    embedding: List[float], url: str, metadata: dict = None):
    point_id = self._generate_uuid(doc_id)

    web_metadata = {
        "url": url,
        "title": title,
        "source_type": "web_content",
        "original_doc_id": doc_id,
        **(metadata or {})
    }

    self.client.upsert(
        collection_name=self.collection_name,
        points=[
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": web_metadata
                }
            )
        ]
    )
```

## Checking Qdrant Data

### Via Python
```python
from src.core.vector_store import vector_store

vector_store._ensure_initialized()
collection_info = vector_store.client.get_collection("book_content")
print(f"Total documents: {collection_info.points_count}")
```

### Via API Endpoint
```python
@app.get("/qdrant-data")
async def get_qdrant_data():
    collection_info = vector_store.client.get_collection("book_content")
    return {
        "status": "connected",
        "collection_name": "book_content",
        "documents_count": collection_info.points_count
    }
```

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/src/core/vector_store.py` | VectorStore class |
| `backend/src/services/rag_service.py` | Uses vector store for search |
| `backend/generate_embeddings.py` | Populates vector store |

## Resources
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Cloud Console](https://cloud.qdrant.io)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
