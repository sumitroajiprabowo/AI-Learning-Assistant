import streamlit as st
import google.generativeai as genai
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ==========================================
# MINGGU 1 & 6: KONFIGURASI HALAMAN & API
# ==========================================
st.set_page_config(page_title="AI Learning Companion", page_icon="📚", layout="wide")

# Inisialisasi Session State agar database RAG tidak hilang saat halaman di-refresh
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# Masukkan API Key Gemini milikmu di sini
GEMINI_API_KEY = "AIzaSyAEB-ZNzgeFNGfnTybwaBhcbGGnldLzRM4"
genai.configure(api_key=GEMINI_API_KEY)

st.title("📚 AI-Powered Smart Learning Companion")
st.markdown("Platform pembelajaran adaptif dan personal dengan bantuan AI.")

# Navigasi Sidebar
menu = st.sidebar.selectbox(
    "Pilih Mode Belajar:",
    [
        "Ask Anything (Q&A)", 
        "Study Plan Generator", 
        "Interactive Quiz", 
        "RAG Document Assistant"
    ]
)

# ==========================================
# MINGGU 2: ASK ANYTHING (Q&A SYSTEM)
# ==========================================
if menu == "Ask Anything (Q&A)":
    st.header("💬 Ask Anything")
    st.write("Tanyakan konsep apapun, dan AI akan merangkumkannya untukmu dalam bentuk poin-poin terstruktur.")
    
    user_question = st.text_input("Apa yang ingin kamu pelajari hari ini?", key="qna_input")
    
    if st.button("Tanya AI", key="qna_button"):
        if user_question:
            with st.spinner("Mencari jawaban terbaik..."):
                try:
                    model = genai.GenerativeModel('gemini-flash-lite-latest')
                    prompt = f"Jawab pertanyaan berikut secara edukatif, jelas, dan mendalam. Wajib gunakan format bullet points untuk poin-poin utamanya: {user_question}"
                    
                    response = model.generate_content(prompt)
                    st.success("Selesai!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan pada API: {e}")
        else:
            st.warning("Silakan masukkan pertanyaan terlebih dahulu.")

# ==========================================
# MINGGU 3: PERSONALIZED STUDY PLAN GENERATOR
# ==========================================
elif menu == "Study Plan Generator":
    st.header("📅 Personalized Study Plan Generator")
    st.write("Buat roadmap belajar harian yang terstruktur berdasarkan target dan durasi waktumu.")
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Topik atau Mata Kuliah:", placeholder="Contoh: Pemrograman Python, Basis Data", key="sp_subject")
    with col2:
        timeline = st.number_input("Durasi Belajar (Hari):", min_value=1, max_value=90, value=7, key="sp_timeline")
        
    goals = st.text_area("Tujuan Akhir / Target Capaian:", placeholder="Contoh: Paham konsep dasarnya dan bisa membuat proyek simpel sendiri", key="sp_goals")
    
    if st.button("Buat Rencana Belajar", key="sp_button"):
        if subject and goals:
            with st.spinner("Menyusun roadmap belajar harian..."):
                try:
                    model = genai.GenerativeModel('gemini-flash-lite-latest')
                    prompt = f"""
                    Bertindaklah sebagai penasihat akademik yang ahli. Buatlah rencana belajar harian (day-wise roadmap) selama {timeline} hari untuk mempelajari '{subject}'.
                    Target akhir siswa adalah: {goals}.
                    Berikan jadwal yang realistis, terstruktur per hari, beserta rekomendasi aktivitas atau latihan di setiap harinya.
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("Rencana Belajar Berhasil Dibuat!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan pada API: {e}")
        else:
            st.warning("Harap isi kolom topik dan tujuan akhir terlebih dahulu.")

# ==========================================
# MINGGU 4: INTERACTIVE QUIZ GENERATOR
# ==========================================
elif menu == "Interactive Quiz":
    st.header("📝 Interactive Quiz Generator")
    st.write("Uji pemahaman belajarmu dengan kuis pilihan ganda dinamis yang dibuat langsung oleh AI.")
    
    col1, col2 = st.columns(2)
    with col1:
        quiz_topic = st.text_input("Topik Kuis:", placeholder="Contoh: Pemrograman Berorientasi Objek", key="quiz_topic")
    with col2:
        difficulty = st.selectbox("Tingkat Kesulitan:", ["Mudah", "Sedang", "Sulit"], key="quiz_diff")
        
    num_questions = st.slider("Jumlah Soal:", min_value=1, max_value=10, value=3, key="quiz_num")
    
    if st.button("Generate Kuis", key="quiz_button"):
        if quiz_topic:
            with st.spinner("Membuat soal kuis..."):
                try:
                    model = genai.GenerativeModel('gemini-flash-lite-latest')
                    prompt = f"""
                    Buatlah {num_questions} soal pilihan ganda (Multiple Choice Questions) dengan tingkat kesulitan '{difficulty}' tentang topik '{quiz_topic}'.
                    Format penampilan:
                    - Tampilkan soal beserta opsi pilihan (A, B, C, D) terlebih dahulu.
                    - Di bagian paling bawah, berikan pemisah yang jelas (misalnya: --- KUNCI JAWABAN ---) lalu tampilkan kunci jawaban beserta penjelasan singkat mengapa jawaban tersebut benar.
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("Kuis Berhasil Dibuat!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan pada API: {e}")
        else:
            st.warning("Harap masukkan topik kuis terlebih dahulu.")

