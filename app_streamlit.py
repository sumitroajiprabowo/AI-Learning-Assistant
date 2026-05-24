"""
Streamlit Frontend - Milestone 6
User-friendly interface for AI Learning Assistant
"""

import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time
import os

# Configuration
API_BASE_URL = "http://localhost:5000"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .quiz-option {
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .quiz-option:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    .quiz-option.selected {
        border-color: #667eea;
        background: #e8f4ff;
        font-weight: 500;
    }
    .study-plan-day {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .study-plan-day:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .day-completed {
        border-left: 4px solid #28a745;
        background: #f8fff9;
    }
    .day-pending {
        border-left: 4px solid #ffc107;
        background: #fffef8;
    }
    .document-item {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    if 'study_plan' not in st.session_state:
        st.session_state.study_plan = None
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    if 'quiz_results' not in st.session_state:
        st.session_state.quiz_results = None
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []
    if 'rag_questions' not in st.session_state:
        st.session_state.rag_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if '_quiz_debug' not in st.session_state:
        st.session_state._quiz_debug = []

def check_api_health():
    """Check if backend API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.markdown("## 🤖 AI Learning Assistant")
        st.markdown("---")
        
        pages = {
            'home': '🏠 Home',
            'qa': '📚 Q&A System',
            'study': '📋 Study Planner',
            'quiz': '🎯 Quiz Generator',
            'documents': '📄 Document Q&A',
            'settings': '⚙️ Settings'
        }
        
        for page_id, page_name in pages.items():
            if st.button(page_name, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # System status
        if check_api_health():
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Offline")

def render_home():
    """Render the home page"""
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">📚 AI Learning Assistant</h1>
        <p style="color: white; margin: 10px 0 0 0;">Your intelligent companion for personalized learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 Q&A System</h3>
            <p>Ask any question and get structured bullet-point answers powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Q&A", key="start_qa", use_container_width=True):
            st.session_state.current_page = 'qa'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Study Planner</h3>
            <p>Create personalized day-by-day learning roadmaps tailored to your goals</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create Study Plan", key="start_study", use_container_width=True):
            st.session_state.current_page = 'study'
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Quiz Generator</h3>
            <p>Generate interactive quizzes with dynamic difficulty levels</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Take Quiz", key="start_quiz", use_container_width=True):
            st.session_state.current_page = 'quiz'
            st.rerun()

def render_qa_system():
    """Render the Q&A System page"""
    st.markdown("## 📚 Ask Anything - AI Q&A System")
    
    with st.form("question_form"):
        question = st.text_area("Your Question:", placeholder="Type your question here...", height=100)
        context = st.text_input("Optional Context (for better answers):", placeholder="Provide additional context if needed")
        provider = st.selectbox("AI Provider:", ["auto", "gemini"], index=0)
        
        submitted = st.form_submit_button("Get Answer", use_container_width=True, type="primary")
    
    if submitted and question.strip():
        with st.spinner("Generating answer..."):
            try:
                payload = {
                    "question": question,
                    "context": context,
                    "provider": provider
                }

                response = requests.post(f"{API_BASE_URL}/api/ask", json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                if not result.get("success"):
                    raise ValueError(result.get("error", "Failed to generate answer"))

                answer = result.get("answer", "• No answer available")
                
                # Add to history
                st.session_state.qa_history.append({
                    'question': question,
                    'answer': answer,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                st.markdown("### ✅ Answer:")
                st.markdown(answer)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Show Q&A history
    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("### 📝 Previous Questions")
        
        for i, qa in enumerate(reversed(st.session_state.qa_history)):
            with st.expander(f"{qa['timestamp']} - {qa['question'][:50]}..."):
                st.markdown(f"**Q:** {qa['question']}")
                st.markdown(f"**A:** {qa['answer']}")

def render_study_planner():
    """Render Study Plan Generator"""
    st.markdown("## 📋 Personalized Study Plan Generator")
    
    with st.form("study_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goals = st.text_input("Learning Goals:", placeholder="e.g., Learn Python programming, Prepare for exam")
            subjects_input = st.text_input("Subjects (comma-separated):", placeholder="e.g., Python, Mathematics, Physics")
            timeline = st.slider("Timeline (Days):", min_value=7, max_value=365, value=30)
        
        with col2:
            daily_hours = st.slider("Daily Study Hours:", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
            difficulty = st.selectbox("Difficulty Level:", ["beginner", "intermediate", "advanced"])
            learning_style = st.selectbox("Learning Style:", ["visual", "auditory", "kinesthetic", "reading", "mixed"])
        
        submitted = st.form_submit_button("Generate Study Plan", use_container_width=True, type="primary")
    
    if submitted and goals.strip() and subjects_input.strip():
        subjects = [s.strip() for s in subjects_input.split(',')]
        
        with st.spinner("Generating your personalized study plan..."):
            try:
                payload = {
                    "goals": goals,
                    "subjects": subjects,
                    "timeline": timeline,
                    "daily_hours": daily_hours,
                    "difficulty_level": difficulty,
                    "learning_style": learning_style
                }

                response = requests.post(f"{API_BASE_URL}/api/study-plan", json=payload, timeout=60)
                response.raise_for_status()
                study_plan = response.json()
                
                st.session_state.study_plan = study_plan
                
                if study_plan['success']:
                    st.markdown("### ✅ Study Plan Generated!")
                    plan = study_plan['plan']
                    
                    # Show plan metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Duration", f"{plan['metadata']['timeline_days']} days")
                    with col2:
                        st.metric("Daily Hours", f"{plan['metadata']['daily_hours']} hrs")
                    with col3:
                        st.metric("Total Hours", f"{plan['metadata']['total_study_hours']} hrs")
                    
                    # Show daily breakdown
                    st.markdown("### 📅 Daily Schedule")
                    for day_data in plan['daily_breakdown']:
                        with st.expander(f"Day {day_data['day']} - {day_data['primary_subject']} ({day_data['date']})"):
                            st.markdown(f"**Total Hours:** {day_data['total_hours']} hours")
                            st.markdown(f"**Topics:**")
                            for topic in day_data['topics']:
                                st.markdown(f"  • {topic}")
                            
                            st.markdown("**Activities:**")
                            for activity in day_data['activities']:
                                st.markdown(f"  • **{activity['activity']}** ({activity['duration_hours']} hours)")
                    
                    # Progress tracking
                    st.markdown("### 📊 Progress Tracking")
                    progress = st.progress(0)
                    status_text = st.empty()
                    status_text.text("0% complete (0/{} days)".format(timeline))
                else:
                    st.error(f"Error: {study_plan.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error generating study plan: {str(e)}")

def render_quiz_generator():
    """Render Quiz Generator page"""
    st.markdown("## 🎯 Interactive Quiz Generator")
    
    # Quiz configuration
    with st.form("quiz_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.text_input("Subject:", placeholder="e.g., Python, Biology, History")
            topic = st.text_input("Topic (Optional):", placeholder="e.g., Functions, Cell Biology")
            difficulty = st.selectbox("Difficulty:", ["easy", "medium", "hard"])
        
        with col2:
            num_questions = st.slider("Number of Questions:", min_value=5, max_value=50, value=10)
            st.info("Quiz ini memakai pilihan ganda saja agar klik jawaban dan penilaian konsisten.")
            question_types = ["multiple_choice"]
        
        submitted = st.form_submit_button("Generate Quiz", use_container_width=True, type="primary")
    
    # Step 1: generate only. Store quiz then rerun so the quiz UI renders
    # outside this form-submit branch (radio clicks trigger reruns that would
    # otherwise reset `submitted` to False and make the quiz disappear).
    if submitted and subject.strip():
        with st.spinner("Creating your quiz..."):
            try:
                payload = {
                    "subject": subject,
                    "topic": topic,
                    "difficulty": difficulty,
                    "num_questions": num_questions,
                    "question_types": question_types
                }

                response = requests.post(f"{API_BASE_URL}/api/quiz/generate", json=payload, timeout=60)
                response.raise_for_status()
                quiz_data = response.json()

                if quiz_data.get('success'):
                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_results = None
                    st.session_state.user_answers = {
                        str(q['question_number']): None
                        for q in quiz_data['quiz']['questions']
                    }
                    st.rerun()
                else:
                    st.error(f"Error: {quiz_data.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")

    # Step 2: render the active quiz from session state (persists across reruns)
    active = st.session_state.quiz_data
    if (active and isinstance(active, dict) and active.get('success')
            and not st.session_state.quiz_results):
        quiz = active['quiz']

        # Ensure answer map exists (e.g., after a fresh page load)
        if not st.session_state.user_answers:
            st.session_state.user_answers = {
                str(q['question_number']): None for q in quiz['questions']
            }

        st.success("✅ Quiz ready! Pilih jawaban lalu klik Submit.")
        st.markdown(f"### 📝 Quiz: {quiz['metadata']['subject']}")
        if quiz['metadata'].get('topic'):
            st.markdown(f"**Topic:** {quiz['metadata']['topic']}")
        st.markdown(f"**Difficulty:** {quiz['metadata']['difficulty']}")
        st.markdown(f"**Questions:** {quiz['metadata']['num_questions']}")

        for q in quiz['questions']:
            with st.container():
                st.markdown(f"**Question {q['question_number']}:**")
                st.markdown(q['question_text'])

                if q['question_type'] == 'multiple_choice':
                    options = q['options']
                    choice_labels = [f"{chr(65+i)}. {options[i]}" for i in range(len(options))]
                    radio_key = f"q_{q['question_number']}_radio"
                    selected_label = st.radio(
                        "Choose your answer:",
                        choice_labels,
                        index=None,
                        key=radio_key,
                    )
                    if isinstance(selected_label, str) and selected_label:
                        selected_index = ord(selected_label[0].upper()) - ord('A')
                    else:
                        selected_index = None
                    st.session_state.user_answers[str(q['question_number'])] = selected_index

                st.markdown("---")

        if st.button("Submit Quiz", use_container_width=True, type="primary"):
            with st.spinner("Calculating score..."):
                try:
                    submit_payload = {
                        "quiz_id": quiz['id'],
                        "answers": {
                            str(k): v
                            for k, v in st.session_state.user_answers.items()
                        }
                    }
                    sub_resp = requests.post(
                        f"{API_BASE_URL}/api/quiz/submit",
                        json=submit_payload,
                        timeout=30,
                    )
                    sub_resp.raise_for_status()
                    sub_data = sub_resp.json()
                    if not sub_data.get('success'):
                        raise ValueError(sub_data.get('error', 'Failed to submit quiz'))
                    st.session_state.quiz_results = sub_data['results']
                    st.rerun()
                except Exception as e:
                    st.error(f"Error submitting quiz: {str(e)}")

    # Show results if available (only when scoring has been computed)
    if st.session_state.quiz_results and isinstance(st.session_state.quiz_results, dict) and 'score' in st.session_state.quiz_results:
        st.markdown("---")
        results = st.session_state.quiz_results['score']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Correct Answers", f"{results['correct_answers']}/{results['total_questions']}")
        with col2:
            st.metric("Score", f"{results['percentage']:.1f}%")
        with col3:
            st.metric("Grade", results['grade'])

        if results.get('passed'):
            st.success(f"✅ {st.session_state.quiz_results.get('feedback', '')}")
        else:
            st.warning("⚠️ Study more and try again!")

        detailed_results = st.session_state.quiz_results.get('detailed_results', {})
        if detailed_results:
            st.markdown("### 🧾 Per Question Result")
            for qid, info in detailed_results.items():
                if info.get('is_correct'):
                    st.success(
                        f"Q{qid}: Benar | Jawaban kamu: {info.get('selected_text')} | Jawaban benar: {info.get('correct_text')}"
                    )
                else:
                    st.error(
                        f"Q{qid}: Salah | Jawaban kamu: {info.get('selected_text')} | Jawaban benar: {info.get('correct_text')}"
                    )

        if st.button("Start New Quiz"):
            st.session_state.quiz_data = None
            st.session_state.quiz_results = None
            st.session_state.user_answers = {}
            st.rerun()

    # Debug area for quiz interactions (hidden unless needed)
    if st.session_state._quiz_debug:
        with st.expander("Quiz Interaction Debug Log"):
            for d in st.session_state._quiz_debug[-50:]:
                st.markdown(f"- {d}")

def render_documents():
    """Render Document Q&A page"""
    st.markdown("## 📄 Document-Based Q&A")
    
    # File upload section
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Upload Document (PDF, TXT, or DOCX):",
            type=['pdf', 'txt', 'docx']
        )
        
        uploaded = st.form_submit_button("Upload Document", use_container_width=True)
    
    if uploaded and uploaded_file:
        with st.spinner("Processing document..."):
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")
                }

                response = requests.post(f"{API_BASE_URL}/api/documents/upload", files=files, timeout=120)
                response.raise_for_status()
                result = response.json()

                if result.get('success'):
                    st.session_state.uploaded_documents.append(result)
                    st.success(f"✅ Document '{result.get('document_name', uploaded_file.name)}' uploaded successfully!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error uploading document: {str(e)}")
    
    # Show uploaded documents
    if st.session_state.uploaded_documents:
        st.markdown("### 📁 Uploaded Documents")
        
        for doc in st.session_state.uploaded_documents:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"📄 **{doc.get('document_name', 'Unknown')}**")
            with col2:
                if st.button("Remove", key=f"remove_{doc.get('document_id', '')}"):
                    st.session_state.uploaded_documents.remove(doc)
                    st.rerun()
    
    # Ask question about documents
    st.markdown("---")
    st.markdown("### 💬 Ask Questions About Your Documents")
    
    with st.form("doc_question_form"):
        question = st.text_input("Your Question:", placeholder="What would you like to know?")
        
        # Document selection if documents exist
        if st.session_state.uploaded_documents:
            doc_options = {d['document_name']: d['document_id'] for d in st.session_state.uploaded_documents}
            selected_docs = st.multiselect("Select Documents:", options=list(doc_options.keys()))
        else:
            st.info("📁 Upload documents first to enable Q&A")
            selected_docs = []
        
        asked = st.form_submit_button("Ask Question", use_container_width=True)
    
    if asked and question.strip() and st.session_state.uploaded_documents:
        with st.spinner("Searching documents..."):
            try:
                doc_ids = [doc_options[name] for name in selected_docs if name in doc_options]
                payload = {
                    "question": question,
                    "document_ids": doc_ids,
                    "top_k": 5
                }

                response = requests.post(f"{API_BASE_URL}/api/documents/ask", json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()

                if not result.get('success'):
                    raise ValueError(result.get('error', 'Failed to answer document question'))

                answer = result.get('answer', '• No answer available')
                
                st.session_state.rag_questions.append({
                    'question': question,
                    'answer': answer,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                st.markdown("### ✅ Answer:")
                st.markdown(answer)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Show RAG question history
    if st.session_state.rag_questions:
        st.markdown("---")
        st.markdown("### 📝 Previous Document Questions")
        
        for i, qq in enumerate(reversed(st.session_state.rag_questions)):
            with st.expander(f"{qq['timestamp']} - {qq['question'][:50]}..."):
                st.markdown(f"**Q:** {qq['question']}")
                st.markdown(f"**A:** {qq['answer']}")

def render_settings():
    """Render Settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔑 API Configuration")
    
    with st.form("api_settings"):
        gemini_key = st.text_input("Gemini API Key:", type="password")
        openai_key = st.text_input("OpenAI API Key (Optional, fallback):", type="password")
        pinecone_key = st.text_input("Pinecone API Key (Optional):", type="password")

        if st.form_submit_button("Save Configuration"):
            try:
                payload = {
                    "gemini_api_key": gemini_key,
                    "openai_api_key": openai_key,
                    "pinecone_api_key": pinecone_key
                }

                response = requests.post(f"{API_BASE_URL}/api/settings/api-keys", json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                if result.get("success"):
                    st.success("Configurations saved!")
                    if result.get("gemini_configured"):
                        st.info("Gemini configured.")
                    if result.get("openai_configured"):
                        st.info("OpenAI configured (fallback).")
                    if not result.get("gemini_configured") and not result.get("openai_configured"):
                        st.warning("No AI provider configured. Q&A will not work.")
                else:
                    st.error(result.get("error", "Failed to save configuration"))

            except Exception as e:
                st.error(f"Error saving configuration: {str(e)}")
    
    st.markdown("### 🎨 Theme")
    
    dark_mode = st.checkbox("Dark Mode", value=False)
    if dark_mode:
        st.markdown("""
        <style>
            .stApp { background-color: #1e1e1e; color: white; }
        </style>
        """, unsafe_allow_html=True)
        st.info("Dark mode is under development")

def main():
    """Main application entry point"""
    initialize_session_state()
    render_sidebar()
    
    # Page routing
    if st.session_state.current_page == 'home':
        render_home()
    elif st.session_state.current_page == 'qa':
        render_qa_system()
    elif st.session_state.current_page == 'study':
        render_study_planner()
    elif st.session_state.current_page == 'quiz':
        render_quiz_generator()
    elif st.session_state.current_page == 'documents':
        render_documents()
    elif st.session_state.current_page == 'settings':
        render_settings()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        f"🤖 AI Learning Assistant v1.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()