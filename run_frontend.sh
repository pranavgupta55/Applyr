#!/bin/bash

# Run the Streamlit frontend

echo "🎨 Starting Applyr Frontend..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run streamlit
streamlit run frontend/app.py
