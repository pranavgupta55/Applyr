#!/bin/bash

# Applyr Setup Script
# Sets up the internship application bot environment

echo "🎯 Applyr Setup Script"
echo "======================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

echo "✅ Playwright browsers installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data/resumes
mkdir -p temp
mkdir -p backend
mkdir -p frontend

echo "✅ Directories created"
echo ""

# Copy example env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "======================"
echo "✅ Setup Complete!"
echo "======================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Copy your resume PDFs to data/resumes/"
echo "3. Run the backend: ./run_backend.sh"
echo "4. Run the frontend: ./run_frontend.sh"
echo ""
