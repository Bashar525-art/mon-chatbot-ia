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
    st.error("⚠️ Configuration manquante. Vérifiez les Secrets.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
correct_password = st.secrets["APP_PASSWORD"]
model = "pixtral-12b-2409"

# --- LOGIN NEXUS ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stTextInput input { text-align: center; border-radius: 10px; letter-spacing: 2px; }
        div[data-testid="stAppViewContainer"] { background-color: #050505; }
    </style>
    <br><br><br>
    <h1 style='text-align:center; color: white; font-weight: 200; letter-spacing: 8px; font-size: 3rem;'>N E X U S</h1>
    <p style='text-align:center; color: #666; font-size: 0.8rem; letter-spacing: 2px;'>SYSTEM ACCESS</p>
    """, unsafe_allow_html=True)
    if st.button("INITIALISER") or st.text_input("CODE D'ACCÈS", type="password") == correct_password:
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Nexus en ligne. Prêt."}]

# --- STYLE CSS "NÉBULEUSE AURORE" (DESIGN FINAL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    
    /* --- FOND ANIMÉ "NÉBULEUSE" --- */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 10% 30%, rgb(23, 20, 65) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgb(45, 15, 70) 0px, transparent 50%),
            radial-gradient(at 50% 50%, #080815 0%, #000000 100%);
        background-size: 300% 300%;
        animation: aurora 25s ease infinite;
    }
    @keyframes aurora {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* TITRE */
    h1 { color: #ffffff; font-weight: 600; text-align: center; letter-spacing: -1px; margin-bottom: 10px; text-shadow: 0 0 20px rgba(0, 150, 255, 0.3); }
    
    /* SIDEBAR (EFFET VERRE) */
    [data-testid="stSidebar"] { background-color: rgba(5, 5, 5, 0.6); border-right: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); }
    
    /* MESSAGES */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    /* Bulle IA */
    div[data-testid="stChatMessage"][data-testid*="assistant"] > div { 
        background-color: rgba(18, 18, 18, 0.7) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 12px !important; 
        padding: 15px; 
        backdrop-filter: blur(5px);
    }
    /* Bulle Utilisateur */
    div[data-testid="stChatMessage"][data-testid*="user"] > div { 
        background-color: rgba(40, 40, 60, 0.8) !important; 
        color: white !important; 
        border-radius: 12px !important; 
        padding: 15px; 
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* INPUT */
    .stChatInput textarea { background-color: rgba(10, 10, 10, 0.8) !important; color: white !important; border: 1px solid rgba(51, 51, 51, 0.5) !important; border-radius: 12px !important; backdrop-filter: blur(5px); }
    
    /* CACHER */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}
    
    /* MICROPHONE HAUT DROITE */
    [data-testid="stAudioInput"] { position: fixed; top: 70px; right: 20px; z-index: 9999; width: fit-content !important; }
    [data-testid="stAudioInput"] > div { background-color: transparent !important; border: none !important; }
    [data-testid="stAudioInput"] button {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke-width='1.5' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 0 1 6 0v8.25a3 3 0 0 1-3 3Z' /%3E%3C/svg%3E");
        background-repeat: no-repeat; background-position: center; background-size: 24px;
        background-color: #1A1A1A !important; border: 1px solid #444 !important; border-radius: 50% !important; width: 55px !important; height: 55px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    [data-testid="stAudioInput"] button > div { display: none !important; }
</style>
""", unsafe_allow_html=True)

INDEX_FOLDER = "faiss_index_mistral"

# --- FONCTIONS ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_pdf_documents(uploaded_files):
    all_docs = []
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]  
    for pdf_file in uploaded_files:
        try:
            reader = PdfReader(pdf_file)
            filename = pdf_file.name
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text: all_docs.append(LangChainDocument(page_content=text, metadata={"source": filename, "page": i + 1}))
        except: continue
    return all_docs

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