# ==========================================
# MINGGU 5: RAG-BASED LEARNING ASSISTANT
# ==========================================
elif menu == "RAG Document Assistant":
    st.header("📄 Document-based Q&A (RAG)")
    st.write("Unggah materi kuliah atau catatan dalam bentuk PDF, lalu ajukan pertanyaan langsung berbasis isi dokumen tersebut.")
    
    uploaded_file = st.file_uploader("Unggah file PDF materi belajar kamu:", type="pdf")
    
    # Cek apakah ada dokumen baru yang diunggah
    if uploaded_file is not None:
        if st.session_state.current_file != uploaded_file.name:
            st.session_state.current_file = uploaded_file.name
            
            # 1. Ekstraksi teks dari dokumen PDF
            with st.spinner("Membaca dokumen PDF..."):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                text_content = ""
                for page in pdf_reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text_content += extracted_text
            
            if text_content:
                # 2. Memecah dokumen menjadi potongan kecil (Text Chunking)
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_text(text_content)
                
                # 3. Membuat Vector Embeddings menggunakan Hugging Face & disimpan ke FAISS
                with st.spinner("Menghitung Vektor & Membangun Knowledge Base (FAISS)..."):
                    # Menggunakan model embeddings open-source yang ringan dan akurat
                    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                    st.session_state.vector_store = FAISS.from_texts(chunks, embeddings)
                st.success(f"Berhasil memproses dokumen: '{uploaded_file.name}'!")
            else:
                st.error("Gagal membaca dokumen. Pastikan file PDF kamu berisi teks, bukan gambar scan.")

    # Bagian input pertanyaan jika database vektor sudah siap
    if st.session_state.vector_store is not None:
        st.markdown("---")
        rag_question = st.text_input("Masukkan pertanyaan seputar isi dokumen:")
        
        if st.button("Cari Jawaban", key="rag_button"):
            if rag_question:
                with st.spinner("Melakukan similarity search & merumuskan jawaban..."):
                    try:
                        # 4. Melakukan pencarian potongan teks paling relevan (Top 3)
                        relevant_docs = st.session_state.vector_store.similarity_search(rag_question, k=3)
                        context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
                        
                        # 5. Mengirimkan konteks dokumen bersama pertanyaan ke Gemini
                        model = genai.GenerativeModel('gemini-flash-lite-latest')
                        prompt = f"""
                        Kamu adalah asisten akademik yang cerdas. Tugasmu adalah menjawab pertanyaan pengguna HANYA berdasarkan konteks dokumen yang disediakan di bawah ini.
                        Jika jawabannya tidak ada di dalam dokumen, katakan secara jujur bahwa informasi tersebut tidak ditemukan di dalam dokumen. Jangan mengada-ada informasi.
                        
                        Konteks Dokumen:
                        {context_text}
                        
                        Pertanyaan:
                        {rag_question}
                        """
                        
                        response = model.generate_content(prompt)
                        st.markdown("### 💡 Jawaban Berdasarkan Dokumen:")
                        st.info(response.text)
                    except Exception as e:
                        st.error(f"Terjadi kendala saat memproses jawaban: {e}")
            else:
                st.warning("Silakan ketik pertanyaan terlebih dahulu.")