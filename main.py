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
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .hero-section h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.3);
    }
    
    .hero-section p {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin-top: 1rem;
        font-weight: 300;
    }
    
    .main-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
    }
    
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .summary-card h3 {
        color: #2d3748;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        margin: 0.5rem 0;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1>📄 AI Document Analyzer</h1>
    <p>Synthèse intelligente propulsée par GLM-4.5-Air</p>
</div>
""", unsafe_allow_html=True)

# --- API Key (LOGIQUE IDENTIQUE) ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("❌ ERREUR : OPENROUTER_API_KEY manquante dans le fichier .env")
    st.stop()

# --- Initialisation client (LOGIQUE IDENTIQUE) ---
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div class="info-box">
        <h2 style="margin-top:0;">🎯 À propos</h2>
        <p>Synthèse automatique de documents avec <strong>GLM-4.5-Air</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Formats supportés")
    st.markdown("- 📄 **PDF**\n- 📝 **TXT**")
    
    st.markdown("---")
    st.markdown("💡 **Astuce :** Précisez le format souhaité pour un résumé personnalisé !")

# --- Widgets (LOGIQUE IDENTIQUE) ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Upload de document")
    upload_file = st.file_uploader(
        "Chargez votre fichier (PDF / TXT)",
        type=["pdf", "txt"]
    )
    
    if upload_file:
        st.success(f"✅ Fichier chargé : **{upload_file.name}**")

with col2:
    st.markdown("### ⚙️ Format")
    summary_style = st.text_input(
        "Format de résumé",
        placeholder="Ex: En 5 points clés"
    )

st.markdown("---")

analyze = st.button("🚀 Générer le Résumé")

st.markdown('</div>', unsafe_allow_html=True)

# --- Extraction Functions (LOGIQUE IDENTIQUE) ---
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

# --- Logique principale (IDENTIQUE + STATS) ---
if analyze and upload_file:
    start_time = time.time()
    
    with st.spinner("🔄 Extraction et analyse en cours..."):
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
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{word_count:,}</div>
                    <div class="stat-label">Mots</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{char_count:,}</div>
                    <div class="stat-label">Caractères</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{max(1, word_count // 250)}</div>
                    <div class="stat-label">Pages ~</div>
                </div>
                """, unsafe_allow_html=True)

            style_instruction = f" {summary_style}" if summary_style else " de manière concise et factuelle."
            system_role = "Tu es un expert en synthèse de documents."

            chunks = split_text_into_chunks(file_content)
            partial_summaries = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            # --- Résumés partiels (LOGIQUE IDENTIQUE) ---
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

            # --- Fusion finale (LOGIQUE IDENTIQUE) ---
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

            # --- Affichage résultat avec design ---
            st.balloons()
            
            st.markdown(f"""
            <div class="summary-card">
                <h3>📝 Résumé Généré par IA</h3>
                <div style="color: #4a5568; font-size: 1.05rem; line-height: 1.8;">
                    {final_summary.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Stats finales
            summary_words = len(final_summary.split())
            reduction_rate = ((word_count - summary_words) / word_count) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{processing_time:.1f}s</div>
                    <div class="stat-label">Temps</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary_words}</div>
                    <div class="stat-label">Mots résumé</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{reduction_rate:.0f}%</div>
                    <div class="stat-label">Réduction</div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

elif analyze and not upload_file:
    st.warning("⚠️ Veuillez d'abord charger un fichier !")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-top: 2rem;">
    <p style="margin:0; font-size: 1.1rem;">Développé avec ❤️ | Propulsé par <strong>GLM-4.5-Air</strong></p>
</div>
""", unsafe_allow_html=True)