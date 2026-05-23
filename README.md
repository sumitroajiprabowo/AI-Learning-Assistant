# AI Learning Assistant 🤖📚

A comprehensive AI-powered learning assistant built with Flask, Streamlit, and advanced AI/ML technologies. This project implements four major milestones creating a complete personalized learning ecosystem.

## ✨ Features

### 📚 Ask Anything - Q&A System (Milestone 2)
- **Multi-provider AI integration**: OpenAI GPT and Google Gemini APIs
- **Structured answers**: All responses formatted in organized bullet points
- **Context-aware**: Supports additional context for better answers
- **Fallback mechanism**: Graceful degradation when one provider fails

### 📋 Personalized Study Plans (Milestone 3)
- **Goal-oriented planning**: Input your learning objectives
- **Flexible timelines**: 7-365 day study durations
- **Subject customization**: Multiple subjects with cycle scheduling
- **Learning style adaptation**: Visual, auditory, kinesthetic, or reading-focused
- **Day-wise roadmaps**: Detailed daily breakdowns with activities
- **Progress tracking**: Mark completed days and track percentages

### 🎯 Interactive Quiz Generator (Milestone 4)
- **Dynamic MCQ generation**: AI-powered question creation
- **Adjustable difficulty**: Easy, medium, and hard levels
- **Authentic categorization**: Questions categorized by subtopic
- **Intelligent weighting**: Balanced question distribution across difficulty
- **Automatic validation**: Verifies answerable questions before storage
- **Contextual hints**: Suggests difficulty-appropriate rationales
- **Score summaries**: Detailed performance reports by subject

### 📄 Document-Based Q&A (Milestone 5)
- **RAG technology**: Retrieval-Augmented Generation for accurate answers
- **Document upload support**: PDF, TXT, and DOCX formats
- **Vector search**: FAISS + HuggingFace embeddings for semantic search
- **Document parsing**: PyPDF2 and python-docx for text extraction
- **Chunking strategy**: Intelligent document chunking for context
- **Citation support**: Source attribution for all answers

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework and API
- **LangChain** - LLM orchestration
- **FAISS** - Vector database for similarity search
- **HuggingFace Transformers** - Sentence embeddings
- **PyPDF2 / python-docx** - Document processing
- **OpenAI API** - GPT integration
- **Google Generative AI** - Gemini integration

### Frontend
- **Streamlit** - Interactive user interface
- **HTML/CSS/JavaScript** - Custom UI components
- **Requests** - API communication

## 📦 Project Structure

```
capstone ai/
├── app.py                    # Flask backend (API endpoints)
├── app_streamlit.py          # Streamlit frontend
├── requirements.txt          # Python dependencies
├── config.py                # Configuration management
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment variables template
├── modules/
│   ├── __init__.py
│   ├── qa_system.py       # Q&A System (Milestone 2)
│   ├── study_planner.py   # Study Plan Generator (Milestone 3)
│   ├── quiz_generator.py    # Quiz Generator (Milestone 4)
│   └── rag_assistant.py     # RAG Learning Assistant (Milestone 5)
├── uploads/               # Uploaded documents
├── vector_db/             # FAISS vector database
├── data/                  # Additional data storage
├── templates/             # HTML templates
└── static/                # Static assets
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git (optional)

### Quick Start

#### Method 1: Automatic Setup (Recommended)

**For Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**For Windows:**
```cmd
setup.bat
```

#### Method 2: Manual Setup

1. **Clone or download the repository**

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

   **Windows:**
   ```cmd
   venv\Scripts\activate.bat
   ```

   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

6. **Start the Flask backend:**
```bash
python app.py
```

7. **Start the Streamlit frontend** (in another terminal):
```bash
streamlit run app_streamlit.py
```

## 🔧 Configuration

### Required API Keys

1. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/)
2. **Gemini API Key** - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Optional API Keys

- **Pinecone API Key** - For cloud vector storage (currently using local FAISS)

## 📖 Usage

### Starting the Application

1. **Backend (Flask API):**
```bash
python app.py
```
- Runs on `http://localhost:5000`
- Provides REST API endpoints for all features

