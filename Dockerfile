FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Expose port (Koyeb automatically sets PORT env variable)
EXPOSE 8000

# Set working directory
WORKDIR /app/backend

# Start server using main.py (which includes ChatKit integration)
CMD ["python", "main.py"]
