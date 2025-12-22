import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Serve static files (frontend) if available
static_dir = os.path.join(os.path.dirname(__file__), "../../static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve index.html for all routes (SPA support)
        if full_path.startswith("api/") or full_path == "health":
            return {"error": "Not found"}
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend not built"}