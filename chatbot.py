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
st.set_page_config(page_title="UltraBrain AI", page_icon="🧠", layout="wide")

if "MISTRAL_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Secrets manquants. Vérifiez .streamlit/secrets.toml")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
correct_password = st.secrets["APP_PASSWORD"]
model = "pixtral-12b-2409"

# --- LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center;'>🔒 Accès Privé</h1>", unsafe_allow_html=True)
    if st.button("Entrer") or st.text_input("Mot de passe", type="password") == correct_password:
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salut ! Je suis là. On parle de quoi ?"}]

# --- STYLE CSS (MICRO EN HAUT A DROITE) ---
st.markdown("""
<style>
    h1 {
        background: -webkit-linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        text-align: center;
        font-size: 2rem;
    }
    .stChatMessage { border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}
    
    /* 🎤 LE FIX DU MICRO : On le place en HAUT à DROITE (Zone sécurisée) */
    [data-testid="stAudioInput"] {
        position: fixed;
        top: 70px;           /* Tout en haut (sous la barre de titre) */
        right: 15px;         /* Collé à droite */
        z-index: 9999;
        width: fit-content !important;
    }
    
    [data-testid="stAudioInput"] > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Bouton Rouge Style Talkie-Walkie */
    [data-testid="stAudioInput"] button {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
        border: 2px solid white !important;
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧰 Outils")
    uploaded_pdf = st.file_uploader("📄 PDF", type="pdf")
    uploaded_img = st.file_uploader("🖼️ Image", type=["jpg", "png"])
    st.divider()
    enable_web = st.toggle("🌍 Internet", value=False)
    enable_audio_out = st.toggle("🔊 Audio", value=False)
    st.divider()
    if st.button("🗑️ Reset", type="primary"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER): shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- MAIN ---
st.title("🧠 UltraBrain")

vector_db = None
if uploaded_pdf:
    raw = get_pdf_documents(uploaded_pdf)
    if raw:
        vector_db = get_vector_store(raw, api_key)
        if vector_db: st.toast("PDF Mémorisé !", icon="🧠")

# Affichage Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"])

# --- INPUTS ---
audio_val = st.audio_input("🎙️")
text_val = st.chat_input("Message...")

final_question = None

if audio_val:
    with st.spinner("🎧 Analyse..."):
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
        context_str += "\nPDF:\n" + "\n".join([d.page_content for d in docs])
        sources = list(set([f"Page {d.metadata['page']}" for d in docs]))

    if enable_web:
        context_str += f"\nWEB:\n{search_web(final_question)}"

    base_instr = """Tu es une IA généraliste, amicale et experte. 
    Adapte-toi au ton de l'utilisateur. Utilise LaTeX ($x^2$) pour les maths."""
    
    if uploaded_img:
        sys_prompt = f"Vision active. Analyse l'image. {base_instr}"
        base64_img = encode_image(uploaded_img)
        msgs_api = [{"role": "user", "content": [{"type": "text", "text": final_question}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}]}]
    else:
        msgs_api = [{"role": "system", "content": f"{base_instr} Contexte: {context_str}"}] + [m for m in st.session_state.messages if m["role"]!="system"]

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
            if sources: st.caption(f"📚 {', '.join(sources)}")
            if enable_audio_out:
                audio_file = text_to_speech(full_resp)
                if audio_file: st.audio(audio_file)
            
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e:
            st.error(f"Erreur : {e}")
