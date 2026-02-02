import streamlit as st
import os
import shutil
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- CONFIGURATION ---

api_key = st.secrets["MISTRAL_API_KEY"]
model = "open-mistral-nemo" 

# Config de la page
st.set_page_config(page_title="UltraBrain AI", page_icon="🧠", layout="wide")

# --- LE STYLE CORRIGÉ (Dark Mode Friendly) ---
st.markdown("""
<style>
    /* Titre principal avec un dégradé stylé */
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF9068);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Sous-titre centré */
    .stMarkdown p {
        text-align: center;
    }

    /* On ne force plus le fond blanc ! On laisse le thème sombre par défaut.
       On ajoute juste une petite bordure discrète */
    .stChatMessage {
        border: 1px solid rgba(255, 255, 255, 0.1); /* Bordure très fine */
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Dossier de sauvegarde
INDEX_FOLDER = "faiss_index_mistral"

# --- FONCTIONS TECHNIQUES ---

def get_pdf_text(pdf_file):
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Erreur lecture PDF : {e}")
        return None

def get_vector_store(text_content, _api_key):
    embeddings = MistralAIEmbeddings(mistral_api_key=_api_key)
    if os.path.exists(INDEX_FOLDER):
        try:
            return FAISS.load_local(INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True)
        except:
            pass
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text_content)
        vector_store = FAISS.from_texts(chunks, embeddings)
        vector_store.save_local(INDEX_FOLDER)
        return vector_store
    except Exception as e:
        st.error(f"Erreur vectorisation : {e}")
        return None

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)
    st.title("⚙️ Contrôle")
    
    mode = st.selectbox(
        "🧠 Mode Expert :",
        ["🎓 Professeur", "⚖️ Juriste", "💼 Business", "💻 Développeur", "📝 Traducteur"]
    )
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 PDF", type="pdf")
    
    if st.button("🗑️ Reset Mémoire", type="primary"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER):
            shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- HEADER ---
st.title("🧠 UltraBrain AI")
st.caption("Ton assistant intelligent polyvalent")

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Salut ! Je suis prêt. Envoie un PDF ou pose une question."})

vector_db = None
if uploaded_file:
    raw_text = get_pdf_text(uploaded_file)
    if raw_text:
        vector_db = get_vector_store(raw_text, api_key)
        if vector_db:
            st.toast("✅ Cerveau mis à jour !", icon="🧠")

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    icone = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icone):
        # Ici, on n'a plus besoin de forcer le style, Streamlit gère le texte blanc auto
        st.markdown(msg["content"])

# --- INPUT ---
if question := st.chat_input("Message..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    contexte = ""
    if vector_db:
        docs = vector_db.similarity_search(question, k=4)
        contexte = "\n".join([d.page_content for d in docs])

    # Gestion des rôles simplifiée
    if "Professeur" in mode:
        sys = "Tu es un prof pédagogue. Explique clairement."
    elif "Juriste" in mode:
        sys = "Tu es un juriste formel et précis."
    elif "Développeur" in mode:
        sys = "Tu es un codeur expert. Donne des exemples."
    else:
        sys = "Tu es un assistant utile."

    if contexte:
        sys += f"\nUtilise ce contexte pour répondre : {contexte}"

    client = Mistral(api_key=api_key)
    msgs = [{"role": "system", "content": sys}]
    msgs.extend([m for m in st.session_state.messages if m["role"] != "system"])

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_resp = ""
        try:
            stream = client.chat.stream(model=model, messages=msgs)
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_resp += content
                    placeholder.markdown(full_resp + "▌")
            placeholder.markdown(full_resp)
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e:
            st.error(f"Erreur : {e}")