FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Expose port
EXPOSE 7860

# Set working directory
WORKDIR /app/backend

# Start server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
