#!/bin/bash
# Setup and Installation Script
# Run this script to set up the AI Learning Assistant project

echo "🚀 Setting up AI Learning Assistant..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🖥️ Windows detected - activating venv..."
    source venv/Scripts/activate
else
    echo "🐧 Linux/Mac detected - activating venv..."
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads vector_db data static templates

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created. Please edit it and add your API keys."
    else
        echo "❌ .env.example not found. Please create .env file manually."
    fi
else
    echo "✅ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your OpenAI and Gemini API keys"
echo "2. Run the Flask backend: python app.py"
echo "3. In another terminal, run the Streamlit frontend: streamlit run app_streamlit.py"
echo ""
echo "🌐 URLs:"
echo "  Flask API: http://localhost:5000"
echo "  Streamlit UI: http://localhost:8501"