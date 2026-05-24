"""
AI Learning Assistant - Main Flask Application
Integrates all modules: Q&A System, Study Planner, Quiz Generator, and RAG Assistant
"""

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
import json
from pathlib import Path

from config import Config, config
from modules.qa_system import QASystem
from modules.study_planner import StudyPlanGenerator
from modules.quiz_generator import QuizGenerator
from modules.rag_assistant import RAGLearningAssistant

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])
ENV_FILE_PATH = Path(__file__).resolve().parent / ".env"

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

qa_system = None
study_planner = None
quiz_generator = None
rag_assistant = None


def _set_env_value(key, value):
    """Update the current process environment and Config attributes."""
    if value is None or not str(value).strip():
        os.environ.pop(key, None)
        setattr(Config, key, None)
    else:
        normalized_value = str(value).strip()
        os.environ[key] = normalized_value
        setattr(Config, key, normalized_value)


def _persist_env_file(updates):
    """Persist selected settings to the workspace .env file."""
    existing_lines = []
    if ENV_FILE_PATH.exists():
        existing_lines = ENV_FILE_PATH.read_text(encoding="utf-8").splitlines()

    updated_keys = set()
    output_lines = []

    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            output_lines.append(line)
            continue

        key, current_value = line.split("=", 1)
        key = key.strip()

        if key in updates:
            new_value = updates[key]
            updated_keys.add(key)
            if new_value is None or not str(new_value).strip():
                continue
            output_lines.append(f"{key}={str(new_value).strip()}")
        else:
            output_lines.append(line)

    for key, value in updates.items():
        if key in updated_keys:
            continue
        if value is None or not str(value).strip():
            continue
        output_lines.append(f"{key}={str(value).strip()}")

    ENV_FILE_PATH.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")


def initialize_ai_modules():
    """Initialize or refresh all AI modules."""
    global qa_system, study_planner, quiz_generator, rag_assistant

    try:
        qa_system = QASystem()
        study_planner = StudyPlanGenerator()
        quiz_generator = QuizGenerator()
        rag_assistant = RAGLearningAssistant()
        logger.info("All AI modules initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing AI modules: {str(e)}")
        qa_system = study_planner = quiz_generator = rag_assistant = None


initialize_ai_modules()

