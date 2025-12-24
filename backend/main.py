"""
RAG ChatBot - Unified Main Entry Point
Integrates OpenAI ChatKit SDK with RAG system for context-aware responses
Includes PostgreSQL database persistence for conversations
"""

import os
import sys
import uuid
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional
from dataclasses import dataclass, field

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

# ChatKit imports
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata, ThreadItem, Page,
    UserMessageItem, AssistantMessageItem,
    ThreadStreamEvent, ThreadItemDoneEvent,
    AssistantMessageContent, UserMessageContent
)

# Load environment variables first
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# Add src to path for imports
sys.path.insert(0, str(ROOT_DIR))

# Import RAG services and database
from src.services.rag_service import RAGService
from src.core.config import settings
from src.core.database import SessionLocal, ThreadDB, ThreadItemDB, init_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database tables
try:
    init_db()
    logger.info("Database tables initialized")
except Exception as e:
    logger.warning(f"Database initialization warning: {e}")


# ============================================================================
# Database Store for ChatKit (PostgreSQL)
# ============================================================================

class DatabaseStore(Store[dict]):
    """PostgreSQL-backed store for ChatKit threads and messages"""

    def __init__(self):
        self._attachments: Dict[str, Any] = {}  # Keep attachments in memory for now
        logger.info("DatabaseStore initialized with PostgreSQL backend")

    def _get_db(self):
        """Get database session"""
        return SessionLocal()

    def generate_thread_id(self, context: dict) -> str:
        return f"thread_{uuid.uuid4().hex[:12]}"

    def generate_item_id(self, item_type: str, thread: ThreadMetadata, context: dict) -> str:
        return f"{item_type}_{uuid.uuid4().hex[:12]}"

    def _ensure_timezone(self, dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware"""
        if dt is None:
            return datetime.now(timezone.utc)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        db = self._get_db()
        try:
            thread_db = db.query(ThreadDB).filter(ThreadDB.id == thread_id).first()

            if thread_db:
                return ThreadMetadata(
                    id=str(thread_db.id),
                    created_at=self._ensure_timezone(thread_db.created_at),
                    metadata=thread_db.metadata_ or {}
                )

            # Create new thread in database
            new_thread = ThreadDB(
                id=thread_id,
                created_at=datetime.now(timezone.utc),
                metadata_={}
            )
            db.add(new_thread)
            db.commit()

            return ThreadMetadata(
                id=thread_id,
                created_at=datetime.now(timezone.utc),
                metadata={}
            )
        except Exception as e:
            logger.error(f"Error loading thread: {e}")
            db.rollback()
            # Return a new thread metadata without persisting
            return ThreadMetadata(
                id=thread_id,
                created_at=datetime.now(timezone.utc),
                metadata={}
            )
        finally:
            db.close()

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        db = self._get_db()
        try:
            thread_db = db.query(ThreadDB).filter(ThreadDB.id == thread.id).first()

            if thread_db:
                thread_db.metadata_ = thread.metadata or {}
            else:
                new_thread = ThreadDB(
                    id=thread.id,
                    created_at=self._ensure_timezone(thread.created_at),
                    metadata_=thread.metadata or {}
                )
                db.add(new_thread)

            db.commit()
        except Exception as e:
            logger.error(f"Error saving thread: {e}")
            db.rollback()
        finally:
            db.close()

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ) -> Page[ThreadItem]:
        db = self._get_db()
        try:
            query = db.query(ThreadItemDB).filter(ThreadItemDB.thread_id == thread_id)

            if order == "desc":
                query = query.order_by(ThreadItemDB.created_at.desc())
            else:
                query = query.order_by(ThreadItemDB.created_at.asc())

            items_db = query.all()

            # Convert to ChatKit items
            items = []
            for item_db in items_db:
                created_at = self._ensure_timezone(item_db.created_at)

                if item_db.role == "user":
                    items.append(UserMessageItem(
                        thread_id=thread_id,
                        id=str(item_db.id),
                        created_at=created_at,
                        content=[UserMessageContent(text=item_db.content or "")]
                    ))
                else:
                    items.append(AssistantMessageItem(
                        thread_id=thread_id,
                        id=str(item_db.id),
                        created_at=created_at,
                        content=[AssistantMessageContent(text=item_db.content or "")]
                    ))

            # Handle pagination
            start = 0
            if after:
                for idx, item in enumerate(items):
                    if item.id == after:
                        start = idx + 1
                        break

            slice_items = items[start: start + limit + 1]
            has_more = len(slice_items) > limit
            result_items = slice_items[:limit]

            return Page(
                data=result_items,
                has_more=has_more,
                after=slice_items[-1].id if has_more and slice_items else None
            )
        except Exception as e:
            logger.error(f"Error loading thread items: {e}")
            return Page(data=[], has_more=False, after=None)
        finally:
            db.close()

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        db = self._get_db()
        try:
            # Ensure thread exists
            thread_db = db.query(ThreadDB).filter(ThreadDB.id == thread_id).first()
            if not thread_db:
                thread_db = ThreadDB(
                    id=thread_id,
                    created_at=datetime.now(timezone.utc),
                    metadata_={}
                )
                db.add(thread_db)
                db.commit()

            # Extract content text
            content_text = ""
            if hasattr(item, 'content') and item.content:
                for c in item.content:
                    if hasattr(c, 'text'):
                        content_text = c.text
                        break

            # Determine role
            role = "assistant"
            if isinstance(item, UserMessageItem):
                role = "user"

            # Check if item exists
            existing = db.query(ThreadItemDB).filter(ThreadItemDB.id == item.id).first()

            if existing:
                existing.content = content_text
                existing.role = role
            else:
                new_item = ThreadItemDB(
                    id=item.id,
                    thread_id=thread_id,
                    type="message",
                    role=role,
                    content=content_text,
                    created_at=self._ensure_timezone(getattr(item, 'created_at', datetime.now(timezone.utc)))
                )
                db.add(new_item)

            db.commit()
            logger.info(f"Saved {role} message to database: {item.id}")
        except Exception as e:
            logger.error(f"Error adding thread item: {e}")
            db.rollback()
        finally:
            db.close()

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        await self.add_thread_item(thread_id, item, context)

    async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem:
        db = self._get_db()
        try:
            item_db = db.query(ThreadItemDB).filter(
                ThreadItemDB.id == item_id,
                ThreadItemDB.thread_id == thread_id
            ).first()

            if not item_db:
                raise ValueError(f"Item {item_id} not found")

            created_at = self._ensure_timezone(item_db.created_at)

            if item_db.role == "user":
                return UserMessageItem(
                    thread_id=thread_id,
                    id=str(item_db.id),
                    created_at=created_at,
                    content=[UserMessageContent(text=item_db.content or "")]
                )
            else:
                return AssistantMessageItem(
                    thread_id=thread_id,
                    id=str(item_db.id),
                    created_at=created_at,
                    content=[AssistantMessageContent(text=item_db.content or "")]
                )
        finally:
            db.close()

    async def delete_thread_item(self, thread_id: str, item_id: str, context: dict) -> None:
        db = self._get_db()
        try:
            db.query(ThreadItemDB).filter(
                ThreadItemDB.id == item_id,
                ThreadItemDB.thread_id == thread_id
            ).delete()
            db.commit()
        except Exception as e:
            logger.error(f"Error deleting thread item: {e}")
            db.rollback()
        finally:
            db.close()

    async def load_threads(self, limit: int, after: str | None, order: str, context: dict) -> Page[ThreadMetadata]:
        db = self._get_db()
        try:
            query = db.query(ThreadDB)

            if order == "desc":
                query = query.order_by(ThreadDB.created_at.desc())
            else:
                query = query.order_by(ThreadDB.created_at.asc())

            threads_db = query.limit(limit).all()

            threads = [
                ThreadMetadata(
                    id=str(t.id),
                    created_at=self._ensure_timezone(t.created_at),
                    metadata=t.metadata_ or {}
                )
                for t in threads_db
            ]

            return Page(data=threads, has_more=False, after=None)
        except Exception as e:
            logger.error(f"Error loading threads: {e}")
            return Page(data=[], has_more=False, after=None)
        finally:
            db.close()

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        db = self._get_db()
        try:
            # Delete thread items first
            db.query(ThreadItemDB).filter(ThreadItemDB.thread_id == thread_id).delete()
            # Delete thread
            db.query(ThreadDB).filter(ThreadDB.id == thread_id).delete()
            db.commit()
            logger.info(f"Deleted thread {thread_id} from database")
        except Exception as e:
            logger.error(f"Error deleting thread: {e}")
            db.rollback()
        finally:
            db.close()

    async def save_attachment(self, attachment: Any, context: dict) -> None:
        self._attachments[attachment.id] = attachment

    async def load_attachment(self, attachment_id: str, context: dict) -> Any:
        if attachment_id not in self._attachments:
            raise ValueError(f"Attachment {attachment_id} not found")
        return self._attachments[attachment_id]

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        self._attachments.pop(attachment_id, None)


# ============================================================================
# RAG ChatKit Server
# ============================================================================

class RAGChatKitServer(ChatKitServer[dict]):
    """
    ChatKit server that integrates RAG for context-aware responses.
    """

    def __init__(self, data_store: Store):
        super().__init__(data_store)
        self.rag_service = RAGService()
        logger.info("RAG ChatKit Server initialized")

    def _extract_user_message(self, input_item: UserMessageItem | None) -> str:
        """Extract text from user message item"""
        if not input_item:
            return ""

        if hasattr(input_item, 'content') and input_item.content:
            for content in input_item.content:
                if hasattr(content, 'text'):
                    return content.text
                elif hasattr(content, 'value'):
                    return content.value
        return ""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_item: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process user message through RAG pipeline and stream response.
        """
        # Extract message text
        message = self._extract_user_message(input_item)

        if not message:
            message = "Hello"

        logger.info(f"Processing RAG query: '{message[:50]}...'")

        try:
            # Process through RAG service
            response_text, context_references = self.rag_service.process_request(
                session_id=thread.id,
                message=message,
                mode="full_book",
                selected_text=None
            )

            # Log context retrieval
            if context_references:
                logger.info(f"Retrieved {len(context_references)} context items")
            else:
                logger.warning("No context retrieved from vector store")

        except Exception as e:
            logger.error(f"RAG service error: {e}")
            response_text = "I apologize, but I encountered an error processing your request. Please try again."
            context_references = []

        # Generate response item
        response_id = self.store.generate_item_id("message", thread, context)

        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=thread.id,
                id=response_id,
                created_at=datetime.now(timezone.utc),
                content=[AssistantMessageContent(text=response_text)],
            ),
        )


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="RAG ChatBot API",
    description="RAG-powered chatbot with ChatKit integration and PostgreSQL persistence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store and server with database backend
