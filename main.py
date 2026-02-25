import streamlit as st
import PyPDF2
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()

# --- Configuration page ---
st.set_page_config(
    page_title="AI Document Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Ultra-Professionnel ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background animé */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Container principal */
    .main-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 30px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: moveBackground 20s linear infinite;
    }
    
    @keyframes moveBackground {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    .hero-section h1 {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .hero-section p {
        color: rgba(255,255,255,0.95);
        font-size: 1.3rem;
        margin-top: 1rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 3px dashed #667eea;
        text-align: center;
        transition: all 0.3s;
    }
    
    .upload-section:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
    }
    
    /* File Uploader Styling */
    .stFileUploader {
        background: white;
        border-radius: 15px;
        padding: 2rem;
    }
    
    /* Input Field */
    .stTextInput input {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s;
        background: white;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 3rem;
        font-size: 1.2rem;
        font-weight: 700;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Summary Card */
    .summary-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1);
        border-left: 6px solid #667eea;
        position: relative;
    }
    
    .summary-card::before {
        content: '📄';
        position: absolute;
        top: -30px;
        left: 30px;
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .summary-card h3 {
        color: #2d3748;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        margin-top: 1rem;
    }
    
    .summary-text {
        color: #4a5568;
        font-size: 1.1rem;
        line-height: 1.8;
        text-align: justify;
    }
    
    /* Stats Section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 15px;
        border: none;
        padding: 1.5rem;
        font-size: 1rem;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        transition: all 0.3s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-weight: 700;
        font-size: 1.2rem;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #718096;
        font-size: 0.95rem;
    }
    
    /* Loading Animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 5px solid rgba(102, 126, 234, 0.3);
        border-top-color: #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1>📄 AI Document Analyzer</h1>
    <p>Synthèse intelligente de vos documents en quelques secondes</p>
</div>
""", unsafe_allow_html=True)

# --- API Key Check ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("❌ ERREUR : OPENROUTER_API_KEY manquante dans le fichier .env")
    st.stop()

# --- Initialisation client ---
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div class="info-box">
        <h2 style="margin-top:0;">🎯 À propos</h2>
        <p>Cet outil utilise <strong>GLM-4.5-Air</strong>, un modèle d'IA avancé pour générer des résumés précis et contextuels de vos documents.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Fonctionnalités")
    
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Multi-format</div>
            <div class="feature-desc">PDF et TXT supportés</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Ultra-rapide</div>
            <div class="feature-desc">Résultats en secondes</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Précision IA</div>
            <div class="feature-desc">Synthèse intelligente</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("💡 **Astuce :** Précisez le format souhaité pour un résumé personnalisé !")

# --- Main Content ---
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown("### 📤 Upload de document")
    upload_file = st.file_uploader(
        "Chargez votre fichier (PDF / TXT)",
        type=["pdf", "txt"],
        help="Formats supportés: PDF, TXT"
    )
    
    if upload_file:
        st.success(f"✅ Fichier chargé : **{upload_file.name}**")
        file_size = len(upload_file.getvalue()) / 1024
        st.info(f"📊 Taille : {file_size:.2f} KB")

with col2:
    st.markdown("### ⚙️ Paramètres")
    summary_style = st.text_input(
        "Format de résumé",
        placeholder="Ex: En 5 points clés",
        help="Précisez comment vous voulez le résumé"
    )

st.markdown("---")

analyze = st.button("🚀 Générer le Résumé", use_container_width=True)

# --- Extraction Functions ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_file(upload_file):
    if upload_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(upload_file.read()))
    return upload_file.read().decode("utf-8")

def split_text_into_chunks(text, max_chars=8000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end
    return chunks

# --- Main Logic ---
if analyze and upload_file:
    start_time = time.time()
    
    with st.spinner('🔄 Extraction et analyse en cours...'):
        try:
            file_content = extract_text_from_file(upload_file)

            if not file_content.strip():
                st.error("❌ Le fichier est vide.")
                st.stop()

            if len(file_content.strip()) < 50:
                st.warning("⚠️ Le texte est trop court pour être résumé.")
                st.stop()

            # Stats du document
            word_count = len(file_content.split())
            char_count = len(file_content)
            
            st.markdown(f"""
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-label">Mots</div>
                    <div class="stat-value">{word_count:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Caractères</div>
                    <div class="stat-value">{char_count:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Pages estimées</div>
                    <div class="stat-value">{max(1, word_count // 250)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            style_instruction = f" {summary_style}" if summary_style else " de manière concise et factuelle."
            system_role = "Tu es un expert en synthèse de documents."

            chunks = split_text_into_chunks(file_content)
            partial_summaries = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            # --- Résumés partiels ---
            for i, chunk in enumerate(chunks):
                status_text.text(f"📖 Analyse du segment {i+1}/{len(chunks)}...")
                
                response = client.chat.completions.create(
                    model="z-ai/glm-4.5-air:free",
                    messages=[
                        {"role": "system", "content": system_role},
                        {
                            "role": "user",
                            "content": f"Résume ce passage en français{style_instruction}:\n\n{chunk}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=800
                )

                summary = response.choices[0].message.content
                partial_summaries.append(summary)
                progress_bar.progress((i + 1) / len(chunks))

            # --- Fusion finale ---
            status_text.text("🔗 Fusion des résumés...")
            combined_text = "\n\n".join(partial_summaries)

            final_response = client.chat.completions.create(
                model="z-ai/glm-4.5-air:free",
                messages=[
                    {"role": "system", "content": system_role},
                    {
                        "role": "user",
                        "content": f"Fusionne ces résumés en un résumé final cohérent en français{style_instruction}:\n\n{combined_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=1200
            )

            final_summary = final_response.choices[0].message.content
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            status_text.empty()
            progress_bar.empty()

            # --- Résultat Final ---
            st.balloons()
            
            st.markdown(f"""
            <div class="summary-card">
                <h3>📝 Résumé Généré par IA</h3>
                <div class="summary-text">
                    {final_summary.replace('\n', '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Stats finales
            summary_words = len(final_summary.split())
            reduction_rate = ((word_count - summary_words) / word_count) * 100
            
            st.markdown(f"""
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-label">Temps de traitement</div>
                    <div class="stat-value">{processing_time:.1f}s</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Mots résumé</div>
                    <div class="stat-value">{summary_words}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Réduction</div>
                    <div class="stat-value">{reduction_rate:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

elif analyze and not upload_file:
    st.warning("⚠️ Veuillez d'abord charger un fichier !")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-top: 3rem;">
    <p style="margin:0; font-size: 1.1rem;">Développé avec ❤️ | Propulsé par <strong>GLM-4.5-Air</strong> & <strong>Streamlit</strong></p>
    <p style="margin-top: 0.5rem; opacity: 0.9;">© 2026 AI Document Analyzer - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)