2. **Frontend (Streamlit UI):**
```bash
streamlit run app_streamlit.py
```
- Runs on `http://localhost:8501`
- Provides interactive web interface

### Using the API Directly

#### Q&A System
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d'{"question": "What is machine learning?", "context": "Educational context"}'
```

#### Generate Study Plan
```bash
curl -X POST http://localhost:5000/api/study-plan \
  -H "Content-Type: application/json" \
  -d'{"goals": "Learn Python programming", "subjects": ["Python", "Data Science"], "timeline": 30, "daily_hours": 2}'
```

#### Generate Quiz
```bash
curl -X POST http://localhost:5000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d'{"subject": "Python programming", "difficulty": "medium", "num_questions": 10}'
```

#### Upload Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@/path/to/your/document.pdf"
```

## 🎯 Development Milestones

### ✅ Milestone 1: Development Environment Setup
- Project structure created
- Dependencies defined in requirements.txt
- Configuration system implemented
- Development tools configured

### ✅ Milestone 2: Ask Anything - Q&A System
- Multi-provider AI integration (OpenAI + Gemini)
- Structured bullet-point answers
- Context-aware responses
- Error handling and fallbacks

### ✅ Milestone 3: Personalized Study Plan Generator
- Input validation for goals, subjects, timeline
- AI-powered topic generation
- Daily activity distribution
- Progress tracking system
- Memory-efficient implementation

### ✅ Milestone 4: Interactive Quiz Generator
- Dynamic MCQ generation
- Difficulty-based question categorization
- True/False and Multiple Choice support
- Scoring and feedback system
- Authentic educational assessment tools

### ✅ Milestone 5: RAG-based Learning Assistant
- Document upload and processing
- FAISS vector database integration
- Semantic search capabilities
- Document Q&A functionality

### ✅ Milestone 6: UI Development and Deployment
- Interactive Streamlit dashboard
- User-friendly navigation
- Visual progress indicators
- Comprehensive testing framework

## 🧪 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/api/ask` | POST | Ask a question (Q&A System) |
| `/api/study-plan` | POST | Generate study plan |
| `/api/quiz/generate` | POST | Generate quiz |
| `/api/quiz/submit` | POST | Submit quiz answers |
| `/api/documents/upload` | POST | Upload document for RAG |
| `/api/documents/ask` | POST | Ask about documents |
| `/api/documents` | GET | List uploaded documents |
| `/api/documents/<id>` | DELETE | Delete a document |

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" errors:**
```bash
pip install -r requirements.txt
```

**2. API key errors:**
- Ensure `.env` file exists with correct API keys
- Check that API keys are valid

**3. Port already in use:**
```bash
# Change port in .env file
PORT=5001
```

**4. Large file upload issues:**
- Check `MAX_CONTENT_LENGTH` in config.py
- Ensure sufficient disk space

## 📝 Notes

- **AI Keys**: Replace placeholders in `.env` with actual API keys before first use
- **Storage**: Local vector store persists in `vector_db/` directory
- **Scaling**: Production deployment may require cloud vector database (Pinecone/Weaviate)
- **Security**: Never commit `.env` file to version control

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Voice input and text-to-speech
- [ ] Social features (study groups, sharing)
- [ ] Mobile app (React Native/Flutter)
- [ ] Offline mode with local LLM
- [ ] Advanced analytics and insights
- [ ] Integration with calendar apps
- [ ] Gamification features

## 📄 License

This project is created for educational purposes as a capstone project.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Verify API key configurations
4. Check application logs

## 📞 Contact

For questions or contributions to this AI Learning Assistant project, please feel free to reach out.

---

**Built with ❤️ using Python, Flask, Streamlit, and AI technologies**