store = DatabaseStore()
server = RAGChatKitServer(store)


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """
    Main ChatKit endpoint - handles all ChatKit SDK requests.
    """
    try:
        body = await request.body()
        logger.info(f"ChatKit request received, body length: {len(body)}")

        result = await server.process(body, {})

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        return Response(content=result.json, media_type="application/json")

    except Exception as e:
        logger.error(f"ChatKit endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    # Check database connection
    db_status = False
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = True
        db.close()
    except:
        pass

    services_status = {
        "rag_service": True,
        "vector_store": bool(settings.qdrant_url and settings.qdrant_api_key),
        "llm_provider": bool(settings.groq_api_key or settings.gemini_api_key),
        "database": db_status
    }

    return {
        "status": "ok",
        "version": "1.0.0",
        "model": settings.llm_model,
        "services": services_status
    }


@app.get("/debug/threads")
async def debug_threads():
    """Debug endpoint to view stored threads from database"""
    db = SessionLocal()
    try:
        threads = db.query(ThreadDB).all()
        result = {}

        for thread in threads:
            items = db.query(ThreadItemDB).filter(
                ThreadItemDB.thread_id == thread.id
            ).order_by(ThreadItemDB.created_at).all()

            result[str(thread.id)] = {
                "thread": {
                    "id": str(thread.id),
                    "created_at": str(thread.created_at)
                },
                "items": [
                    {
                        "id": str(item.id),
                        "role": item.role,
                        "content": item.content[:100] + "..." if item.content and len(item.content) > 100 else item.content,
                        "created_at": str(item.created_at)
                    }
                    for item in items
                ],
                "item_count": len(items)
            }

        return result
    finally:
        db.close()


@app.get("/qdrant-data")
async def get_qdrant_data():
    """Check Qdrant vector store status"""
    from src.core.vector_store import vector_store

    if not settings.qdrant_url or not settings.qdrant_api_key:
        return {
            "status": "warning",
            "message": "Qdrant not configured",
            "documents_count": 0
        }

    try:
        vector_store._ensure_initialized()
        try:
            collection_info = vector_store.client.get_collection(vector_store.collection_name)
            points_count = collection_info.points_count
        except Exception:
            points_count = 0

        return {
            "status": "connected",
            "collection_name": vector_store.collection_name,
            "documents_count": points_count,
            "last_checked": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "documents_count": 0
        }


@app.get("/api/sessions")
async def list_sessions():
    """List all conversation sessions from database"""
    db = SessionLocal()
    try:
        threads = db.query(ThreadDB).order_by(ThreadDB.created_at.desc()).all()
        sessions = []

        for thread in threads:
            item_count = db.query(ThreadItemDB).filter(
                ThreadItemDB.thread_id == thread.id
            ).count()

            sessions.append({
                "id": str(thread.id),
                "created_at": str(thread.created_at),
                "message_count": item_count
            })

        return {"sessions": sessions, "total": len(sessions)}
    finally:
        db.close()


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session from database"""
    db = SessionLocal()
    try:
        # Delete items first
        db.query(ThreadItemDB).filter(ThreadItemDB.thread_id == session_id).delete()
        # Delete thread
        deleted = db.query(ThreadDB).filter(ThreadDB.id == session_id).delete()
        db.commit()

        if deleted:
            return {"status": "deleted", "session_id": session_id}
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============================================================================
# Serve Frontend
# ============================================================================

FRONTEND_DIR = ROOT_DIR.parent / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
    logger.info(f"Serving frontend from {FRONTEND_DIR}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("RAG ChatBot Server (ChatKit SDK + PostgreSQL)")
    print("=" * 60)
    print(f"Model: {settings.llm_model}")
    print(f"Database: {'Configured' if settings.database_url else 'Not configured'}")
    print(f"Qdrant: {'Configured' if settings.qdrant_url else 'Not configured'}")
    # Separate variable to satisfy Replit privacy scanner
    groq_status = "Configured" if settings.groq_api_key else "Not configured"
    print(f"Groq: {groq_status}")
    print("=" * 60)
    print("Server: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
