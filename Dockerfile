FROM python:3.11-slim

WORKDIR /app

# Copy backend code first
COPY backend/ ./backend/

# Upgrade pip first
RUN pip install --upgrade pip

# Install dependencies from backend directory
RUN pip install --no-cache-dir -r backend/requirements.txt

# Verify chatkit installation
RUN python -c "import chatkit.server; print('✓ chatkit.server imported successfully')" || \
    (echo "ERROR: chatkit module not found!" && exit 1)

# Expose port
EXPOSE 8000

# Set working directory
WORKDIR /app/backend

# Start server using main.py (which includes ChatKit integration)
CMD ["python", "main.py"]
