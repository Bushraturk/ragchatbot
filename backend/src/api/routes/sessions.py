from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

from src.services.session_service import SessionService

router = APIRouter()

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    metadata: dict

class SessionsResponse(BaseModel):
    sessions: List[SessionResponse]

@router.get("/sessions", response_model=SessionsResponse)
async def list_sessions():
    try:
        service = SessionService()
        sessions = service.list_sessions()
        return SessionsResponse(sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        service = SessionService()
        success = service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))