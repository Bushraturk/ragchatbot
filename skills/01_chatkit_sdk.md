# ChatKit SDK Integration

## Overview
ChatKit SDK OpenAI ka official SDK hai jo chat applications banane ke liye use hota hai. Ye streaming responses, thread management, aur message handling provide karta hai.

## Installation

```bash
pip install chatkit
```

## Key Concepts

### 1. ChatKitServer
Ye main server class hai jo requests handle karta hai.

```python
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata, ThreadItem, Page,
    UserMessageItem, AssistantMessageItem,
    AssistantMessageContent, UserMessageContent
)
```

### 2. Store Implementation
ChatKit ko ek Store chahiye jo threads aur messages save kare.

```python
class DatabaseStore(Store[dict]):
    """Custom store implementation"""

    def generate_thread_id(self, context: dict) -> str:
        return f"thread_{uuid.uuid4().hex[:12]}"

    def generate_item_id(self, item_type: str, thread: ThreadMetadata, context: dict) -> str:
        return f"{item_type}_{uuid.uuid4().hex[:12]}"

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        # Load thread from database
        pass

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        # Save thread to database
        pass

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        # Save message to database
        pass
```

### 3. Custom Server with RAG
```python
class RAGChatKitServer(ChatKitServer[dict]):
    def __init__(self, data_store: Store):
        super().__init__(data_store)
        self.rag_service = RAGService()

    async def respond(
        self,
        thread: ThreadMetadata,
        input_item: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Process message and generate response
        message = self._extract_user_message(input_item)
        response_text, _ = self.rag_service.process_request(
            session_id=thread.id,
            message=message,
            mode="full_book"
        )

        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=thread.id,
                id=self.store.generate_item_id("message", thread, context),
                content=[AssistantMessageContent(text=response_text)],
            ),
        )
```

## Common Mistakes & Solutions

### Mistake 1: UUID vs String ID Issue
**Problem:** ChatKit generates IDs like `thread_abc123` but PostgreSQL expects UUID format.

**Error:**
```
invalid input syntax for type uuid: "thread_abc123def456"
```

**Solution:** Database columns ko `VARCHAR(100)` use karo, UUID nahi.

```python
# WRONG - UUID type
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), primary_key=True)

# CORRECT - String type
ID_TYPE = String(100)
id = Column(ID_TYPE, primary_key=True)
```

### Mistake 2: Content Extraction
**Problem:** User message content complex structure mein hota hai.

**Solution:**
```python
def _extract_user_message(self, input_item: UserMessageItem | None) -> str:
    if not input_item:
        return ""

    if hasattr(input_item, 'content') and input_item.content:
        for content in input_item.content:
            if hasattr(content, 'text'):
                return content.text
    return ""
```

### Mistake 3: Timezone Issues
**Problem:** DateTime without timezone causes issues.

**Solution:**
```python
from datetime import datetime, timezone

def _ensure_timezone(self, dt: datetime) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()
store = DatabaseStore()
server = RAGChatKitServer(store)

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    body = await request.body()
    result = await server.process(body, {})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

## Frontend Integration

```javascript
// React frontend with ChatKit
import { useChat } from '@openai/chatkit-react';

function ChatComponent() {
    const { messages, sendMessage, isLoading } = useChat({
        endpoint: '/chatkit',
        threadId: 'thread_123'
    });

    return (
        <div>
            {messages.map(msg => (
                <div key={msg.id}>{msg.content}</div>
            ))}
        </div>
    );
}
```

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/main.py` | ChatKit server implementation |
| `frontend/src/services/chatkit.js` | Frontend ChatKit service |
| `frontend/src/pages/ChatPage.jsx` | Chat UI component |

## Resources
- [ChatKit Documentation](https://github.com/openai/chatkit)
- [ChatKit React SDK](https://www.npmjs.com/package/@openai/chatkit-react)
