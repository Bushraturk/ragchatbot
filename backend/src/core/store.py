import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from dataclasses import dataclass, field

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.src.core.database import SessionLocal, ThreadDB, ThreadItemDB

load_dotenv()


@dataclass
class Page:
    data: List[Any]
    has_more: bool
    after: str = None


class Store:
    """Database-backed store implementation using Neon Postgres"""

    def __init__(self) -> None:
        # We'll use a session factory rather than a single session to handle concurrency
        pass

    def _get_db_session(self) -> Session:
        return SessionLocal()

    def generate_thread_id(self, context: Dict) -> str:
        return f"thread_{uuid.uuid4().hex[:12]}"

    def generate_item_id(self, item_type: str, thread_id: str, context: Dict) -> str:
        new_id = f"{item_type}_{uuid.uuid4().hex[:12]}"
        print(f"[Store] generate_item_id: type={item_type}, id={new_id}")
        return new_id

    async def load_thread(self, thread_id: str, context: Dict) -> Dict:
        db = self._get_db_session()
        try:
            thread = db.query(ThreadDB).filter(ThreadDB.id == thread_id).first()
            if thread:
                # Convert to dict format that matches original ThreadMetadata
                return {
                    "id": str(thread.id),
                    "created_at": thread.created_at,
                    "metadata": thread.metadata_
                }
            else:
                # Create new thread
                new_thread = ThreadDB(
                    id=thread_id,
                    metadata_={}
                )
                db.add(new_thread)
                db.commit()
                
                return {
                    "id": str(new_thread.id),
                    "created_at": new_thread.created_at,
                    "metadata": new_thread.metadata_
                }
        finally:
            db.close()

    async def save_thread(self, thread_data: Dict, context: Dict) -> None:
        db = self._get_db_session()
        try:
            thread = db.query(ThreadDB).filter(ThreadDB.id == thread_data["id"]).first()
            if thread:
                thread.metadata_ = thread_data.get("metadata", {})
                db.commit()
            else:
                new_thread = ThreadDB(
                    id=thread_data["id"],
                    metadata_=thread_data.get("metadata", {}),
                    created_at=thread_data.get("created_at", datetime.now(timezone.utc))
                )
                db.add(new_thread)
                db.commit()
        finally:
            db.close()

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: Dict,
    ) -> Page:
        db = self._get_db_session()
        try:
            query = db.query(ThreadItemDB).filter(ThreadItemDB.thread_id == thread_id)
            
            # Apply ordering
            if order == "desc":
                query = query.order_by(ThreadItemDB.created_at.desc())
            else:
                query = query.order_by(ThreadItemDB.created_at.asc())
            
            # Apply pagination
            if after:
                after_item = db.query(ThreadItemDB).filter(ThreadItemDB.id == after).first()
                if after_item:
                    query = query.filter(ThreadItemDB.created_at > after_item.created_at)
            
            items = query.limit(limit + 1).all()  # +1 to check if there are more items
            
            has_more = len(items) > limit
            result_items = items[:limit] if has_more else items
            
            # Convert to expected format
            converted_items = []
            for item in result_items:
                # Process content to extract text from the complex structure
                content_text = ""
                if item.content:
                    import json
                    try:
                        content_obj = json.loads(item.content)
                        if isinstance(content_obj, list) and len(content_obj) > 0:
                            # Get the text from the first content part
                            first_content = content_obj[0]
                            if isinstance(first_content, dict) and "content" in first_content:
                                for part in first_content["content"]:
                                    if isinstance(part, dict) and "text" in part:
                                        content_text += part["text"]
                    except (json.JSONDecodeError, KeyError, IndexError):
                        # Fallback to using content as-is if parsing fails
                        content_text = item.content

                converted_item = {
                    "id": str(item.id),
                    "thread_id": str(item.thread_id),
                    "type": item.type,
                    "role": item.role,
                    "content": content_text,
                    "created_at": item.created_at.isoformat() if hasattr(item.created_at, 'isoformat') else str(item.created_at)
                }
                converted_items.append(converted_item)
            
            after_cursor = str(items[limit].id) if has_more and len(items) > limit else None
            
            print(f"[Store] Returning {len(converted_items)} items for thread {thread_id}, has_more={has_more}")
            
            return Page(
                data=converted_items,
                has_more=has_more,
                after=after_cursor
            )
        finally:
            db.close()

    async def add_thread_item(self, thread_id: str, item_data: Dict, context: Dict) -> None:
        db = self._get_db_session()
        try:
            # Check if item already exists
            existing_item = db.query(ThreadItemDB).filter(ThreadItemDB.id == item_data["id"]).first()
            
            if existing_item:
                # Update existing item
                existing_item.type = item_data["type"]
                existing_item.role = item_data["role"]
                existing_item.content = item_data["content"]
                db.commit()
                print(f"[Store] Updated existing item {item_data['id']}")
            else:
                # Create new item
                new_item = ThreadItemDB(
                    id=item_data["id"],
                    thread_id=thread_id,
                    type=item_data["type"],
                    role=item_data["role"],
                    content=item_data["content"]
                )
                db.add(new_item)
                db.commit()
                
                print(f"[Store] Added NEW item {item_data['id']}")
        finally:
            db.close()

    async def save_item(self, thread_id: str, item_data: Dict, context: Dict) -> None:
        await self.add_thread_item(thread_id, item_data, context)

    async def load_item(self, thread_id: str, item_id: str, context: Dict) -> Dict:
        db = self._get_db_session()
        try:
            item = db.query(ThreadItemDB).filter(
                ThreadItemDB.thread_id == thread_id,
                ThreadItemDB.id == item_id
            ).first()
            
            if item:
                return {
                    "id": str(item.id),
                    "thread_id": str(item.thread_id),
                    "type": item.type,
                    "role": item.role,
                    "content": item.content,
                    "created_at": item.created_at
                }
            else:
                raise ValueError(f"Item {item_id} not found")
        finally:
            db.close()

    async def delete_thread_item(self, thread_id: str, item_id: str, context: Dict) -> None:
        db = self._get_db_session()
        try:
            item = db.query(ThreadItemDB).filter(
                ThreadItemDB.thread_id == thread_id,
                ThreadItemDB.id == item_id
            ).first()
            
            if item:
                db.delete(item)
                db.commit()
        finally:
            db.close()

    async def load_threads(self, limit: int, after: str | None, order: str, context: Dict) -> Page:
        db = self._get_db_session()
        try:
            query = db.query(ThreadDB)
            
            # Apply ordering
            if order == "desc":
                query = query.order_by(ThreadDB.created_at.desc())
            else:
                query = query.order_by(ThreadDB.created_at.asc())
            
            # Apply pagination
            if after:
                after_thread = db.query(ThreadDB).filter(ThreadDB.id == after).first()
                if after_thread:
                    query = query.filter(ThreadDB.created_at > after_thread.created_at)
            
            threads = query.limit(limit + 1).all()  # +1 to check if there are more items
            
            has_more = len(threads) > limit
            result_threads = threads[:limit] if has_more else threads
            
            # Convert to expected format
            converted_threads = []
            for thread in result_threads:
                converted_thread = {
                    "id": str(thread.id),
                    "created_at": thread.created_at.isoformat() if hasattr(thread.created_at, 'isoformat') else str(thread.created_at),
                    "metadata": thread.metadata_
                }
                converted_threads.append(converted_thread)
            
            after_cursor = str(threads[limit].id) if has_more and len(threads) > limit else None
            
            return Page(
                data=converted_threads,
                has_more=has_more,
                after=after_cursor
            )
        finally:
            db.close()

    async def delete_thread(self, thread_id: str, context: Dict) -> None:
        db = self._get_db_session()
        try:
            # Delete associated items first (due to foreign key constraint)
            db.query(ThreadItemDB).filter(ThreadItemDB.thread_id == thread_id).delete()
            
            # Delete thread
            thread = db.query(ThreadDB).filter(ThreadDB.id == thread_id).first()
            if thread:
                db.delete(thread)
            
            db.commit()
        finally:
            db.close()