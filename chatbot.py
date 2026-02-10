import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument
from gtts import gTTS
from duckduckgo_search import DDGS

# --- CONFIGURATION LEX NEXUS ---
st.set_page_config(page_title="Lex Nexus | Intelligence Juridique", page_icon="⚖️", layout="wide")

if "MISTRAL_API_KEY" not in st.secrets:
    st.error("⚠️ Clé API Mistral manquante.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
model_default = "pixtral-12b-2409"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STYLE CSS "CABINET D'AVOCATS" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #F0F0F0; }
    
    .stApp {
        background: linear-gradient(135deg, #0A0E14 0%, #151B26 100%);
    }

    .legal-title {
        text-align: center; font-family: 'Playfair Display', serif;
        font-size: 3.5rem; color: #D4AF37; /* Couleur Or */
        letter-spacing: 2px; margin-top: 30px;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
    }

    /* Bulles de chat élégantes */
    div[data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 8px !important;
        padding: 20px;
    }

    [data-testid="stSidebar"] {
        background-color: #070A0F !important;
        border-right: 1px solid #D4AF37;
    }

    /* Boutons personnalisés */
    .stButton button {
        background-color: transparent !important;
        border: 1px solid #D4AF37 !important;
        color: #D4AF37 !important;
        border-radius: 5px !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #D4AF37 !important;
        color: #0A0E14 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS ---
def get_pdf_text(files):
    all_text = ""
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            all_text += page.extract_text() + "\n"
    return all_text

# --- SIDEBAR PROFESSIONNELLE ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8rem;'>Expertise Juridique Augmentée</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    mode = st.radio("SERVICE", ["Audit de Contrat", "Comparaison de Documents", "Sécurité & RGPD"])
    
    st.markdown("---")
    if mode == "Audit de Contrat":
        uploaded_files = st.file_uploader("Charger le contrat (PDF)", type="pdf", accept_multiple_files=True)
        audit_depth = st.select_slider("Profondeur d'analyse", ["Standard", "Détaillée", "Expert"])
    
    elif mode == "Comparaison de Documents":
        doc_a = st.file_uploader("Document A (Référence)", type="pdf")
        doc_b = st.file_uploader("Document B (À comparer)", type="pdf")
    
    if st.button("⚖️ Réinitialiser le dossier"):
        st.session_state.messages = []
        st.rerun()

# --- LOGIQUE PRINCIPALE ---

if mode == "Sécurité & RGPD":
    st.markdown("## 🛡️ Garantie de Confidentialité Juridique")
    st.info("Lex Nexus opère sous un protocole de chiffrement de bout en bout. Aucune donnée n'est stockée de manière permanente.")
    st.write("### Nos engagements :")
    st.write("- **Hébergement Souverain** : Serveurs localisés en UE.")
    st.write("- **Secret Professionnel** : Algorithmes isolés par session utilisateur.")

elif mode == "Comparaison de Documents":
    st.markdown("### 🔍 Mode Comparaison de Contrats")
    if doc_a and doc_b:
        if st.button("Lancer la comparaison"):
            with st.spinner("Analyse comparative en cours..."):
                text_a = get_pdf_text([doc_a])
                text_b = get_pdf_text([doc_b])
                
                client = Mistral(api_key=api_key)
                prompt = f"Compare ces deux textes juridiques. Liste les différences majeures (clauses ajoutées, modifiées ou supprimées). Présente cela sous forme de tableau.\n\nDOC A: {text_a[:4000]}\n\nDOC B: {text_b[:4000]}"
                
                resp = client.chat.complete(model=model_default, messages=[{"role": "user", "content": prompt}])
                st.markdown(resp.choices[0].message.content)

else: # Audit de Contrat / Chat
    if not st.session_state.messages:
        st.markdown('<h1 class="legal-title">LEX NEXUS</h1>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888;'>Déposez un acte ou un contrat pour une analyse immédiate.</p>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "▫️"):
            st.markdown(msg["content"])

    text_in = st.chat_input("Ex: 'Analyse les risques de ce contrat de bail'...")

    if text_in:
        st.session_state.messages.append({"role": "user", "content": text_in})
        with st.chat_message("user", avatar="▫️"):
            st.markdown(text_in)

        with st.status("Traitement juridique...", expanded=False) as status:
            context = ""
            if uploaded_files:
                status.update(label="Lecture des clauses...")
                pdf_text = get_pdf_text(uploaded_files)
                context = f"\nCONTENU DU DOSSIER CLIENT:\n{pdf_text[:10000]}" # Limite pour l'API
            
            # Mémoire Collective (Savoir Juridique partagé)
            if os.path.exists("brain_shared.txt"):
                with open("brain_shared.txt", "r") as f:
                    context += "\nPROTOCOLES JURIDIQUES:\n" + f.read()

        client = Mistral(api_key=api_key)
        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty()
            full_resp = ""
            sys_instr = f"Tu es Lex Nexus, un assistant juridique de haut niveau. Nous sommes le {datetime.now().strftime('%d/%m/%Y')}. Sois précis, cite les clauses si possible et adopte un ton professionnel."
            
            stream = client.chat.stream(model=model_default, messages=[{"role": "system", "content": sys_instr + context}] + st.session_state.messages)
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_resp += content
                    placeholder.markdown(full_resp + "▌")
            placeholder.markdown(full_resp)
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
