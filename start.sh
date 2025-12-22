#!/bin/bash

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Install frontend dependencies and build
echo "Building frontend..."
cd ../frontend
npm install
npm run build

# Copy frontend build to backend static folder
echo "Setting up static files..."
cd ..
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

# Start backend server (which will also serve frontend)
echo "Starting server..."
cd backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
