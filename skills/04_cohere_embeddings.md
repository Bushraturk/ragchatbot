# Cohere Embeddings

## Overview
Cohere ek AI company hai jo high-quality text embeddings provide karti hai. RAG applications mein documents aur queries ko vectors mein convert karne ke liye use hota hai.

## Setup

### 1. Cohere Account
1. [https://dashboard.cohere.com](https://dashboard.cohere.com) pe jao
2. Sign up karo
3. API Keys section mein jao
4. API key create aur copy karo

### 2. Environment Variable
```env
COHERE_API_KEY=your_cohere_api_key_here
EMBEDDING_MODEL=embed-english-v3.0
```

## Installation

```bash
pip install cohere
```

## Basic Implementation

### Embedding Service Class
```python
# backend/src/services/embedding_service.py

import cohere
from typing import List, Dict, Any

class EmbeddingService:
    def __init__(self):
        self.co = cohere.Client(settings.cohere_api_key)
        self.model = settings.embedding_model  # "embed-english-v3.0"

    def embed_text(self, text: str, input_type: str = "search_query") -> List[float]:
        """Single text embedding"""
        response = self.co.embed(
            texts=[text],
            model=self.model,
            input_type=input_type
        )
        return response.embeddings[0]

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Multiple documents embedding"""
        response = self.co.embed(
            texts=documents,
            model=self.model,
            input_type="search_document"
        )
        return response.embeddings
```

## Input Types

Cohere mein different input types hote hain:

| Input Type | Use Case |
|------------|----------|
| `search_document` | Documents store karte waqt |
| `search_query` | User query search karte waqt |
| `classification` | Text classification ke liye |
| `clustering` | Document clustering ke liye |

```python
# Document ko store karte waqt
doc_embedding = embedding_service.embed_text(
    "This is document content",
    input_type="search_document"
)

# User query search karte waqt
query_embedding = embedding_service.embed_text(
    "What is NVIDIA Isaac?",
    input_type="search_query"
)
```

## Common Mistakes & Solutions

### Mistake 1: Wrong Input Type
**Problem:** Documents `search_query` se embed kiye aur queries `search_document` se.

**Impact:** Poor search results, low similarity scores.

**Solution:** Correct input types use karo:

```python
# WRONG
doc_embedding = co.embed(texts=[doc], input_type="search_query")  # Wrong!
query_embedding = co.embed(texts=[query], input_type="search_document")  # Wrong!

# CORRECT
doc_embedding = co.embed(texts=[doc], input_type="search_document")
query_embedding = co.embed(texts=[query], input_type="search_query")
```

### Mistake 2: Rate Limiting
**Problem:** Too many requests in short time.

**Error:**
```
CohereAPIError: rate limit exceeded
```

**Solution:** Batch requests aur delays add karo:

```python
import time

def embed_documents_with_rate_limit(self, documents: List[str], batch_size: int = 96) -> List[List[float]]:
    all_embeddings = []

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]

        response = self.co.embed(
            texts=batch,
            model=self.model,
            input_type="search_document"
        )
        all_embeddings.extend(response.embeddings)

        # Rate limit ke liye wait
        if i + batch_size < len(documents):
            time.sleep(1)

    return all_embeddings
```

### Mistake 3: Empty or None Text
**Problem:** Empty string ya None value embed karne ki koshish.

**Error:**
```
CohereAPIError: texts cannot be empty
```

**Solution:** Input validate karo:

```python
def embed_text(self, text: str, input_type: str = "search_query") -> List[float]:
    if not text or not text.strip():
        # Return zero vector as fallback
        return [0.0] * 1024

    try:
        response = self.co.embed(
            texts=[text],
            model=self.model,
            input_type=input_type
        )
        return response.embeddings[0]
    except Exception as e:
        print(f"Embedding error: {e}")
        return [0.0] * 1024
```

### Mistake 4: API Key Not Loaded
**Problem:** API key environment se load nahi hui.

**Solution:**
```python
import os
from dotenv import load_dotenv

# Make sure .env is loaded
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in environment")

co = cohere.Client(api_key)
```

### Mistake 5: Model Name Typo
**Problem:** Wrong model name.

**Error:**
```
CohereAPIError: model not found
```

**Available Models:**
- `embed-english-v3.0` (recommended, 1024 dimensions)
- `embed-english-light-v3.0` (faster, 384 dimensions)
- `embed-multilingual-v3.0` (multilingual, 1024 dimensions)

## Web Content Embedding

```python
def embed_web_content(self, content: Dict[str, Any]) -> List[float]:
    """Embed web content with title for better context"""
    # Combine title and content
    text_to_embed = f"Title: {content.get('title', '')}\n\nContent: {content.get('content', '')}"

    return self.embed_text(text_to_embed, input_type="search_document")
```

## Embedding Dimensions

| Model | Dimensions | Best For |
|-------|------------|----------|
| embed-english-v3.0 | 1024 | High accuracy |
| embed-english-light-v3.0 | 384 | Speed & cost |
| embed-multilingual-v3.0 | 1024 | Multiple languages |

**Important:** Qdrant collection ka vector size embedding dimensions se match hona chahiye!

## Cost Optimization

```python
# Batch multiple texts together
texts = ["doc1", "doc2", "doc3", "doc4"]

# One API call for all (cheaper)
embeddings = co.embed(texts=texts, model="embed-english-v3.0", input_type="search_document")

# Instead of multiple calls (expensive)
# for text in texts:
#     embedding = co.embed(texts=[text], ...)
```

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/src/services/embedding_service.py` | EmbeddingService class |
| `backend/src/services/rag_service.py` | Uses embeddings for search |
| `backend/generate_embeddings.py` | Batch embedding script |

## Resources
- [Cohere Documentation](https://docs.cohere.com/)
- [Cohere Embed Guide](https://docs.cohere.com/docs/embeddings)
- [Cohere API Reference](https://docs.cohere.com/reference/embed)
