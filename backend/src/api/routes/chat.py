from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
import logging

from src.core.database import get_db
from src.services.rag_service import RAGService
from src.services.session_service import SessionService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    mode: Optional[str] = "full_book"  # 'full_book' or 'selected_text'
    selected_text: Optional[str] = None

class ContextReference(BaseModel):
    document_id: str
    chunk_id: str
    content_snippet: str
    similarity_score: float

class ChatResponse(BaseModel):
    session_id: str
    response: str
    context_references: List[ContextReference]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        # Validate the request
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if chat_request.mode not in ["full_book", "selected_text"]:
            raise HTTPException(status_code=400, detail="Mode must be either 'full_book' or 'selected_text'")

        if chat_request.mode == "selected_text" and (not chat_request.selected_text or not chat_request.selected_text.strip()):
            raise HTTPException(status_code=400, detail="Selected text is required for 'selected_text' mode")

        rag_service = RAGService()
        session_service = SessionService()

        # If no session_id provided, create a new session
        if not chat_request.session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Creating new session: {session_id}")
        else:
            session_id = chat_request.session_id
            # Verify session exists
            existing_session = session_service.get_session(session_id)
            if not existing_session:
                logger.warning(f"Session not found: {session_id}, creating new one")
                session_id = str(uuid.uuid4())

        logger.info(f"Processing chat request for session: {session_id}, mode: {chat_request.mode}")

        # Process the chat request using RAG service
        response, context_refs = rag_service.process_query(
            query=chat_request.message,
            mode=chat_request.mode,
            selected_text=chat_request.selected_text,
            thread_id=session_id
        )

        # Save the interaction to session
        user_message_added = session_service.add_message_to_session(
            session_id=session_id,
            message=chat_request.message,
            sender_type="USER"
        )
        assistant_message_added = session_service.add_message_to_session(
            session_id=session_id,
            message=response,
            sender_type="ASSISTANT",
            context_references=context_refs
        )

        if not user_message_added or not assistant_message_added:
            logger.error(f"Failed to save messages to session: {session_id}")

        logger.info(f"Chat response generated successfully for session: {session_id}")

        return ChatResponse(
            session_id=session_id,
            response=response,
            context_references=context_refs,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    try:
        session_service = SessionService()
        history = session_service.get_session_messages(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/health")
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={"database": True, "vector_store": True, "llm_provider": True}
    )