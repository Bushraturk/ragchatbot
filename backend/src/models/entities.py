from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Base models for API requests and responses (Pydantic models)

class SessionBase(BaseModel):
    metadata: Optional[Dict[str, Any]] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    session_id: uuid.UUID
    sender_type: str  # 'USER' or 'ASSISTANT'
    content: str
    context_references: Optional[List[Dict[str, Any]]] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: uuid.UUID
    timestamp: datetime

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    content: str
    source_type: Optional[str] = "BOOK_FULL"  # 'BOOK_FULL' or 'BOOK_SELECTION'
    metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentChunkBase(BaseModel):
    document_id: uuid.UUID
    content: str
    chunk_order: int
    metadata: Optional[Dict[str, Any]] = None

class DocumentChunkCreate(DocumentChunkBase):
    embedding: Optional[str] = None  # String representation of vector

class DocumentChunk(DocumentChunkBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True