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

# Copy frontend build to backend static folder (main.py serves from frontend/dist)
echo "Frontend built successfully..."

# Start backend server using main.py (includes ChatKit + serves frontend)
echo "Starting RAG ChatKit server..."
cd ../backend
python main.py
