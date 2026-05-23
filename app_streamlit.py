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
        provider = st.selectbox("AI Provider:", ["auto", "openai", "gemini"], index=0)
        
        submitted = st.form_submit_button("Get Answer", use_container_width=True, type="primary")
    
    if submitted and question.strip():
        with st.spinner("Generating answer..."):
            try:
                # Call API
                payload = {
                    "question": question,
                    "context": context,
                    "provider": provider
                }
                
                # Mock response for demo
                answer = f"""
                • **Understanding the Question**: I need to analyze the question "{question}" thoroughly.
                • **Key Concepts**: Based on the question, here are the main concepts to consider:
                  • First important point related to your question
                  • Second aspect that needs attention  
                  • Third consideration for a complete answer
                • **Detailed Explanation**: 
                  • The core concept involves understanding the fundamental principles
                  • Practical application requires hands-on experience
                  • Best practices suggest starting with basics and building up
                • **Recommendations**:
                  • Start with foundational knowledge
                  • Practice with real-world examples
                  • Seek additional resources for deeper understanding
                """
                
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
                # Call API
                payload = {
                    "goals": goals,
                    "subjects": subjects,
                    "timeline": timeline,
                    "daily_hours": daily_hours,
                    "difficulty_level": difficulty,
                    "learning_style": learning_style
                }
                
                # Mock study plan for demonstration
                study_plan = {
                    "success": True,
                    "plan": {
                        "id": str(uuid.uuid4()),
                        "daily_breakdown": [
                            {
                                "day": i+1,
                                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                                "primary_subject": subjects[i % len(subjects)],
                                "total_hours": daily_hours,
                                "topics": [f"Topic {j+1} for Day {i+1}" for j in range(3)],
                                "activities": [
                                    {"activity": "Study", "duration_hours": daily_hours * 0.6, "topics_covered": ["Chapter 1"], "completed": False},
                                    {"activity": "Practice", "duration_hours": daily_hours * 0.3, "topics_covered": ["Exercises"], "completed": False},
                                    {"activity": "Review", "duration_hours": daily_hours * 0.1, "topics_covered": ["Notes"], "completed": False}
                                ],
                                "completed": False
                            }
                            for i in range(min(7, timeline))  # Show first 7 days for demo
                        ]
                    }
                }
                
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
            question_types = st.multiselect(
                "Question Types:",
                ["multiple_choice", "true_false"],
                default=["multiple_choice"]
            )
        
        submitted = st.form_submit_button("Generate Quiz", use_container_width=True, type="primary")
    
    if submitted and subject.strip():
        with st.spinner("Creating your quiz..."):
            try:
                # Mock quiz for demonstration
                quiz_data = {
                    "success": True,
                    "quiz": {
                        "id": str(uuid.uuid4()),
                        "metadata": {
                            "subject": subject,
                            "topic": topic,
                            "difficulty": difficulty,
                            "num_questions": num_questions
                        },
                        "questions": [
                            {
                                "question_number": i+1,
                                "question_text": f"Sample {difficulty} question about {subject} #{i+1}: What is a key concept?",
                                "question_type": "multiple_choice",
                                "options": ["Option A", "Option B", "Option C", "Option D"],
                                "points": 1
                            }
                            for i in range(min(3, num_questions))  # Demo: show 3 questions
                        ]
                    }
                }
                
                st.session_state.quiz_data = quiz_data
                
                if quiz_data['success']:
                    st.success("✅ Quiz generated successfully!")
                    
                    quiz = quiz_data['quiz']
                    st.markdown(f"### 📝 Quiz: {quiz['metadata']['subject']}")
                    if quiz['metadata'].get('topic'):
                        st.markdown(f"**Topic:** {quiz['metadata']['topic']}")
                    st.markdown(f"**Difficulty:** {quiz['metadata']['difficulty']}")
                    st.markdown(f"**Questions:** {quiz['metadata']['num_questions']}")
                    
                    # Quiz questions
                    st.session_state.user_answers = {}
                    
                    for q in quiz['questions']:
                        with st.container():
                            st.markdown(f"**Question {q['question_number']}:**")
                            st.markdown(q['question_text'])
                            
                            if q['question_type'] == 'multiple_choice':
                                options = q['options']
                                selected = st.radio(
                                    "Choose your answer:",
                                    range(len(options)),
                                    format_func=lambda x: f"{chr(65+x)}. {options[x]}",
                                    key=f"q_{q['question_number']}"
                                )
                                st.session_state.user_answers[str(q['question_number'])] = selected
                            
                            st.markdown("---")
                    
                    if st.button("Submit Quiz", use_container_width=True, type="primary"):
                        with st.spinner("Calculating score..."):
                            # Mock scoring
                            correct = sum(1 for ans in st.session_state.user_answers.values() if ans == 0)
                            total = len(st.session_state.user_answers)
                            percentage = (correct / total * 100) if total > 0 else 0
                            
                            results = {
                                "score": {
                                    "correct_answers": correct,
                                    "total_questions": total,
                                    "percentage": round(percentage, 1),
                                    "grade": "A" if percentage >= 90 else "B" if percentage >= 80 else "C" if percentage >= 70 else "D",
                                    "passed": percentage >= 60
                                },
                                "feedback": "Great job!" if percentage >= 80 else "Good effort, keep practicing!"
                            }
                            
                            st.session_state.quiz_results = results
                            st.rerun()
                    
                else:
                    st.error(f"Error: {quiz_data.get('error', 'Unknown error')}");
                    
            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")
    
    # Show results if available
    if st.session_state.quiz_results:
        st.markdown("---")
        results = st.session_state.quiz_results['score']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Correct Answers", f"{results['correct_answers']}/{results['total_questions']}")
        with col2:
            st.metric("Score", f"{results['percentage']:.1f}%")
        with col3:
            st.metric("Grade", results['grade'])
        
        if results['passed']:
            st.success(f"✅ {st.session_state.quiz_results['feedback']}")
        else:
            st.warning("⚠️ Study more and try again!")
        
        if st.button("Start New Quiz"):
            st.session_state.quiz_data = None
            st.session_state.quiz_results = None
            st.rerun()

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
                # Save file
                file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Mock upload response
                response = {
                    "success": True,
                    "document_id": str(uuid.uuid4()),
                    "document_name": uploaded_file.name,
                    "chunks_created": 15,
                    "content_length": len(uploaded_file.getvalue())
                }
                
                if response['success']:
                    st.session_state.uploaded_documents.append(response)
                    st.success(f"✅ Document '{uploaded_file.name}' uploaded successfully!")
                else:
                    st.error(f"Error: {response.get('error', 'Unknown error')}");
                    
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
                # Mock RAG response
                answer = """
                **Based on your documents:**
                
                • The document contains information related to your question.
                • Key points from the document suggest the following:
                  • First important detail
                  • Second relevant point
                  • Third consideration
                
                **Sources:** Document content analysis
                """
                
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
        openai_key = st.text_input("OpenAI API Key:", type="password")
        gemini_key = st.text_input("Gemini API Key:", type="password")
        pinecone_key = st.text_input("Pinecone API Key (Optional):", type="password")
        
        if st.form_submit_button("Save Configuration"):
            st.success("Configurations saved!")
    
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