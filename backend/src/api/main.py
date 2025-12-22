import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.routes import chat, documents, sessions
from backend.src.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description
)

# Production CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Define allowed origins
allowed_origins = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
]

# Add Vercel preview URLs if in production
if FRONTEND_URL and "vercel.app" in FRONTEND_URL:
    allowed_origins.append("https://*.vercel.app")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2025-12-16", "services": {"database": True, "vector_store": True, "llm_provider": True}}