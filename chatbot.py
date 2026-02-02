import streamlit as st
import os
import shutil
import base64
import tempfile
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from gtts import gTTS

# --- CONFIGURATION & SÉCURITÉ ---
st.set_page_config(page_title="UltraBrain AI", page_icon="🔒", layout="wide")

# Vérification des secrets
if "MISTRAL_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Configuration manquante : Vérifiez .streamlit/secrets.toml")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
correct_password = st.secrets["APP_PASSWORD"]
model = "pixtral-12b-2409"

# --- SYSTÈME DE LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔒 Connexion requise</h1>", unsafe_allow_html=True)
    password_input = st.text_input("Mot de passe :", type="password")
    if st.button("Entrer"):
        if password_input == correct_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop() # Arrête tout si pas connecté

# --- STYLE ---
st.markdown("""
<style>
    h1 {
        background: -webkit-linear-gradient(45deg, #00F260, #0575E6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        text-align: center;
    }
    .stChatMessage {
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    /* Cache le menu GitHub */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
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
            if text:
                docs.append(Document(page_content=text, metadata={"page": i + 1}))
        return docs
    except Exception as e:
        st.error(f"Erreur PDF : {e}")
        return None

def get_vector_store(documents, _api_key):
    embeddings = MistralAIEmbeddings(mistral_api_key=_api_key)
    if os.path.exists(INDEX_FOLDER):
        try:
            return FAISS.load_local(INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True)
        except: pass
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(splits, embeddings)
        vector_store.save_local(INDEX_FOLDER)
        return vector_store
    except Exception as e:
        st.error(f"Erreur FAISS : {e}")
        return None

def text_to_speech(text):
    """Convertit le texte en audio MP3"""
    try:
        tts = gTTS(text=text, lang='fr')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        return None

# --- SIDEBAR (Contrôles) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2583/2583166.png", width=80)
    st.title("🎛️ Commandes")
    
    mode = st.selectbox("🧠 Expert :", ["🎓 Professeur", "⚖️ Juriste", "💻 Codeur", "🍳 Cuisinier", "👁️ Vision"])
    enable_audio = st.toggle("🔊 Activer la lecture audio", value=False)
    
    st.markdown("---")
    st.caption("📂 Fichiers")
    uploaded_pdf = st.file_uploader("Cours (PDF)", type="pdf")
    uploaded_img = st.file_uploader("Image (JPG)", type=["jpg", "png"])

    # BOUTON EXPORT (Option 2)
    chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}\n" for m in st.session_state.messages])
    st.download_button("💾 Télécharger la conversation", chat_history, file_name="conversation.txt")

    if st.button("🗑️ Reset", type="primary"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER): shutil.rmtree(INDEX_FOLDER)
        st.rerun()

    if st.button("🔒 Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()

# --- MAIN ---
st.title("🧠 UltraBrain Ultimate")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bienvenue. Je suis sécurisé et prêt. 🔐"}]

vector_db = None
if uploaded_pdf:
    raw_docs = get_pdf_documents(uploaded_pdf)
    if raw_docs:
        vector_db = get_vector_store(raw_docs, api_key)
        if vector_db: st.toast("PDF chargé !", icon="📚")

for msg in st.session_state.messages:
    icone = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icone):
        st.markdown(msg["content"])
        # Affiche le lecteur audio si c'était un message assistant récent (optionnel, on le fait juste pour le dernier)

if question := st.chat_input("Votre message..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
        if uploaded_img: st.image(uploaded_img, width=200)

    # RAG + Vision Logic
    contexte = ""
    sources = []
    if vector_db and not uploaded_img:
        docs = vector_db.similarity_search(question, k=3)
        contexte = "\n".join([d.page_content for d in docs])
        sources = list(set([f"Page {d.metadata['page']}" for d in docs]))

    latex_instr = "FORMAT MATHS: Utilise LaTeX ($x^2$). Ne parle pas trop, sois précis."
    
    if uploaded_img:
        sys_prompt = f"Tu as la vision. Analyse l'image. {latex_instr}"
        base64_img = encode_image(uploaded_img)
        msgs_api = [{"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}]}]
    elif contexte:
        sys_prompt = f"Contexte (PDF): {contexte}. {latex_instr}. Réponds d'après le contexte."
        msgs_api = [{"role": "system", "content": sys_prompt}] + [m for m in st.session_state.messages if m["role"]!="system"]
    else:
        sys_prompt = f"Tu es {mode}. {latex_instr}."
        msgs_api = [{"role": "system", "content": sys_prompt}] + [m for m in st.session_state.messages if m["role"]!="system"]

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
            if sources: st.caption(f"📚 Sources: {', '.join(sources)}")
            
            # --- AUDIO GENERATION (Option 3) ---
            if enable_audio:
                with st.spinner("🗣️ Génération audio..."):
                    audio_file = text_to_speech(full_resp)
                    if audio_file:
                        st.audio(audio_file, format="audio/mp3")

            st.session_state.messages.append({"role": "assistant", "content": full_resp})
            
        except Exception as e:
            st.error(f"Erreur : {e}")
