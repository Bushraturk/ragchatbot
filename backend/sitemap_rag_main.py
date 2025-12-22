"""
A RAG ChatKit Gemini implementation that uses fetched sitemap data for responses.
This implementation does not require external vector stores or API keys for initialization.
"""

import os
import uuid
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List
from dataclasses import dataclass, field
import asyncio

import cohere
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from enum import Enum

# Load .env from project root
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# Load the scraped sitemap data
def load_sitemap_data():
    sitemap_file = ROOT_DIR / "scraped_sitemap_data.json"
    if sitemap_file.exists():
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"Sitemap data file not found: {sitemap_file}")
        return []

SITEMAP_DATA = load_sitemap_data()

class ItemType(str, Enum):
    MESSAGE = "message"
    THREAD = "thread"


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ContentPart:
    type: str
    text: str = ""


@dataclass
class MessageContent:
    id: str
    type: str
    content: List[ContentPart]


@dataclass
class ThreadItem:
    id: str
    type: ItemType
    content: List[MessageContent]
    role: Role
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ThreadMetadata:
    id: str
    created_at: datetime
    metadata: Dict[str, Any]


class SitemapRAGService:
    """
    A simple RAG service that uses the scraped sitemap data to find relevant content
    and responds based on that content.
    """
    def __init__(self, sitemap_data: List[Dict[str, Any]]):
        self.sitemap_data = sitemap_data
        self.content_index = self._build_content_index()
    
    def _build_content_index(self):
        """
        Create a simple index to enable fast searching.
        In a real implementation, this would use vector embeddings.
        """
        index = []
        for item in self.sitemap_data:
            index.append({
                'url': item.get('url', ''),
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'description': item.get('description', '')
            })
        return index
    
    def find_relevant_content(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        """
        Find content relevant to the query using simple keyword matching.
        In a real implementation, this would use vector similarity search.
        """
        # Simple keyword-based search for demonstration
        query_lower = query.lower()
        results = []
        
        for item in self.content_index:
            score = 0
            # Check for query terms in the title
            if query_lower in item['title'].lower():
                score += 3
            # Check for query terms in the content
            if query_lower in item['content'].lower():
                score += 2
            # Check for partial matches
            for word in query_lower.split():
                if word in item['title'].lower():
                    score += 1
                if word in item['content'].lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'url': item['url'],
                    'title': item['title'],
                    'content': item['content'][:1000] + "..." if len(item['content']) > 1000 else item['content'],  # Truncate if too long
                    'score': score
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def generate_response(self, query: str, context_items: List[Dict[str, str]]) -> str:
        """
        Generate a response based on the query and context items.
        """
        if not context_items:
            return "I couldn't find any relevant information in the provided documents. Please ask a question related to the Physical AI & Humanoid Robotics textbook."
        
        # Combine context items into a single context string
        context_parts = []
        for item in context_items:
            content = item.get('content', '')
            if content:
                context_parts.append(f"Title: {item.get('title', '')}\nURL: {item.get('url', '')}\nContent: {content}\n---")
        
        combined_context = "\n".join(context_parts)
        
        # Create a prompt that includes the context and query
        system_prompt = f"""
        You are a helpful assistant for the Physical AI & Humanoid Robotics textbook. 
        Answer the user's question based ONLY on the information provided in the context below.
        If the context does not contain relevant information to answer the question, 
        please respond with "I couldn't find relevant information about that in the textbook."

        Context:
        {combined_context}
        """
        
        # For this implementation, we'll generate a simple response based on the context
        # In a production system, you would send this to a real LLM
        
        # Check if the query is asking about content in our context
        query_lower = query.lower()
        
        # Find the most relevant content based on the query
        relevant_content = ""
        best_score = 0
        for item in context_items:
            content_lower = item['content'].lower()
            score = sum(1 for word in query_lower.split() if word in content_lower)
            if score > best_score:
                best_score = score
                relevant_content = item['content']
        
        if relevant_content:
            # If we found relevant content, return a summary of that content
            # In a real system, this would be a properly generated response from an LLM
            if len(relevant_content) > 300:
                response = f"Based on the textbook:\n\n{relevant_content[:300]}..."
            else:
                response = f"Based on the textbook:\n\n{relevant_content}"
        else:
            response = "I couldn't find relevant information about that in the textbook."
        
        return response


class SimpleStore:
    """
    A simple in-memory store for chat threads.
    """
    def __init__(self):
        self.threads: Dict[str, List[ThreadItem]] = {}
        self.thread_metadata: Dict[str, ThreadMetadata] = {}
    
    def generate_thread_id(self) -> str:
        return f"thread_{uuid.uuid4().hex[:12]}"
    
    def generate_item_id(self) -> str:
        return f"item_{uuid.uuid4().hex[:12]}"
    
    def add_thread(self, thread_id: str, metadata: Dict[str, Any] = None):
        if metadata is None:
            metadata = {}
        self.thread_metadata[thread_id] = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(timezone.utc),
            metadata=metadata
        )
        self.threads[thread_id] = []
    
    def add_message(self, thread_id: str, role: Role, content: str):
        if thread_id not in self.threads:
            self.add_thread(thread_id)
        
        content_part = ContentPart(type="text", text=content)
        message_content = [MessageContent(
            id=self.generate_item_id(),
            type="text",
            content=[content_part]
        )]
        
        item = ThreadItem(
            id=self.generate_item_id(),
            type=ItemType.MESSAGE,
            content=message_content,
            role=role
        )
        
        self.threads[thread_id].append(item)
    
    def get_thread_messages(self, thread_id: str) -> List[ThreadItem]:
        return self.threads.get(thread_id, [])


