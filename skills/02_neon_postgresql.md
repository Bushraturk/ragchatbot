# Neon PostgreSQL Database

## Overview
Neon ek serverless PostgreSQL database hai jo cloud mein run hota hai. Ye free tier provide karta hai aur automatic scaling support karta hai.

## Setup

### 1. Neon Account Create Karo
1. [https://neon.tech](https://neon.tech) pe jao
2. Sign up karo (GitHub se easy hai)
3. New Project create karo
4. Connection string copy karo

### 2. Connection String Format
```
postgresql://username:password@ep-xxx-xxx-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 3. Environment Variable
```env
DATABASE_URL=postgresql://neondb_owner:your_password@ep-sparkling-cell-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## SQLAlchemy Integration

### Installation
```bash
pip install sqlalchemy psycopg2-binary
```

### Database Configuration
```python
# backend/src/core/database.py

from sqlalchemy import create_engine, Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fallback.db")

# Use String type for flexible IDs
ID_TYPE = String(100)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### Model Definition
```python
class ThreadDB(Base):
    __tablename__ = "threads"

    id = Column(ID_TYPE, primary_key=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    metadata_ = Column("metadata", JSON)

class ThreadItemDB(Base):
    __tablename__ = "thread_items"

    id = Column(ID_TYPE, primary_key=True)
    thread_id = Column(ID_TYPE, ForeignKey("threads.id"))
    type = Column(String(20))
    role = Column(String(20))
    content = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
```

## Common Mistakes & Solutions

### Mistake 1: UUID Type Mismatch
**Problem:** Neon mein UUID column banaya lekin application String IDs bhej rahi hai.

**Error:**
```
invalid input syntax for type uuid: "thread_abc123def456"
```

**Root Cause:** ChatKit SDK `thread_xxx` format IDs generate karta hai jo UUID nahi hai.

**Solution:** Tables ko VARCHAR type ke saath recreate karo:

```sql
-- Drop existing tables
DROP TABLE IF EXISTS thread_items CASCADE;
DROP TABLE IF EXISTS threads CASCADE;

-- Recreate with VARCHAR
CREATE TABLE threads (
    id VARCHAR(100) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE thread_items (
    id VARCHAR(100) PRIMARY KEY,
    thread_id VARCHAR(100) REFERENCES threads(id),
    type VARCHAR(20),
    role VARCHAR(20),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Mistake 2: Connection Timeout
**Problem:** Neon free tier mein connection idle hone pe close ho jata hai.

**Error:**
```
server closed the connection unexpectedly
```

**Solution:** Connection pooling use karo:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections after 30 minutes
)
```

### Mistake 3: SSL Required
**Problem:** Neon requires SSL connection.

**Error:**
```
SSL connection is required
```

**Solution:** Connection string mein `sslmode=require` add karo:

```
postgresql://user:pass@host/db?sslmode=require
```

### Mistake 4: SQLite Fallback Issue
**Problem:** Local development mein SQLite use ho raha hai instead of Neon.

**Solution:** Check karo ke `.env` file load ho rahi hai:

```python
from dotenv import load_dotenv
import os

# Load from correct path
load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Using database: {DATABASE_URL[:30]}...")  # Debug
```

## CRUD Operations

### Create
```python
db = SessionLocal()
new_thread = ThreadDB(id="thread_123", metadata_={"mode": "full_book"})
db.add(new_thread)
db.commit()
db.close()
```

### Read
```python
db = SessionLocal()
thread = db.query(ThreadDB).filter(ThreadDB.id == "thread_123").first()
db.close()
```

### Update
```python
db = SessionLocal()
thread = db.query(ThreadDB).filter(ThreadDB.id == "thread_123").first()
thread.metadata_ = {"mode": "selected_text"}
db.commit()
db.close()
```

### Delete
```python
db = SessionLocal()
db.query(ThreadItemDB).filter(ThreadItemDB.thread_id == "thread_123").delete()
db.query(ThreadDB).filter(ThreadDB.id == "thread_123").delete()
db.commit()
db.close()
```

## Checking Data in Neon Dashboard

1. Neon Console: [https://console.neon.tech](https://console.neon.tech)
2. Project select karo
3. "Tables" tab pe jao
4. `threads` aur `thread_items` tables dekho

## Python Script to Check Data
```python
from src.core.database import SessionLocal, ThreadDB, ThreadItemDB

db = SessionLocal()
threads = db.query(ThreadDB).all()
items = db.query(ThreadItemDB).all()

print(f"Threads: {len(threads)}")
print(f"Messages: {len(items)}")

for t in threads:
    print(f"  - {t.id}: {t.metadata_}")

db.close()
```

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/src/core/database.py` | Database models & connection |
| `backend/main.py` | DatabaseStore class for ChatKit |
| `backend/.env` | Connection string (not in git) |
| `backend/.env.example` | Template for connection string |

## Resources
- [Neon Documentation](https://neon.tech/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Neon Free Tier Limits](https://neon.tech/docs/introduction/plans)
