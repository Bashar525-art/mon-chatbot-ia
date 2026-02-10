import streamlit as st
import os
import shutil
import base64
import tempfile
import io
import speech_recognition as sr
from datetime import datetime  # Pour la date réelle
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument
from gtts import gTTS
from duckduckgo_search import DDGS

# --- CONFIGURATION NEXUS ---
st.set_page_config(page_title="Nexus Omni", page_icon="💠", layout="wide")

if "MISTRAL_API_KEY" not in st.secrets:
    st.error("⚠️ Clé API Mistral manquante dans les Secrets.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
model_default = "pixtral-12b-2409"

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STYLE CSS "PUBLIC & 3D" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
    }

    .nexus-title {
        text-align: center; font-size: 4rem; font-weight: 200; letter-spacing: 15px;
        color: white; text-shadow: 0 0 30px rgba(0, 150, 255, 0.5);
        margin-top: 50px; animation: fadeIn 2s ease-in;
    }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    div[data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px !important; margin-bottom: 10px;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(20px);
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS SYSTÈME ---
def get_pdf_documents(files):
    docs = []
    for f in files:
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text: docs.append(LangChainDocument(page_content=text, metadata={"source": f.name, "page": i+1}))
    return docs

def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_bytes) as source:
            audio_data = r.record(source)
            return r.recognize_google(audio_data, language="fr-FR")
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>N E X U S</h2>", unsafe_allow_html=True)
    st.markdown("---")
    enable_web = st.toggle("🌐 Recherche Web", value=False)
    enable_vocal = st.toggle("🔊 Réponse Vocale", value=False)
    st.markdown("---")
    uploaded_pdfs = st.file_uploader("Fichiers PDF", type="pdf", accept_multiple_files=True)
    uploaded_img = st.file_uploader("Image", type=["jpg", "png"])
    if st.button("🗑️ Nouvelle Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ACCUEIL ---
if not st.session_state.messages:
    st.markdown('<h1 class="nexus-title">NEXUS</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Système Omni-Intelligent. Posez n'importe quelle question.</p>", unsafe_allow_html=True)

# --- CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="💠" if msg["role"]=="assistant" else "▫️"):
        st.markdown(msg["content"])

audio_in = st.audio_input("🎙️")
text_in = st.chat_input("Commandez Nexus...")

query = None
if audio_in:
    with st.spinner("Analyse de la voix..."):
        query = transcribe_audio(audio_in)
elif text_in:
    query = text_in

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="▫️"):
        st.markdown(query)

    # ANIMATION DE RÉFLEXION
    with st.spinner("Nexus réfléchit..."):
        # 1. Préparation de la date réelle (Correction bug 2024/2026)
        now = datetime.now()
        date_str = now.strftime("%A %d %B %Y, %H:%M")
        
        # 2. Contexte documents / Web
        context = ""
        if uploaded_pdfs:
            docs = get_pdf_documents(uploaded_pdfs)
            if docs:
                vector_db = FAISS.from_documents(docs, MistralAIEmbeddings(mistral_api_key=api_key))
                res = vector_db.similarity_search(query, k=3)
                context += "\nDOCUMENTS:\n" + "\n".join([d.page_content for d in res])

        if enable_web:
            try: context += f"\nWEB SEARCH:\n{DDGS().text(query, max_results=2)}"
            except: pass

        # 3. Génération
        client = Mistral(api_key=api_key)
        with st.chat_message("assistant", avatar="💠"):
            placeholder = st.empty()
            full_resp = ""
            
            # PROMPT SYSTÈME AVEC DATE MISE À JOUR
            sys_instr = f"Tu es Nexus. La date et l'heure actuelles sont : {date_str}. Utilise LaTeX pour les maths."
            msgs = [{"role": "system", "content": f"{sys_instr} {context}"}] + st.session_state.messages
            
            try:
                stream = client.chat.stream(model=model_default, messages=msgs)
                for chunk in stream:
                    content = chunk.data.choices[0].delta.content
                    if content:
                        full_resp += content
                        placeholder.markdown(full_resp + "▌")
                placeholder.markdown(full_resp)

                if enable_vocal:
                    tts = gTTS(text=full_resp, lang='fr')
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)

                st.session_state.messages.append({"role": "assistant", "content": full_resp})
            except Exception as e:
                st.error("Nexus est saturé ou le quota API est atteint.")
