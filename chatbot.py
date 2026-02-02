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

# --- CONFIGURATION & SÉCURITÉ ---
st.set_page_config(page_title="UltraBrain GOD MODE", page_icon="⚡", layout="wide")

if "MISTRAL_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Secrets manquants (MISTRAL_API_KEY ou APP_PASSWORD).")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
correct_password = st.secrets["APP_PASSWORD"]
model = "pixtral-12b-2409"

# --- LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center;'>⚡ GOD MODE ACCESS</h1>", unsafe_allow_html=True)
    if st.button("Entrer") or st.text_input("Mot de passe", type="password") == correct_password:
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Système en ligne. Internet ✅ Vision ✅ Audio ✅"}]

# --- STYLE CSS ---
st.markdown("""
<style>
    h1 { background: -webkit-linear-gradient(45deg, #FFD700, #FF8C00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .stChatMessage { border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}
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
        # Streamlit audio input returns a file-like object (WAV)
        with sr.AudioFile(audio_bytes) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="fr-FR")
            return text
    except Exception as e:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Commandes")
    mode = st.selectbox("Mode :", ["🎓 Professeur", "⚖️ Juriste", "💻 Codeur", "🍳 Cuisinier", "👁️ Vision"])
    
    st.divider()
    enable_web = st.toggle("🌍 Accès Internet", value=False)
    enable_audio_out = st.toggle("🔊 Lire les réponses", value=False)
    
    st.divider()
    uploaded_pdf = st.file_uploader("Cours (PDF)", type="pdf")
    uploaded_img = st.file_uploader("Image (JPG)", type=["jpg", "png"])
    
    st.divider()
    if st.button("📝 GÉNÉRER UN QUIZ"):
        st.session_state.messages.append({"role": "user", "content": "Génère un Quiz QCM de 5 questions sur le document (ou connaissances générales) pour me tester. Affiche la correction après."})
        st.rerun()

    if st.button("💾 Sauvegarder Chat"):
        chat_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("Télécharger", chat_str, "chat.txt")
        
    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER): shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- MAIN ---
st.title("⚡ UltraBrain God Mode")

vector_db = None
if uploaded_pdf:
    raw = get_pdf_documents(uploaded_pdf)
    if raw:
        vector_db = get_vector_store(raw, api_key)
        if vector_db: st.toast("Mémoire PDF active !", icon="🧠")

# Affichage Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"])

# --- INPUT (MICROPHONE OU CLAVIER) ---
input_text = st.chat_input("Message...")
input_audio = st.audio_input("🎙️ Parler") # Nouveauté Streamlit 1.40

final_question = None

# Priorité : Audio > Texte
if input_audio:
    with st.spinner("🎧 Transcription..."):
        transcription = transcribe_audio(input_audio)
        if transcription:
            final_question = transcription
        else:
            st.error("Je n'ai pas compris l'audio.")
elif input_text:
    final_question = input_text

# --- TRAITEMENT ---
if final_question:
    # On ajoute la question à l'historique
    st.session_state.messages.append({"role": "user", "content": final_question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(final_question)
        if uploaded_img: st.image(uploaded_img, width=200)

    # 1. RAG (PDF)
    contexte_pdf = ""
    sources = []
    if vector_db and not uploaded_img:
        docs = vector_db.similarity_search(final_question, k=3)
        contexte_pdf = "\n".join([d.page_content for d in docs])
        sources = list(set([f"Page {d.metadata['page']}" for d in docs]))

    # 2. WEB SEARCH (Internet)
    contexte_web = ""
    if enable_web:
        with st.status("🌍 Recherche Internet...", expanded=False):
            contexte_web = search_web(final_question)
            st.write(contexte_web)

    # 3. PROMPT CONSTRUCTION
    latex_instr = "FORMAT MATHS: Utilise LaTeX ($x^2$). Sois pédagogue."
    
    if uploaded_img:
        sys_prompt = f"Tu as la vision. Analyse l'image. {latex_instr}"
        base64_img = encode_image(uploaded_img)
        msgs_api = [{"role": "user", "content": [{"type": "text", "text": final_question}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}]}]
    else:
        # Fusion des cerveaux (PDF + Web + Général)
        full_context = ""
        if contexte_pdf: full_context += f"\nSOURCE PDF:\n{contexte_pdf}"
        if contexte_web: full_context += f"\nSOURCE INTERNET:\n{contexte_web}"
        
        sys_prompt = f"Tu es {mode}. {latex_instr}. Utilise ces infos si pertinentes: {full_context}"
        msgs_api = [{"role": "system", "content": sys_prompt}] + [m for m in st.session_state.messages if m["role"]!="system"]

    # 4. GENERATION
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
            
            # Affichage des métadonnées
            if sources: st.caption(f"📚 Sources PDF : {', '.join(sources)}")
            if enable_web and contexte_web: st.caption("🌍 Infos vérifiées sur le Web")
            
            # Lecture Audio
            if enable_audio_out:
                audio_file = text_to_speech(full_resp)
                if audio_file: st.audio(audio_file)
            
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
            
        except Exception as e:
            st.error(f"Erreur : {e}")
