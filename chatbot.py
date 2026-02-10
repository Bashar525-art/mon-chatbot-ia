import streamlit as st
import os
import shutil
import base64
import tempfile
import io
import speech_recognition as sr
from datetime import datetime
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
    st.error("⚠️ Clé API Mistral manquante.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
model_default = "pixtral-12b-2409"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STYLE CSS ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    .stApp { background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%); overflow-x: hidden; }
    .nexus-title { text-align: center; font-size: 4rem; font-weight: 200; letter-spacing: 15px; color: white; text-shadow: 0 0 30px rgba(0, 150, 255, 0.5); margin-top: 50px; }
    div[data-testid="stChatMessage"] { background-color: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 15px !important; margin-bottom: 10px; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.8) !important; backdrop-filter: blur(20px); }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS ---
def get_pdf_documents(files):
    docs = []
    for f in files:
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text: docs.append(LangChainDocument(page_content=text, metadata={"source": f.name, "page": i+1}))
    return docs

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>N E X U S</h2>", unsafe_allow_html=True)
    st.markdown("---")
    enable_web = st.toggle("🌐 Recherche Web", value=False)
    enable_vocal = st.toggle("🔊 Réponse Vocale", value=False)
    st.markdown("---")
    uploaded_pdfs = st.file_uploader("Fichiers PDF (Optionnel)", type="pdf", accept_multiple_files=True)
    if st.button("🗑️ Nouvelle Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not st.session_state.messages:
    st.markdown('<h1 class="nexus-title">NEXUS</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Prêt pour toute commande.</p>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="💠" if msg["role"]=="assistant" else "▫️"):
        st.markdown(msg["content"])

text_in = st.chat_input("Posez votre question...")

if text_in:
    st.session_state.messages.append({"role": "user", "content": text_in})
    with st.chat_message("user", avatar="▫️"):
        st.markdown(text_in)

    # --- LOGIQUE DE RÉPONSE ÉCLAIR ---
    context = ""
    date_str = datetime.now().strftime("%A %d %B %Y, %H:%M")
    
    # On ne crée un spinner "Réflexion" que si des outils lourds sont activés
    with st.status("Nexus analyse...", expanded=False) as status:
        # Recherche PDF : Uniquement si l'utilisateur a chargé des fichiers
        if uploaded_pdfs:
            status.update(label="Analyse des documents...")
            docs = get_pdf_documents(uploaded_pdfs)
            if docs:
                vector_db = FAISS.from_documents(docs, MistralAIEmbeddings(mistral_api_key=api_key))
                res = vector_db.similarity_search(text_in, k=3)
                context += "\nCONNAISSANCE DOCS:\n" + "\n".join([d.page_content for d in res])
        
        # Recherche Web : Uniquement si activé
        if enable_web:
            status.update(label="Recherche sur le web...")
            try: context += f"\nINFO WEB:\n{DDGS().text(text_in, max_results=2)}"
            except: pass
        
        status.update(label="Génération de la réponse...", state="complete", expanded=False)

    # GÉNÉRATION FINALE
    client = Mistral(api_key=api_key)
    with st.chat_message("assistant", avatar="💠"):
        placeholder = st.empty()
        full_resp = ""
        sys_instr = f"Tu es Nexus. Date : {date_str}. Sois direct. Si c'est une question simple, réponds en une phrase."
        msgs = [{"role": "system", "content": f"{sys_instr} {context}"}] + st.session_state.messages
        
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
