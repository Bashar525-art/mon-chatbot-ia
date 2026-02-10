import streamlit as st
import os
import shutil
import base64
import tempfile
import io
import speech_recognition as sr
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument
from gtts import gTTS
from duckduckgo_search import DDGS
from docx import Document as WordDocument

# --- CONFIGURATION NEXUS ---
st.set_page_config(page_title="Nexus Omni", page_icon="💠", layout="wide")

# Récupération de la clé API uniquement (le mot de passe n'est plus requis pour l'accès)
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("⚠️ Clé API Mistral manquante dans les Secrets.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
model_default = "pixtral-12b-2409"

# --- INITIALISATION DE LA SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STYLE CSS "PUBLIC & 3D" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        overflow-x: hidden;
    }

    /* Animation d'entrée pour le titre */
    .nexus-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 200;
        letter-spacing: 15px;
        color: white;
        text-shadow: 0 0 30px rgba(0, 150, 255, 0.5);
        margin-top: 50px;
        animation: fadeIn 2s ease-in;
    }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    /* Bulles de chat stylisées */
    div[data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px !important;
        margin-bottom: 10px;
    }

    /* Sidebar futuriste */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(20px);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR PUBLIQUE ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>N E X U S</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("🌐 **Outils disponibles :**")
    enable_web = st.toggle("Recherche Web Temps Réel", value=False)
    enable_vocal = st.toggle("Synthèse Vocale", value=False)
    
    st.markdown("---")
    uploaded_pdfs = st.file_uploader("Analysez vos documents (PDF)", type="pdf", accept_multiple_files=True)
    uploaded_img = st.file_uploader("Analysez une image", type=["jpg", "png"])
    
    if st.button("🗑️ Nouvelle Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- LOGIQUE DE TRAITEMENT ---
def get_pdf_documents(files):
    docs = []
    for f in files:
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text: docs.append(LangChainDocument(page_content=text, metadata={"source": f.name, "page": i+1}))
    return docs

# Affichage de l'accueil si aucun message
if not st.session_state.messages:
    st.markdown('<h1 class="nexus-title">NEXUS</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Intelligence Artificielle Universelle. Posez une question ou déposez un fichier.</p>", unsafe_allow_html=True)

# --- INTERFACE DE CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="💠" if msg["role"]=="assistant" else "▫️"):
        st.markdown(msg["content"])

# Gestion des entrées (Audio ou Texte)
audio_in = st.audio_input("🎙️")
text_in = st.chat_input("Posez votre question à Nexus...")

query = None
if audio_in:
    # (Logique de transcription simplifiée pour l'exemple)
    query = "L'utilisateur a envoyé un message audio." 
elif text_in:
    query = text_in

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="▫️"):
        st.markdown(query)

    # Préparation du contexte
    context = ""
    if uploaded_pdfs:
        docs = get_pdf_documents(uploaded_pdfs)
        vector_db = FAISS.from_documents(docs, MistralAIEmbeddings(mistral_api_key=api_key))
        search_results = vector_db.similarity_search(query, k=3)
        context = "\nCONTEXTE PDF:\n" + "\n".join([d.page_content for d in search_results])

    if enable_web:
        context += f"\nWEB:\n{DDGS().text(query, max_results=2)}"

    # Appel API Mistral
    client = Mistral(api_key=api_key)
    with st.chat_message("assistant", avatar="💠"):
        placeholder = st.empty()
        full_resp = ""
        
        # Instruction système
        sys_msg = r"Tu es Nexus, une IA publique. Sois clair et utilise LaTeX pour les maths : $$E=mc^2$$."
        msgs = [{"role": "system", "content": f"{sys_msg} {context}"}] + st.session_state.messages
        
        stream = client.chat.stream(model=model_default, messages=msgs)
        for chunk in stream:
            content = chunk.data.choices[0].delta.content
            if content:
                full_resp += content
                placeholder.markdown(full_resp + "▌")
        placeholder.markdown(full_resp)
        
        st.session_state.messages.append({"role": "assistant", "content": full_resp})
