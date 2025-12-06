#!/bin/bash

# Run the FastAPI backend server

echo "🚀 Starting Applyr Backend..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run uvicorn
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
