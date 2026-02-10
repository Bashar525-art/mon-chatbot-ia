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
st.set_page_config(page_title="Nexus", page_icon="💠", layout="wide")

if "MISTRAL_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Configuration manquante.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
correct_password = st.secrets["APP_PASSWORD"]

# --- LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("<br><br><h1 style='text-align:center; color: white; letter-spacing: 8px;'>N E X U S</h1>", unsafe_allow_html=True)
    if st.button("INITIALISER") or st.text_input("ACCÈS", type="password") == correct_password:
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Système Nexus synchronisé. Mémoire permanente active."}]

# --- STYLE CSS "GLASS & NEON" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    
    .stApp {
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
    }
    
    /* Effet de bordure lumineuse sur les messages */
    div[data-testid="stChatMessage"] {
        border-left: 3px solid rgba(0, 150, 255, 0.5);
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border-radius: 0 15px 15px 0 !important;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stChatMessage"]:hover {
        border-left: 3px solid #0096ff;
        background-color: rgba(255, 255, 255, 0.06) !important;
    }

    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.7); backdrop-filter: blur(25px); }
    
    /* Bouton micro stylisé */
    [data-testid="stAudioInput"] button {
        background-color: #0096ff !important;
        box-shadow: 0 0 15px rgba(0, 150, 255, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE MÉMOIRE ---
DATA_DIR = "data"
INDEX_FOLDER = "nexus_permanent_index"

def load_permanent_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    if not files: return None
    
    all_docs = []
    for f in files:
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text: all_docs.append(LangChainDocument(page_content=text, metadata={"source": os.path.basename(f), "page": i+1}))
    return all_docs

# --- FONCTIONS SYSTÈME ---
def get_vector_store(documents, _api_key):
    embeddings = MistralAIEmbeddings(mistral_api_key=_api_key)
    return FAISS.from_documents(documents, embeddings)

def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_bytes) as source:
            audio_data = r.record(source)
            return r.recognize_google(audio_data, language="fr-FR")
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("💠 NEXUS OMNI")
    
    # SÉLECTEUR DE MODÈLE
    power_mode = st.select_slider("MODE PUISSANCE", options=["Vitesse", "Équilibre", "Maximum"])
    model_map = {"Vitesse": "open-mistral-nemo", "Équilibre": "mistral-small-latest", "Maximum": "mistral-large-latest"}
    chosen_model = model_map[power_mode]
    
    st.divider()
    uploaded_pdfs = st.file_uploader("Ajouter PDFs temporaires", type="pdf", accept_multiple_files=True)
    enable_web = st.toggle("🌍 Accès Web direct", value=False)
    enable_vocal = st.toggle("🔊 Réponse Vocale", value=False)
    
    if st.button("🗑️ PURGER SESSION"):
        st.session_state.messages = []
        st.rerun()

# --- TRAITEMENT DES DONNÉES ---
perm_docs = load_permanent_data()
temp_docs = get_pdf_documents(uploaded_pdfs) if uploaded_pdfs else []
final_docs = (perm_docs or []) + (temp_docs or [])

vector_db = None
if final_docs:
    vector_db = get_vector_store(final_docs, api_key)

# --- CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="💠" if msg["role"]=="assistant" else "▫️"):
        st.markdown(msg["content"])

audio_in = st.audio_input("🎙️")
text_in = st.chat_input("Commandez Nexus...")

query = None
if audio_in:
    query = transcribe_audio(audio_in)
elif text_in:
    query = text_in

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="▫️"):
        st.markdown(query)

    # RECHERCHE CONTEXTE
    context = ""
    if vector_db:
        docs = vector_db.similarity_search(query, k=5)
        context = "\nDOCUMENTS:\n" + "\n".join([d.page_content for d in docs])
    
    if enable_web:
        context += f"\nWEB:\n{DDGS().text(query, max_results=3)}"

    # GÉNÉRATION
    client = Mistral(api_key=api_key)
    with st.chat_message("assistant", avatar="💠"):
        placeholder = st.empty()
        full_resp = ""
        msgs = [{"role": "system", "content": r"Tu es Nexus. Réponds avec précision. LaTeX obligatoire pour maths : $$x^2$$"}] + st.session_state.messages
        
        stream = client.chat.stream(model=chosen_model, messages=msgs)
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
