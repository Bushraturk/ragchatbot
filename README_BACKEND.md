# Backend Deployment - Hugging Face Spaces

## Quick Deploy

1. Go to: https://huggingface.co/new-space
2. Select **Docker** as Space SDK
3. Connect GitHub repo: `Bushraturk/ragchatbot`
4. Add Secrets (Settings → Repository Secrets):
   - `DATABASE_URL`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `GEMINI_API_KEY`
   - `COHERE_API_KEY`

5. Space will auto-deploy!

## Backend URL
After deployment: `https://your-space.hf.space`

Update Vercel env: `VITE_API_URL=https://your-space.hf.space`
