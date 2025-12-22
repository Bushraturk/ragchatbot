# LiteLLM - Multi-Provider LLM Integration

## Overview
LiteLLM ek unified interface hai jo multiple LLM providers (OpenAI, Gemini, Groq, Anthropic, etc.) ko ek hi API se access karne deta hai. Is project mein Gemini aur Groq dono support hain.

## Installation

```bash
pip install litellm
```

## Basic Usage

```python
import litellm
from litellm import completion

# Gemini
response = completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Groq
response = completion(
    model="groq/llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

## Environment Variables

```env
# Gemini
GEMINI_API_KEY=your_gemini_api_key

# Groq
GROQ_API_KEY=your_groq_api_key

# Model to use
LLM_MODEL=gemini/gemini-2.0-flash
```

## Model Naming Convention

| Provider | Model Format |
|----------|--------------|
| OpenAI | `gpt-4`, `gpt-3.5-turbo` |
| Gemini | `gemini/gemini-2.0-flash`, `gemini/gemini-1.5-pro` |
| Groq | `groq/llama-3.1-70b-versatile`, `groq/mixtral-8x7b-32768` |
| Anthropic | `claude-3-opus-20240229` |

## Implementation in RAG Service

```python
# backend/src/services/rag_service.py

import litellm
from src.core.config import settings

class RAGService:
    def generate_response(self, query: str, context: str) -> str:
        system_prompt = f"""
        Answer based on this context:
        {context}
        """

        response = litellm.completion(
            model=settings.llm_model,  # From config
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.1
        )

        return response.choices[0].message.content
```

## Common Mistakes & Solutions

### Mistake 1: API Key Not Found
**Problem:** LiteLLM can't find the API key.

**Error:**
```
AuthenticationError: No API key provided
```

**Solution:** Environment variables properly set karo:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Manually set for LiteLLM
if os.getenv('GROQ_API_KEY'):
    os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
if os.getenv('GEMINI_API_KEY'):
    os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
```

### Mistake 2: Wrong Model Name Format
**Problem:** Model name format wrong hai.

**Error:**
```
BadRequestError: Invalid model name
```

**Solution:** Correct format use karo:

```python
# WRONG
model = "gemini-2.0-flash"  # Missing provider prefix

# CORRECT
model = "gemini/gemini-2.0-flash"  # With provider prefix
```

### Mistake 3: Rate Limit Exceeded
**Problem:** Too many requests.

**Error:**
```
RateLimitError: Rate limit exceeded
```

**Solution:** Retry logic add karo:

```python
import time

def generate_with_retry(self, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model=settings.llm_model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            if "rate" in str(e).lower() or "429" in str(e):
                wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                time.sleep(wait_time)
            else:
                raise e

    return "Error: Rate limit exceeded. Please try again later."
```

### Mistake 4: Context Too Long
**Problem:** Input tokens exceed model limit.

**Error:**
```
InvalidRequestError: This model's maximum context length is exceeded
```

**Solution:** Context truncate karo:

```python
def truncate_context(context: str, max_chars: int = 8000) -> str:
    """Truncate context to fit model limits"""
    if len(context) > max_chars:
        return context[:max_chars] + "..."
    return context
```

### Mistake 5: Streaming Not Working
**Problem:** Streaming response handle nahi ho raha.

**Solution:** Stream parameter use karo:

```python
# Non-streaming (simpler)
response = litellm.completion(
    model=settings.llm_model,
    messages=messages,
    stream=False
)

# Streaming
response = litellm.completion(
    model=settings.llm_model,
    messages=messages,
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Provider Comparison

| Provider | Speed | Cost | Quality |
|----------|-------|------|---------|
| Groq | Very Fast | Low | Good |
| Gemini | Fast | Low | Very Good |
| OpenAI GPT-4 | Medium | High | Excellent |
| Claude | Medium | Medium | Excellent |

## Fallback Strategy

```python
def generate_with_fallback(self, messages):
    """Try primary model, fallback to secondary"""
    primary_model = "gemini/gemini-2.0-flash"
    fallback_model = "groq/llama-3.1-70b-versatile"

    try:
        response = litellm.completion(
            model=primary_model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Primary model failed: {e}, trying fallback...")

        response = litellm.completion(
            model=fallback_model,
            messages=messages
        )
        return response.choices[0].message.content
```

## Temperature Settings

| Use Case | Temperature |
|----------|-------------|
| Factual/RAG | 0.1 - 0.3 |
| Balanced | 0.5 - 0.7 |
| Creative | 0.8 - 1.0 |

```python
response = litellm.completion(
    model=settings.llm_model,
    messages=messages,
    temperature=0.1  # Low for factual responses
)
```

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/src/services/rag_service.py` | Uses LiteLLM for generation |
| `backend/src/core/config.py` | LLM model configuration |
| `backend/.env` | API keys |

## Resources
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Supported Models](https://docs.litellm.ai/docs/providers)
- [Gemini API](https://ai.google.dev/docs)
- [Groq API](https://console.groq.com/docs)
