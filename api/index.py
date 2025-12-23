# Vercel serverless function entry point
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import FastAPI app from main.py (includes ChatKit integration)
from main import app

# Export for Vercel
handler = app

# Note: Vercel serverless has limitations:
# - 10-60 sec timeout (may affect long RAG queries)
# - Streaming (SSE) may not work properly
# - Cold starts can be slow with heavy dependencies
