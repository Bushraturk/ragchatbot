from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from typing import Optional

from dotenv import load_dotenv
import os

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rag_chatbot.db")  # Use SQLite by default

# Use String type for IDs to support ChatKit-style IDs (thread_xxx, message_xxx)
# This works with both SQLite and PostgreSQL
ID_TYPE = String(100)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database Models
class ThreadDB(Base):
    __tablename__ = "threads"

    id = Column(ID_TYPE, primary_key=True)  # ChatKit-style IDs like "thread_abc123"
    created_at = Column(DateTime, default=func.current_timestamp())
    metadata_ = Column("metadata", JSON)  # Using metadata_ to avoid conflict with SQLAlchemy's metadata

class ThreadItemDB(Base):
    __tablename__ = "thread_items"

    id = Column(ID_TYPE, primary_key=True)  # ChatKit-style IDs like "message_xyz789"
    thread_id = Column(ID_TYPE, ForeignKey("threads.id"))
    type = Column(String(20))  # 'message' or other types
    role = Column(String(20))  # 'user', 'assistant', 'system'
    content = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationship to thread
    thread = relationship("ThreadDB", back_populates="items")

ThreadDB.items = relationship("ThreadItemDB", order_by=ThreadItemDB.created_at, back_populates="thread")

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)