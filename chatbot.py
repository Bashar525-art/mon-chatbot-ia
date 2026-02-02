import streamlit as st
import os
import shutil
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- CONFIGURATION ---
# On récupère la clé depuis le coffre-fort (Fonctionne sur PC et sur le Cloud)
if "MISTRAL_API_KEY" in st.secrets:
    api_key = st.secrets["MISTRAL_API_KEY"]
else:
    # Fallback pour éviter le crash si le secret n'est pas encore configuré
    st.error("Clé API introuvable. Configurez .streamlit/secrets.toml")
    st.stop()

model = "open-mistral-nemo" 

# Config de la page
st.set_page_config(page_title="UltraBrain AI", page_icon="🧠", layout="wide")

# --- LE STYLE (Design Dark Mode) ---
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
    .stMarkdown p {
        text-align: center;
    }
    .stChatMessage {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Dossier de sauvegarde temporaire
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
    # On met _api_key pour éviter que Streamlit ne recalcule tout si la clé ne change pas
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
        "🧠 Personnalité de l'IA :",
        ["🎓 Professeur Pédagogue", "⚖️ Juriste Expert", "💼 Consultant Business", "💻 Développeur Senior", "📝 Traducteur", "🍳 Chef Cuisinier"]
    )
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Charge un PDF (Optionnel)", type="pdf")
    
    if st.button("🗑️ Reset Mémoire", type="primary"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER):
            shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- HEADER ---
st.title("🧠 UltraBrain AI")
st.caption("Ton assistant intelligent : Pose n'importe quelle question (Cours, Recettes, Code...)")

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Salut ! Je suis prêt. Envoie un PDF pour travailler ou pose juste une question."})

vector_db = None
if uploaded_file:
    raw_text = get_pdf_text(uploaded_file)
    if raw_text:
        vector_db = get_vector_store(raw_text, api_key)
        if vector_db:
            st.toast("✅ Document lu et mémorisé !", icon="🧠")

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    icone = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icone):
        st.markdown(msg["content"])

# --- INPUT UTILISATEUR & LOGIQUE IA ---
if question := st.chat_input("Message..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # 1. Recherche dans le PDF (si dispo)
    contexte = ""
    if vector_db:
        docs = vector_db.similarity_search(question, k=4)
        contexte = "\n".join([d.page_content for d in docs])

    # 2. Définition du Rôle (Prompt Système)
    if "Professeur" in mode:
        role_prompt = "Tu es un prof pédagogue. Explique clairement."
    elif "Juriste" in mode:
        role_prompt = "Tu es un juriste formel. Cite les textes."
    elif "Développeur" in mode:
        role_prompt = "Tu es un codeur expert. Donne des exemples de code."
    elif "Cuisinier" in mode:
        role_prompt = "Tu es un chef étoilé. Donne des recettes précises et gourmandes."
    else:
        role_prompt = "Tu es un assistant polyvalent et utile."

    # 3. Le Prompt Hybride (Le secret pour qu'il sache tout faire)
    if contexte:
        system_prompt = f"""{role_prompt}
        
        Voici des informations contextuelles issues du document fourni par l'utilisateur :
        ---
        {contexte}
        ---
        CONSIGNE IMPORTANTE : 
        1. Utilise le contexte ci-dessus en priorité pour répondre à la question.
        2. SI la réponse ne se trouve pas dans le contexte (ou si la question est générale comme "Donne-moi une recette" ou "Qui est Napoléon"), IGNORE le contexte et utilise tes propres connaissances générales.
        Ne dis jamais "je ne trouve pas l'info", réponds simplement à la question.
        """
    else:
        # Pas de PDF, liberté totale
        system_prompt = f"{role_prompt} (Réponds avec tes vastes connaissances générales)."

    # 4. Appel à Mistral
    client = Mistral(api_key=api_key)
    msgs = [{"role": "system", "content": system_prompt}]
    # On ajoute l'historique de la conversation
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
            st.error(f"Une erreur est survenue : {e}")
