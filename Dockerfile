FROM python:3.11-slim

WORKDIR /app

# Copy backend code first
COPY backend/ ./backend/

# Install dependencies from backend directory
RUN pip install --no-cache-dir -r backend/requirements.txt && \
    pip install --no-cache-dir chatkit

# Expose port
EXPOSE 8000

# Set working directory
WORKDIR /app/backend

# Start server using main.py (which includes ChatKit integration)
CMD ["python", "main.py"]
