import streamlit as st
import os
import shutil
import base64
import tempfile
import speech_recognition as sr
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from gtts import gTTS
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
st.set_page_config(page_title="UltraBrain Nexus", page_icon="💠", layout="wide")

if "MISTRAL_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Secrets manquants. Vérifiez .streamlit/secrets.toml")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
correct_password = st.secrets["APP_PASSWORD"]
model = "pixtral-12b-2409"

# --- LOGIN STYLE FUTURISTE ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stTextInput input { text-align: center; font-size: 1.2rem; letter-spacing: 3px; }
    </style>
    <h1 style='text-align:center; font-family: sans-serif; letter-spacing: 2px; background: -webkit-linear-gradient(0deg, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>💠 NEXUS ACCESS</h1>
    """, unsafe_allow_html=True)
    if st.button("INITIALISER SESSION") or st.text_input("IDENTIFIANT SECURISE", type="password") == correct_password:
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Initialisation terminée. Je suis le Nexus. Vision, Audition et Connexion Globale actives. En attente d'instructions."}]

# --- 🎨 STYLE CSS ULTRA-MODERNE (AURORA THEME) ---
st.markdown("""
<style>
    /* IMPORT D'UNE POLICE MODERNE (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* FOND ANIME "AURORA" */
    .stApp {
        background: radial-gradient(at top left, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }

    /* TITRE PRINCIPAL CYBERPUNK */
    h1 {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* SIDEBAR EFFET VERRE */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* BULLES DE CHAT MODERNES */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    /* Bulle utilisateur avec dégradé */
    div[data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #3b2667 10%, #bc78ec 100%) !important;
        border: none;
    }

    /* CACHER LES MENUS INUTILES */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}
    
    /* --- 🎙️ LE HACK DU MICRO MODERNE --- */
    
    /* 1. Positionnement en haut à droite (Zone Talkie-Walkie) */
    [data-testid="stAudioInput"] {
        position: fixed;
        top: 80px;
        right: 25px;
        z-index: 9999;
        width: fit-content !important;
    }
    
    /* 2. Rendre le conteneur transparent */
    [data-testid="stAudioInput"] > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* 3. HACK : Cacher le vieil emoji moche à l'intérieur du bouton */
    [data-testid="stAudioInput"] button > div {
        display: none !important;
    }
    
    /* 4. Remplacer par une icône SVG moderne en background */
    [data-testid="stAudioInput"] button {
        /* Icône SVG blanche moderne */
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke-width='1.5' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 0 1 6 0v8.25a3 3 0 0 1-3 3Z' /%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 28px;
        
        background-color: #FF4B4B !important; /* Couleur de fond du bouton */
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.6); /* Lueur moderne */
        border: 2px solid rgba(255,255,255,0.8) !important;
        transition: all 0.3s ease;
    }
    /* Effet au survol */
    [data-testid="stAudioInput"] button:hover {
        transform: scale(1.1);
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.9);
    }
</style>
""", unsafe_allow_html=True)

INDEX_FOLDER = "faiss_index_mistral"

# --- FONCTIONS ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_pdf_documents(pdf_file):
    docs = []
    try:
        reader = PdfReader(pdf_file)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text: docs.append(Document(page_content=text, metadata={"page": i + 1}))
        return docs
    except: return None

def get_vector_store(documents, _api_key):
    embeddings = MistralAIEmbeddings(mistral_api_key=_api_key)
    if os.path.exists(INDEX_FOLDER):
        try: return FAISS.load_local(INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True)
        except: pass
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(splits, embeddings)
        vector_store.save_local(INDEX_FOLDER)
        return vector_store
    except: return None

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='fr')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except: return None

def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except: return "Pas de résultats web."

def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_bytes) as source:
            audio_data = r.record(source)
            return r.recognize_google(audio_data, language="fr-FR")
    except: return None

# --- SIDEBAR MODERNE ---
with st.sidebar:
    st.markdown("<h3 style='text-align:center;'>🎛️ SYSTÈME</h3>", unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("📄 Charger Données (PDF)", type="pdf")
    uploaded_img = st.file_uploader("🖼️ Charger Visuel (IMG)", type=["jpg", "png"])
    st.divider()
    col1, col2 = st.columns(2)
    with col1: enable_web = st.toggle("🌍 Net", value=False)
    with col2: enable_audio_out = st.toggle("🔊 Vocal", value=False)
    st.divider()
    if st.button("🔄 REBOOT SYSTÈME", type="primary", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER): shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- MAIN ---
st.title("💠 UltraBrain NEXUS")

vector_db = None
if uploaded_pdf:
    raw = get_pdf_documents(uploaded_pdf)
    if raw:
        vector_db = get_vector_store(raw, api_key)
        if vector_db: st.toast("Données intégrées au Nexus.", icon="💠")

# Affichage Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"])

# --- INPUTS ---
# Le micro est géré par le CSS en haut à droite avec la nouvelle icône
audio_val = st.audio_input("🎙️")
text_val = st.chat_input("Entrez votre requête au Nexus...")

final_question = None

if audio_val:
    with st.spinner("📼 Analyse du flux audio..."):
        transcribed = transcribe_audio(audio_val)
        if transcribed: final_question = transcribed
elif text_val:
    final_question = text_val

# --- LOGIQUE ---
if final_question:
    st.session_state.messages.append({"role": "user", "content": final_question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_question)
        if uploaded_img: st.image(uploaded_img, width=200)

    context_str = ""
    sources = []
    
    if vector_db and not uploaded_img:
        docs = vector_db.similarity_search(final_question, k=3)
        context_str += "\nBASE DE DONNÉES PDF:\n" + "\n".join([d.page_content for d in docs])
        sources = list(set([f"Page {d.metadata['page']}" for d in docs]))

    if enable_web:
        context_str += f"\nFLUX WEB EN TEMPS RÉEL:\n{search_web(final_question)}"

    base_instr = """Tu es le NEXUS, une IA de pointe, futuriste et omnisciente. 
    Ton ton est direct, précis, moderne, parfois avec une pointe d'humour technologique.
    Utilise LaTeX ($x^2$) pour les maths."""
    
    if uploaded_img:
        sys_prompt = f"Analyse visuelle activée. {base_instr}"
        base64_img = encode_image(uploaded_img)
        msgs_api = [{"role": "user", "content": [{"type": "text", "text": final_question}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}]}]
    else:
        msgs_api = [{"role": "system", "content": f"{base_instr} Données Contexte: {context_str}"}] + [m for m in st.session_state.messages if m["role"]!="system"]

    client = Mistral(api_key=api_key)
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_resp = ""
        try:
            stream = client.chat.stream(model=model, messages=msgs_api)
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_resp += content
                    placeholder.markdown(full_resp + "▌")
            
            placeholder.markdown(full_resp)
            if sources: st.caption(f"💠 Sources: {', '.join(sources)}")
            if enable_audio_out:
                audio_file = text_to_speech(full_resp)
                if audio_file: st.audio(audio_file)
            
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e:
            st.error(f"Erreur système : {e}")
