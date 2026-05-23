@echo off
REM Setup and Installation Script for Windows
REM Run this script to set up the AI Learning Assistant project

echo 🚀 Setting up AI Learning Assistant...

REM Check Python installation
echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python from python.org
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🖥️ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "vector_db" mkdir vector_db
if not exist "data" mkdir data
if not exist "static" mkdir static
if not exist "templates" mkdir templates

REM Check for .env file
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo 📝 Creating .env file from template...
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ .env file created. Please edit it and add your API keys.
    ) else (
        echo ❌ .env.example not found. Please create .env file manually.
    )
) else (
    echo ✅ .env file exists
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Edit .env file and add your OpenAI and Gemini API keys
echo 2. Run the Flask backend: python app.py
echo 3. In another terminal, run the Streamlit frontend: streamlit run app_streamlit.py
echo.
echo 🌐 URLs:
echo   Flask API: http://localhost:5000
echo   Streamlit UI: http://localhost:8501
pause