# Initialize services
rag_service = SitemapRAGService(SITEMAP_DATA)
store = SimpleStore()


# Initialize FastAPI app
app = FastAPI(title="Sitemap RAG ChatKit Gemini")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    try:
        body = await request.json()
        
        # Extract parameters from the request
        message = body.get("message", "")
        thread_id = body.get("thread_id", store.generate_thread_id())
        mode = body.get("mode", "full_book")
        selected_text = body.get("selected_text", None)
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Add user message to the thread
        store.add_message(thread_id, Role.USER, message)
        
        # Find relevant content from the sitemap data
        if mode == "selected_text" and selected_text:
            # In selected text mode, we only use the selected text as context
            context_items = [{
                'url': 'user_selection',
                'title': 'Selected Text',
                'content': selected_text,
                'score': 10
            }]
        else:
            # In full book mode, search the sitemap data
            context_items = rag_service.find_relevant_content(message, limit=3)
        
        # Generate response based on context
        response = rag_service.generate_response(message, context_items)
        
        # Add assistant response to the thread
        store.add_message(thread_id, Role.ASSISTANT, response)
        
        # Stream the response back to the client
        async def event_generator():
            yield f"data: {response}\n\n"
            yield f"data: [DONE]\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/plain")
    
    except Exception as e:
        print(f"Error in chatkit endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "model": "sitemap-rag",
        "sitemap_data_loaded": len(SITEMAP_DATA) > 0,
        "items_count": len(SITEMAP_DATA)
    }


@app.get("/debug/threads")
async def debug_threads():
    """Debug endpoint to view all stored threads"""
    result = {}
    for thread_id, items in store.threads.items():
        item_data = []
        for item in items:
            content_text = ""
            if item.content:
                for content_part in item.content:
                    for part in content_part.content:
                        content_text += part.text
            item_data.append({
                "id": item.id,
                "role": item.role.value,
                "content": content_text[:100] + "..." if len(content_text) > 100 else content_text
            })
        result[thread_id] = {
            "items": item_data,
            "count": len(item_data)
        }
    return {"threads": result, "total_threads": len(result)}


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Sitemap RAG ChatKit server at http://localhost:8000")
    print(f"Loaded {len(SITEMAP_DATA)} items from sitemap data")
    uvicorn.run(app, host="0.0.0.0", port=8000)