# HTML Templates
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Learning Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; font-size: 2.5em; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }
        .feature-card { background: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #667eea; transition: transform 0.3s; }
        .feature-card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #667eea; margin-top: 0; font-size: 1.3em; }
        .feature-card p { color: #666; line-height: 1.6; }
        .api-endpoints { background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .endpoint { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8; }
        .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; font-size: 0.8em; }
        .get { background: #28a745; }
        .post { background: #007bff; }
        .status { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .milestone { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .milestone h4 { color: #856404; margin: 0 0 10px 0; }
        .milestone ul { margin: 10px 0; padding-left: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Learning Assistant</h1>
        
        <div class="status">
            <h3>🟢 System Status: Operational</h3>
            <p>All AI modules are running successfully. Your learning assistant is ready to help!</p>
        </div>

        <div class="feature-grid">
            <div class="feature-card">
                <h3>📚 Ask Anything (Q&A System)</h3>
                <p>Get instant answers to any question with structured bullet points. Powered by Google Gemini for comprehensive responses.</p>
                <strong>Endpoint:</strong> <code>POST /api/ask</code>
            </div>

            <div class="feature-card">
                <h3>📋 Personalized Study Plans</h3>
                <p>Generate customized day-by-day learning roadmaps based on your goals, timeline, and preferred subjects. Smart scheduling with progress tracking.</p>
                <strong>Endpoint:</strong> <code>POST /api/study-plan</code>
            </div>

            <div class="feature-card">
                <h3>🎯 Interactive Quizzes</h3>
                <p>Dynamic MCQ generation with adjustable difficulty levels. Test your knowledge and get detailed feedback on your performance.</p>
                <strong>Endpoint:</strong> <code>POST /api/quiz/generate</code>
            </div>

            <div class="feature-card">
                <h3>📄 Document-Based Q&A</h3>
                <p>Upload PDFs, documents, and notes. Ask questions directly from your materials using advanced RAG technology with FAISS vector search.</p>
                <strong>Endpoint:</strong> <code>POST /api/documents/upload</code>
            </div>
        </div>

        <div class="api-endpoints">
            <h3>🔗 Available API Endpoints</h3>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/health</strong> - System health check
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/ask</strong> - Ask any question
                <br><small>Body: {"question": "your question", "context": "optional context"}</small>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/study-plan</strong> - Generate study plan
                <br><small>Body: {"goals": "learning goals", "subjects": ["subject1", "subject2"], "timeline": 30, "daily_hours": 2}</small>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/quiz/generate</strong> - Create quiz
                <br><small>Body: {"subject": "topic", "difficulty": "medium", "num_questions": 10}</small>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/documents/upload</strong> - Upload document for RAG
                <br><small>Form data with file field</small>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/documents/ask</strong> - Ask question about documents
                <br><small>Body: {"question": "your question", "document_ids": ["optional", "doc", "ids"]}</small>
            </div>
        </div>

        <div class="milestone">
            <h4>🎯 Development Milestones Progress</h4>
            <ul>
                <li>✅ Milestone 1: Development environment setup</li>
                <li>✅ Milestone 2: Q&A System implementation</li>
                <li>✅ Milestone 3: Study Plan Generator</li>
                <li>✅ Milestone 4: Interactive Quiz Generator</li>
                <li>✅ Milestone 5: RAG-based Learning Assistant</li>
                <li>🔄 Milestone 6: UI Development and Deployment (In Progress)</li>
            </ul>
        </div>

        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>🚀 Ready to start learning? Use the API endpoints above or integrate with your preferred frontend framework!</p>
            <p><strong>Next Steps:</strong> Install dependencies with <code>pip install -r requirements.txt</code> and configure your API keys in <code>.env</code></p>
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    """Homepage with feature overview"""
    try:
        return render_template_string(MAIN_TEMPLATE)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health')
def health_check():
    """System health check"""
    try:
        # Check API key configuration
        missing_keys = Config.validate_api_keys()
        
        # Check module status
        modules_status = {
            'qa_system': qa_system is not None,
            'study_planner': study_planner is not None,
            'quiz_generator': quiz_generator is not None,
            'rag_assistant': rag_assistant is not None
        }
        
        # Get RAG system status
        rag_status = {}
        if rag_assistant:
            rag_status = rag_assistant.get_system_status()
        
        return jsonify({
            "status": "healthy",
            "message": "AI Learning Assistant is operational",
            "timestamp": datetime.now().isoformat(),
            "modules": modules_status,
            "rag_system": rag_status,
            "missing_api_keys": missing_keys,
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({"error": "Health check failed", "details": str(e)}), 500


@app.route('/api/settings/api-keys', methods=['POST'])
def update_api_keys():
    """Persist API key settings and refresh AI modules."""
    try:
        data = request.get_json(silent=True) or {}

        gemini_api_key = data.get('gemini_api_key')
        openai_api_key = data.get('openai_api_key')
        pinecone_api_key = data.get('pinecone_api_key')

        _set_env_value('GEMINI_API_KEY', gemini_api_key)
        _set_env_value('OPENAI_API_KEY', openai_api_key)
        _set_env_value('PINECONE_API_KEY', pinecone_api_key)

        _persist_env_file({
            'GEMINI_API_KEY': gemini_api_key,
            'OPENAI_API_KEY': openai_api_key,
            'PINECONE_API_KEY': pinecone_api_key,
        })

        initialize_ai_modules()

        return jsonify({
            "success": True,
            "message": "API configuration saved successfully",
            "gemini_configured": bool(Config.GEMINI_API_KEY),
            "openai_configured": bool(Config.OPENAI_API_KEY),
            "pinecone_configured": bool(Config.PINECONE_API_KEY)
        })

    except Exception as e:
        logger.error(f"Error saving API settings: {str(e)}")
        return jsonify({"success": False, "error": f"Failed to save API settings: {str(e)}"}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Q&A System endpoint - Milestone 2"""
    try:
        if not qa_system:
            return jsonify({"error": "Q&A system not available"}), 503
        
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data.get('question', '').strip()
        context = data.get('context', '')
        provider = data.get('provider', 'auto')
        
        response = qa_system.ask_question(question, context, provider)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return jsonify({"error": "Failed to process question", "details": str(e)}), 500

@app.route('/api/study-plan', methods=['POST'])
def generate_study_plan():
    """Study Plan Generator endpoint - Milestone 3"""
    try:
        if not study_planner:
            return jsonify({"error": "Study planner not available"}), 503
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        response = study_planner.generate_study_plan(data)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in study plan endpoint: {str(e)}")
        return jsonify({"error": "Failed to generate study plan", "details": str(e)}), 500

@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """Quiz Generator endpoint - Milestone 4"""
    try:
        if not quiz_generator:
            return jsonify({"error": "Quiz generator not available"}), 503
        
        data = request.get_json()
        if not data or 'subject' not in data:
            return jsonify({"error": "Subject is required"}), 400
        
        response = quiz_generator.generate_quiz(data)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in quiz generation endpoint: {str(e)}")
        return jsonify({"error": "Failed to generate quiz", "details": str(e)}), 500

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    """Submit quiz answers for scoring"""
    try:
        if not quiz_generator:
            return jsonify({"error": "Quiz generator not available"}), 503
        
        data = request.get_json()
        if not data or 'quiz_id' not in data or 'answers' not in data:
            return jsonify({"error": "Quiz ID and answers are required"}), 400
        
        quiz_id = data['quiz_id']
        answers = data['answers']
        
        response = quiz_generator.submit_quiz(quiz_id, answers)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in quiz submission endpoint: {str(e)}")
        return jsonify({"error": "Failed to submit quiz", "details": str(e)}), 500

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Document upload endpoint for RAG - Milestone 5"""
    try:
        if not rag_assistant:
            return jsonify({"error": "RAG assistant not available"}), 503
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt', '.docx')):
            return jsonify({"error": "Unsupported file format. Use PDF, TXT, or DOCX"}), 400
        
        # Save file securely
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process document
        response = rag_assistant.upload_document(file_path, filename)
        
        # Clean up uploaded file after processing
        try:
            os.remove(file_path)
        except:
            pass  # Ignore cleanup errors
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in document upload endpoint: {str(e)}")
        return jsonify({"error": "Failed to upload document", "details": str(e)}), 500

@app.route('/api/documents/ask', methods=['POST'])
def ask_document_question():
    """Ask questions about uploaded documents"""
    try:
        if not rag_assistant:
            return jsonify({"error": "RAG assistant not available"}), 503
        
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data.get('question', '').strip()
        document_ids = data.get('document_ids', None)
        top_k = data.get('top_k', 5)
        
        response = rag_assistant.ask_document_question(question, document_ids, top_k)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in document question endpoint: {str(e)}")
        return jsonify({"error": "Failed to process document question", "details": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of uploaded documents"""
    try:
        if not rag_assistant:
            return jsonify({"error": "RAG assistant not available"}), 503
        
        documents = rag_assistant.get_uploaded_documents()
        return jsonify({
            "success": True,
            "documents": documents,
            "total_count": len(documents)
        })
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({"error": "Failed to get documents", "details": str(e)}), 500

@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a specific document"""
    try:
        if not rag_assistant:
            return jsonify({"error": "RAG assistant not available"}), 503
        
        response = rag_assistant.delete_document(document_id)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return jsonify({"error": "Failed to delete document", "details": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        print(f"🚀 Starting AI Learning Assistant on port {port}")
        print(f"🔧 Debug mode: {debug}")
        print(f"📚 Visit http://localhost:{port} to get started")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        print(f"❌ Error: {str(e)}")