def create_word_docx(messages):
    doc = WordDocument()
    doc.add_heading('Rapport NEXUS', 0)
    for msg in messages:
        role = "NEXUS" if msg["role"] == "assistant" else "UTILISATEUR"
        doc.add_heading(role, level=2)
        doc.add_paragraph(msg["content"])
        doc.add_paragraph("_" * 20)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

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
    st.markdown("<h3 style='color:white; letter-spacing:2px; text-align:center;'>N E X U S</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:10px 0; border-color:#333;'>", unsafe_allow_html=True)
    
    uploaded_pdfs = st.file_uploader("Sources (PDF)", type="pdf", accept_multiple_files=True)
    uploaded_img = st.file_uploader("Visuel (IMG)", type=["jpg", "png"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: enable_web = st.toggle("Net", value=False)
    with col2: enable_audio_out = st.toggle("Vocal", value=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if len(st.session_state.messages) > 1:
        docx_file = create_word_docx(st.session_state.messages)
        st.download_button("📄 Export Word", data=docx_file, file_name="Nexus_Rapport.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

    if st.button("🔴 Purger Mémoire", type="primary", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER): shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- MAIN ---
st.title("Nexus")

vector_db = None
if uploaded_pdfs:
    raw = get_pdf_documents(uploaded_pdfs)
    if raw:
        vector_db = get_vector_store(raw, api_key)
        if vector_db: st.toast(f"{len(uploaded_pdfs)} fichiers intégrés.", icon="💠")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="▫️" if msg["role"]=="user" else "💠"):
        st.markdown(msg["content"])

audio_val = st.audio_input("🎙️")
text_val = st.chat_input("Ordre pour Nexus...")

final_question = None
if audio_val:
    with st.spinner("Analyse audio..."):
        transcribed = transcribe_audio(audio_val)
        if transcribed: final_question = transcribed
elif text_val:
    final_question = text_val

if final_question:
    st.session_state.messages.append({"role": "user", "content": final_question})
    with st.chat_message("user", avatar="▫️"):
        st.markdown(final_question)
        if uploaded_img: st.image(uploaded_img, width=200)

    context_str = ""
    sources = []
    
    if vector_db and not uploaded_img:
        docs = vector_db.similarity_search(final_question, k=4)
        context_str += "\nNEXUS DATABASE:\n" + "\n".join([d.page_content for d in docs])
        sources = list(set([f"{d.metadata['source']} (p.{d.metadata['page']})" for d in docs]))

    if enable_web:
        context_str += f"\nNEXUS WEB SEARCH:\n{search_web(final_question)}"

   base_instr = """
    Tu es Nexus, une Intelligence Artificielle avancée.
    Ton style est : Précis, Synthétique, Élégant et Direct.
    Ne joue pas de rôle de robot, sois une extension intellectuelle de l'utilisateur.

    RÈGLE ABSOLUE POUR LES FORMULES (Maths, Logique, Éco...) :
    Tu DOIS utiliser des doubles dollars `$$` pour TOUTE expression mathématique ou logique, même courte.
    Exemple : $$ E = mc^2 $$ ou $$ P_A \uparrow \rightarrow Q_B \uparrow $$
    N'utilise JAMAIS de simples dollars `$`.
    """
    
    if uploaded_img:
        sys_prompt = f"Vision active. {base_instr}"
        base64_img = encode_image(uploaded_img)
        msgs_api = [{"role": "user", "content": [{"type": "text", "text": final_question}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}]}]
    else:
        msgs_api = [{"role": "system", "content": f"{base_instr} Données: {context_str}"}] + [m for m in st.session_state.messages if m["role"]!="system"]

    client = Mistral(api_key=api_key)
    with st.chat_message("assistant", avatar="💠"):
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
            if sources: st.caption(f"Sources Nexus: {', '.join(sources)}")
            if enable_audio_out:
                audio_file = text_to_speech(full_resp)
                if audio_file: st.audio(audio_file)
            
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e:
            st.error(f"Erreur Nexus : {e}")

