import streamlit as st 
import PyPDF2
import io
import os
from google import genai
from dotenv import load_dotenv
from google.genai.types import GenerateContentConfig

# --- Configuration et Initialisation ---
load_dotenv()

st.set_page_config(page_title="Synthèse de Document par IA", page_icon="📝", layout='centered')
st.title("Outil de Synthèse de Document par IA")
st.markdown("Chargez n'importe quel document (PDF ou TXT) pour obtenir un résumé précis et objectif généré par **Gemini 2.5 Flash**.")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("ERREUR : La clé GEMINI_API_KEY est manquante. Assurez-vous que votre fichier .env est correctement configuré.")
    st.stop()

# --- Widgets Streamlit ---
upload_file = st.file_uploader("Charger votre fichier (PDF / TXT)", type=["pdf", "txt"])

# Champ optionnel pour définir le style ou la longueur du résumé
summary_style = st.text_input(
    "Optionnel : Précisez le format de résumé souhaité", 
    placeholder="Ex: En trois points clés, pour un enfant de 10 ans, ou en 200 mots."
)

# Le bouton d'analyse est renommé pour plus de clarté
analyze = st.button('Générer le Résumé 📝')

# --- Fonctions d'Extraction ---

def extract_text_from_pdf(pdf_file):
    """
    Extrait le texte de toutes les pages d'un fichier PDF en mémoire.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "" 
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
    
def extract_text_from_file(upload_file):
    """Détecte le type de fichier et appelle l'extracteur approprié."""
    if upload_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(upload_file.read()))
    # Pour les fichiers TXT, assure la lecture correcte
    return upload_file.read().decode("utf-8")

# --- Logique de Résumé ---

if analyze and upload_file:
    # 0. Utilisation d'un spinner pour l'expérience utilisateur
    with st.spinner("Extraction du texte et synthèse du document par Gemini..."):
        try:
            # 1. Extraction du contenu
            file_content = extract_text_from_file(upload_file)

            if not file_content.strip():
                st.error("Le fichier est vide ou le texte n'a pas pu être extrait. Veuillez vérifier le contenu.")
                st.stop()
            
            # NOUVEAU : Vérification de la longueur minimale (par exemple 50 caractères pour être sûr)
            if len(file_content.strip()) < 50:
                st.warning("Le texte extrait semble trop court pour être résumé (moins de 50 caractères).")
                st.markdown(f"**Contenu extrait :** *{file_content.strip()}*")
                st.stop()

            # --- 2. Construction du Prompt ---
            
            # Instruction spécifique pour le résumé
            style_instruction = f" {summary_style}" if summary_style else " de manière concise et factuelle."

            prompt_content = f"""
            Veuillez lire le document ci-dessous et fournir un résumé EN FRANÇAIS.{style_instruction}
            Le résumé doit capturer les points clés et les informations essentielles du document. S'il n'y a pas assez de contenu pour un résumé, veuillez expliquer brièvement pourquoi.
            
            ---
            CONTENU DU DOCUMENT À RÉSUMER :
            {file_content}
            ---
            """

            # 3. Création du client GenAI
            client = genai.Client(api_key=GEMINI_API_KEY)

            # --- 4. Appel de l'API ---
            
            # Instruction Système (Rôle de l'IA)
            system_role = "Tu es un assistant expert en synthèse de documents. Ton objectif est de résumer efficacement de longs textes en français, en conservant l'information cruciale et le ton de l'original."
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                
                config=GenerateContentConfig(
                    system_instruction=system_role,
                    temperature=0.3, 
                    max_output_tokens=1500 
                ),
                
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt_content}
                        ]
                    }
                ]
            )

            # 5. Affichage du Résultat (Gestion explicite de la réponse vide)
            st.markdown("---")
            st.markdown("### 📝 Résultat de la Synthèse par Gemini")
            
            if response.text and response.text.strip():
                st.markdown(response.text) 
            else:
                st.error("L'IA n'a retourné aucun contenu pour ce document. Cela peut être dû à un texte illisible, non pertinent, ou un problème temporaire de l'API.")
                st.markdown("Veuillez essayer avec un autre fichier ou un format plus simple (TXT).")

        except Exception as e:
            # Gestion des erreurs
            st.error(f"Une erreur est survenue lors du traitement : {str(e)}")
            st.warning("Veuillez vérifier que le fichier est valide et non protégé, ou que la clé API est correcte.")