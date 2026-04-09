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
    
    .stFileUploader {
        background: white;
        border-radius: 15px;
        padding: 2rem;
    }
    
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
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .summary-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1);
        border-left: 6px solid #667eea;
        position: relative;
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
    
    .stAlert {
        border-radius: 15px;
        border: none;
        padding: 1.5rem;
        font-size: 1rem;
    }
    
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
    
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
    
    .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
    .feature-title { font-weight: 700; font-size: 1.2rem; color: #2d3748; margin-bottom: 0.5rem; }
    .feature-desc { color: #718096; font-size: 0.95rem; }

    /* ===== CHAT SECTION ===== */
    .chat-section {
        background: white;
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.12);
        border-top: 6px solid #764ba2;
    }

    .chat-section h3 {
        color: #2d3748;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }

    .chat-message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .chat-message-ai {
        background: #f7f8fc;
        color: #2d3748;
        border-radius: 18px 18px 18px 4px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
        font-size: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        line-height: 1.7;
    }

    .chat-label-user {
        text-align: right;
        font-size: 0.75rem;
        color: #a0aec0;
        margin-bottom: 2px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .chat-label-ai {
        font-size: 0.75rem;
        color: #a0aec0;
        margin-bottom: 2px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .tab-section {
        background: white;
        border-radius: 20px;
        padding: 0.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1>📄 AI Document Analyzer</h1>
    <p>Synthèse intelligente & interrogation de vos documents en quelques secondes</p>
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

# --- Session State pour le chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_content" not in st.session_state:
    st.session_state.file_content = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div class="info-box">
        <h2 style="margin-top:0;">🎯 À propos</h2>
        <p>Cet outil utilise <strong>GLM-4.5-Air</strong>, un modèle d'IA avancé pour analyser et répondre à vos questions sur vos documents.</p>
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
            <div class="feature-icon">💬</div>
            <div class="feature-title">Chat IA</div>
            <div class="feature-desc">Interrogez vos docs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Bouton pour vider l'historique du chat
    if st.session_state.chat_history:
        if st.button("🗑️ Effacer l'historique du chat"):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("💡 **Astuce :** Après avoir chargé un fichier, posez directement vos questions dans l'onglet **Chat** !")

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
        
        # Extraire et stocker le contenu dans session_state
        if st.session_state.file_name != upload_file.name:
            raw_bytes = upload_file.read()
            upload_file.seek(0)
            
            if upload_file.type == "application/pdf":
                extracted = extract_text_from_pdf(io.BytesIO(raw_bytes))
            else:
                extracted = raw_bytes.decode("utf-8")
            
            st.session_state.file_content = extracted
            st.session_state.file_name = upload_file.name
            st.session_state.chat_history = []  # Reset chat quand nouveau fichier

with col2:
    st.markdown("### ⚙️ Paramètres")
    summary_style = st.text_input(
        "Format de résumé",
        placeholder="Ex: En 5 points clés",
        help="Précisez comment vous voulez le résumé"
    )

st.markdown("---")

# --- TABS : Résumé | Chat ---
if st.session_state.file_content:
    tab1, tab2 = st.tabs(["📝 Générer un Résumé", "💬 Interroger le Document"])

    # ===========================
    # TAB 1 : RÉSUMÉ
    # ===========================
    with tab1:
        analyze = st.button("🚀 Générer le Résumé", use_container_width=True)
        
        if analyze:
            file_content = st.session_state.file_content
            start_time = time.time()
            
            with st.spinner('🔄 Extraction et analyse en cours...'):
                try:
                    if not file_content.strip():
                        st.error("❌ Le fichier est vide.")
                        st.stop()

                    if len(file_content.strip()) < 50:
                        st.warning("⚠️ Le texte est trop court pour être résumé.")
                        st.stop()

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

                    for i, chunk in enumerate(chunks):
                        status_text.text(f"📖 Analyse du segment {i+1}/{len(chunks)}...")
                        
                        response = client.chat.completions.create(
                            model="z-ai/glm-4.5-air:free",
                            messages=[
                                {"role": "system", "content": system_role},
                                {"role": "user", "content": f"Résume ce passage en français{style_instruction}:\n\n{chunk}"}
                            ],
                            temperature=0.3,
                            max_tokens=800
                        )
                        partial_summaries.append(response.choices[0].message.content)
                        progress_bar.progress((i + 1) / len(chunks))

                    status_text.text("🔗 Fusion des résumés...")
                    combined_text = "\n\n".join(partial_summaries)

                    final_response = client.chat.completions.create(
                        model="z-ai/glm-4.5-air:free",
                        messages=[
                            {"role": "system", "content": system_role},
                            {"role": "user", "content": f"Fusionne ces résumés en un résumé final cohérent en français{style_instruction}:\n\n{combined_text}"}
                        ],
                        temperature=0.3,
                        max_tokens=1200
                    )

                    final_summary = final_response.choices[0].message.content
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    status_text.empty()
                    progress_bar.empty()

                    st.balloons()
                    
                    st.markdown(f"""
                    <div class="summary-card">
                        <h3>📝 Résumé Généré par IA</h3>
                        <div class="summary-text">
                            {final_summary.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
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

    # ===========================
    # TAB 2 : CHAT
    # ===========================
    with tab2:
        st.markdown("""
        <div class="chat-section">
            <h3>💬 Interrogez votre document</h3>
            <p style="color:#718096; margin-bottom:0;">Posez n'importe quelle question sur le contenu du fichier chargé.</p>
        </div>
        """, unsafe_allow_html=True)

        # Affichage de l'historique du chat
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-label-user">Vous</div>
                <div class="chat-message-user">{msg["content"]}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-label-ai">🤖 IA</div>
                <div class="chat-message-ai">{msg["content"].replace(chr(10), '<br>')}</div>
                """, unsafe_allow_html=True)

        # Zone de saisie
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form(key="chat_form", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                user_question = st.text_input(
                    "",
                    placeholder="Ex: Quels sont les points principaux ? Quelle est la conclusion ?",
                    label_visibility="collapsed"
                )
            with col_btn:
                send = st.form_submit_button("📨 Envoyer", use_container_width=True)

        if send and user_question.strip():
            file_content = st.session_state.file_content

            # Tronquer le contenu si trop long pour le contexte
            max_context_chars = 12000
            context = file_content[:max_context_chars]
            if len(file_content) > max_context_chars:
                context += "\n\n[... document tronqué pour la longueur ...]"

            # Construire les messages avec historique
            system_prompt = (
                "Tu es un assistant expert en analyse de documents. "
                "Réponds en français uniquement en te basant sur le contenu du document fourni. "
                "Si la réponse ne se trouve pas dans le document, dis-le clairement."
            )

            messages_for_api = [{"role": "system", "content": system_prompt}]
            
            # Ajouter le contexte du document dans le premier message utilisateur
            messages_for_api.append({
                "role": "user",
                "content": f"Voici le contenu du document :\n\n{context}\n\n---\n\nQuestion : {user_question}"
            })

            # Ajouter l'historique de la conversation (sans re-dupliquer le contexte)
            for i, msg in enumerate(st.session_state.chat_history):
                if i == 0 and msg["role"] == "user":
                    continue  # déjà inclus via le contexte
                messages_for_api.append(msg)

            # Ajouter la question actuelle si historique non vide
            if st.session_state.chat_history:
                messages_for_api.append({"role": "user", "content": user_question})

            # Stocker la question dans l'historique
            st.session_state.chat_history.append({"role": "user", "content": user_question})

            with st.spinner("🤔 L'IA réfléchit..."):
                try:
                    response = client.chat.completions.create(
                        model="z-ai/glm-4.5-air:free",
                        messages=messages_for_api,
                        temperature=0.3,
                        max_tokens=1000
                    )
                    answer = response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de la réponse : {str(e)}")

        elif send and not user_question.strip():
            st.warning("⚠️ Veuillez saisir une question avant d'envoyer.")

else:
    # Si aucun fichier chargé, afficher le bouton résumé normal
    analyze = st.button("🚀 Générer le Résumé", use_container_width=True)
    if analyze:
        st.warning("⚠️ Veuillez d'abord charger un fichier !")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-top: 3rem;">
    <p style="margin:0; font-size: 1.1rem;">Développé avec ❤️ | Propulsé par <strong>GLM-4.5-Air</strong> & <strong>Streamlit</strong></p>
    <p style="margin-top: 0.5rem; opacity: 0.9;">© 2026 AI Document Analyzer - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)