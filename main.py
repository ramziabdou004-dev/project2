import streamlit as st
import PyPDF2
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

# --- Configuration page ---
st.set_page_config(
    page_title="Synthèse de Document par IA",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Outil de Synthèse de Document par IA")
st.markdown("Chargez un document (PDF ou TXT) pour obtenir un résumé généré par GLM-4.5-Air.")

# --- API Key ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("ERREUR : OPENROUTER_API_KEY manquante dans le fichier .env")
    st.stop()

# --- Initialisation client OpenRouter ---
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# --- Widgets ---
upload_file = st.file_uploader("Charger votre fichier (PDF / TXT)", type=["pdf", "txt"])

summary_style = st.text_input(
    "Optionnel : Précisez le format de résumé souhaité",
    placeholder="Ex: En 5 points clés ou en 200 mots."
)

analyze = st.button("Générer le Résumé 📝")

# --- Extraction PDF ---
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

# --- Découpage intelligent ---
def split_text_into_chunks(text, max_chars=8000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end
    return chunks

# --- Logique principale ---
if analyze and upload_file:
    with st.spinner("Extraction et analyse en cours..."):

        try:
            file_content = extract_text_from_file(upload_file)

            if not file_content.strip():
                st.error("Le fichier est vide.")
                st.stop()

            if len(file_content.strip()) < 50:
                st.warning("Le texte est trop court pour être résumé.")
                st.stop()

            style_instruction = f" {summary_style}" if summary_style else " de manière concise et factuelle."

            system_role = "Tu es un expert en synthèse de documents."

            chunks = split_text_into_chunks(file_content)

            partial_summaries = []
            progress_bar = st.progress(0)

            # --- Résumés partiels ---
            for i, chunk in enumerate(chunks):

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

            st.markdown("---")
            st.markdown("### 📝 Résumé Final")
            st.markdown(final_summary)

        except Exception as e:
            st.error(f"Erreur : {str(e)}")