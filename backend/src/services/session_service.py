from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel

from src.core.database import SessionLocal
from src.models.database_models import Session as SessionModel, Message as MessageModel
from src.models.entities import MessageCreate


class SessionService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def get_session(self, session_id: str):
        """Retrieve a session by ID"""
        try:
            session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
            return session
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None

    def create_session(self, metadata: dict = None):
        """Create a new session"""
        try:
            # Initialize with default mode if not specified
            if metadata is None:
                metadata = {}
            if "mode" not in metadata:
                metadata["mode"] = "full_book"  # Default mode

            db_session = SessionModel(metadata_=metadata)
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            return db_session.id
        except Exception as e:
            self.db.rollback()
            print(f"Error creating session: {e}")
            return None

    def update_session_mode(self, session_id: str, mode: str):
        """Update the mode for a session"""
        try:
            session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session:
                return False

            if session.metadata_ is None:
                session.metadata_ = {}
            session.metadata_["mode"] = mode

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error updating session mode: {e}")
            return False

    def get_session_mode(self, session_id: str) -> str:
        """Get the mode for a session"""
        try:
            session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session or not session.metadata_:
                return "full_book"  # Default mode

            return session.metadata_.get("mode", "full_book")
        except Exception as e:
            print(f"Error getting session mode: {e}")
            return "full_book"

    def add_message_to_session(self, session_id: str, message: str, sender_type: str, context_references: list = None):
        """Add a message to a session"""
        try:
            db_message = MessageModel(
                session_id=session_id,
                sender_type=sender_type,
                content=message,
                context_references=context_references or []
            )
            self.db.add(db_message)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error adding message to session: {e}")
            return False

    def get_session_messages(self, session_id: str) -> List[dict]:
        """Retrieve all messages for a session"""
        try:
            messages = (
                self.db.query(MessageModel)
                .filter(MessageModel.session_id == session_id)
                .order_by(MessageModel.timestamp.asc())
                .all()
            )
            
            return [
                {
                    "id": str(msg.id),
                    "sender_type": msg.sender_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "context_references": msg.context_references or []
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error retrieving session messages: {e}")
            return []

    def list_sessions(self):
        """List all sessions"""
        try:
            sessions = self.db.query(SessionModel).all()
            return [
                {
                    "id": str(session.id),
                    "title": f"Session {str(session.id)[:8]}",
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                    "metadata": session.metadata_ or {}
                }
                for session in sessions
            ]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its messages"""
        try:
            session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session:
                return False
            
            # Delete associated messages first
            self.db.query(MessageModel).filter(MessageModel.session_id == session_id).delete()
            
            # Then delete the session
            self.db.delete(session)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting session: {e}")
            return False