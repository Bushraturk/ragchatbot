# RAG (Retrieval-Augmented Generation) Pipeline

## Overview
RAG ek technique hai jismein LLM ko relevant context provide kiya jata hai database se, taake wo accurate answers de sake. Is project mein RAG pipeline Cohere embeddings + Qdrant + Gemini/Groq use karti hai.

## RAG Pipeline Flow

```
User Query
    |
    v
[1. Embed Query] --> Cohere API
    |
    v
[2. Search Vector DB] --> Qdrant
    |
    v
[3. Get Relevant Docs] --> Context
    |
    v
[4. Generate Response] --> Gemini/Groq LLM
    |
    v
Response to User
```

## Implementation

### RAG Service Class
```python
# backend/src/services/rag_service.py

class RAGService:
    def __init__(self):
        self.collection_name = "book_content"
        self.vector_store = vector_store
        self.co = cohere.Client(settings.cohere_api_key)

    def retrieve_context(self, query: str, limit: int = 5) -> List[Dict]:
        """Step 1 & 2: Embed query and search"""
        # Generate query embedding
        query_embedding = self.co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        ).embeddings[0]

        # Search in vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            limit=limit
        )

        return results

    def generate_response(self, query: str, context_items: List[Dict]) -> str:
        """Step 3 & 4: Build context and generate"""
        # Combine context
        context_parts = [item.get('content', '') for item in context_items]
        combined_context = "\n\n".join(context_parts)

        # Create prompt
        system_prompt = f"""
        Answer based ONLY on this context:
        {combined_context}

        If information not found, say "Information not found in the content".
        """

        # Generate with LLM
        response = litellm.completion(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.1
        )

        return response.choices[0].message.content

    def process_query(self, query: str) -> Tuple[str, List[Dict]]:
        """Full RAG pipeline"""
        context_items = self.retrieve_context(query)
        response = self.generate_response(query, context_items)
        return response, context_items
```

## Common Mistakes & Solutions

### Mistake 1: Empty Context
**Problem:** Vector store empty hai, koi context nahi milta.

**Symptom:** Response always "Information not found"

**Solution:** Check if data exists:

```python
# Debug: Check Qdrant data
collection_info = vector_store.client.get_collection("book_content")
print(f"Documents in Qdrant: {collection_info.points_count}")

# If 0, run the embedding pipeline first:
# python fetch_sitemap_data.py
# python generate_embeddings.py
```

### Mistake 2: Wrong Embedding Model Mismatch
**Problem:** Documents ek model se embed kiye, queries doosre se.

**Impact:** Similarity scores wrong, irrelevant results.

**Solution:** Same model use karo:

```python
# Document embedding (storage time)
doc_embedding = co.embed(
    texts=[doc],
    model="embed-english-v3.0",  # Same model
    input_type="search_document"
)

# Query embedding (search time)
query_embedding = co.embed(
    texts=[query],
    model="embed-english-v3.0",  # Same model
    input_type="search_query"
)
```

### Mistake 3: Context Too Large
**Problem:** Too much context causes LLM to lose focus or hit token limits.

**Solution:** Limit context and chunk properly:

```python
def retrieve_context(self, query: str, limit: int = 5, max_chars: int = 4000):
    results = self.vector_store.search(query_embedding, limit=limit)

    # Limit total context size
    context_items = []
    total_chars = 0

    for result in results:
        content = result.get('content', '')
        if total_chars + len(content) > max_chars:
            break
        context_items.append(result)
        total_chars += len(content)

    return context_items
```

### Mistake 4: No Conversation History
**Problem:** Multi-turn conversations mein context lose ho jata hai.

**Solution:** Chat history include karo:

```python
def generate_response(self, query: str, context_items: List[Dict],
                     chat_history: List[Dict] = None) -> str:
    messages = [{"role": "system", "content": system_prompt}]

    # Add chat history
    if chat_history:
        for msg in chat_history[-5:]:  # Last 5 messages
            messages.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })

    messages.append({"role": "user", "content": query})

    response = litellm.completion(model=settings.llm_model, messages=messages)
    return response.choices[0].message.content
```

### Mistake 5: System Prompt Too Restrictive
**Problem:** LLM "Information not found" kehta hai even when context exists.

**Cause:** System prompt bahut strict hai.

**Original (Too Strict):**
```python
system_prompt = """
Answer ONLY from context. If not found, say "Information not found".
"""
```

**Better:**
```python
system_prompt = """
You are a helpful assistant. Use the provided context to answer questions.
If the context contains relevant information, provide a detailed answer.
If the context doesn't contain the specific information, say so and offer
to help with related topics from the available content.

Context:
{context}
"""
```

### Mistake 6: Low Similarity Threshold
**Problem:** Irrelevant documents retrieve ho rahe hain.

**Solution:** Similarity threshold add karo:

```python
def retrieve_context(self, query: str, limit: int = 5,
                    min_score: float = 0.5) -> List[Dict]:
    results = self.vector_store.search(query_embedding, limit=limit)

    # Filter by similarity score
    filtered_results = [
        r for r in results
        if r.get('similarity_score', 0) >= min_score
    ]

    return filtered_results
```

## Dual Mode Support

### Full Book Mode
```python
if mode == "full_book":
    # Search entire vector database
    context_items = self.retrieve_context(query)
```

### Selected Text Mode
```python
if mode == "selected_text" and selected_text:
    # Use only user-selected text as context
    context_items = [{
        "content": selected_text,
        "metadata": {"source_type": "USER_SELECTION"},
        "similarity_score": 1.0
    }]
```

## LLM Configuration

### Using LiteLLM for Multiple Providers
```python
import litellm

# Gemini
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=messages
)

# Groq
response = litellm.completion(
    model="groq/llama-3.1-70b-versatile",
    messages=messages
)
```

### Environment Variables for LLM
```env
# Choose one
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key

# Model to use
LLM_MODEL=gemini/gemini-2.0-flash
```

## Performance Tips

1. **Cache Embeddings:** Same queries ke embeddings cache karo
2. **Batch Processing:** Multiple documents ek saath embed karo
3. **Limit Context:** 3-5 chunks usually enough hain
4. **Lower Temperature:** Factual answers ke liye 0.1-0.3 use karo

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/src/services/rag_service.py` | Main RAG logic |
| `backend/src/services/embedding_service.py` | Embedding generation |
| `backend/src/core/vector_store.py` | Vector search |
| `backend/main.py` | RAGChatKitServer integration |

## Resources
- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Cohere RAG Guide](https://docs.cohere.com/docs/retrieval-augmented-generation-rag)
