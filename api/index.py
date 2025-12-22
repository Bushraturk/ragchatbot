# Vercel serverless function entry point
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.src.api.main import app

# Export for Vercel
handler = app
