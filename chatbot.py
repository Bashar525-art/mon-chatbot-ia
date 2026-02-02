import streamlit as st
import os
import shutil
import base64
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# --- CONFIGURATION ---
if "MISTRAL_API_KEY" in st.secrets:
    api_key = st.secrets["MISTRAL_API_KEY"]
else:
    st.error("Clé API introuvable. Configurez .streamlit/secrets.toml")
    st.stop()

# On utilise "Pixtral" (le modèle qui voit) par défaut
model = "pixtral-12b-2409"

st.set_page_config(page_title="UltraBrain AI", page_icon="👁️", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
    h1 {
        background: -webkit-linear-gradient(45deg, #12c2e9, #c471ed, #f64f59);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        text-align: center;
    }
    .stChatMessage {
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

INDEX_FOLDER = "faiss_index_mistral"

# --- FONCTIONS ---

def encode_image(uploaded_file):
    """Convertit l'image en format lisible par l'IA (Base64)"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_pdf_documents(pdf_file):
    """Lit le PDF et garde en mémoire le numéro de la page"""
    docs = []
    try:
        reader = PdfReader(pdf_file)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # On crée un objet Document avec le texte ET le numéro de page
                docs.append(Document(page_content=text, metadata={"page": i + 1}))
        return docs
    except Exception as e:
        st.error(f"Erreur lecture PDF : {e}")
        return None

def get_vector_store(documents, _api_key):
    embeddings = MistralAIEmbeddings(mistral_api_key=_api_key)
    if os.path.exists(INDEX_FOLDER):
        try:
            return FAISS.load_local(INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True)
        except:
            pass
    try:
        # On découpe les pages en morceaux plus petits pour la recherche
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(splits, embeddings)
        vector_store.save_local(INDEX_FOLDER)
        return vector_store
    except Exception as e:
        st.error(f"Erreur vectorisation : {e}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/11698/11698471.png", width=80)
    st.title("⚙️ Contrôle")
    
    mode = st.selectbox("🧠 Personnalité :", ["🎓 Professeur", "⚖️ Juriste", "💻 Développeur", "🍳 Cuisinier", "👁️ Analyste Visuel"])
    
    st.markdown("---")
    st.caption("📂 **Zone de dépôt**")
    uploaded_pdf = st.file_uploader("Document (PDF)", type="pdf", key="pdf")
    uploaded_img = st.file_uploader("Image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="img")

    if st.button("🗑️ Reset", type="primary"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER):
            shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- MAIN ---
st.title("👁️ UltraBrain AI (Vision & Sources)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salut ! Je peux lire tes PDF et VOIR tes images. Essaie-moi !"}]

# Gestion du PDF (Mémoire)
vector_db = None
if uploaded_pdf:
    raw_docs = get_pdf_documents(uploaded_pdf)
    if raw_docs:
        vector_db = get_vector_store(raw_docs, api_key)
        if vector_db:
            st.toast("✅ PDF mémorisé avec numéros de pages !", icon="📄")

# Affichage Historique
for msg in st.session_state.messages:
    icone = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icone):
        st.markdown(msg["content"])

# INPUT UTILISATEUR
if question := st.chat_input("Pose une question ou envoie une image..."):
    
    # 1. Construction du message utilisateur pour l'affichage
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
        if uploaded_img:
            st.image(uploaded_img, caption="Image envoyée", width=200)

    # 2. Recherche RAG (Sources)
    contexte = ""
    sources_utilisees = []
    
    if vector_db and not uploaded_img: # On privilégie la vision si une image est là
        docs = vector_db.similarity_search(question, k=3)
        contexte = "\n".join([d.page_content for d in docs])
        # On garde les sources pour l'affichage à la fin
        sources_utilisees = [f"Page {d.metadata['page']}" for d in docs]
        sources_utilisees = list(set(sources_utilisees)) # Enlever les doublons

    # 3. Prompt Système & LaTeX
    latex_instruction = """
    FORMATTAGE MATHS : Utilise TOUJOURS le format LaTeX.
    - $x^2$ pour les formules en ligne.
    - $$ E = mc^2 $$ pour les formules centrées.
    """
    
    if uploaded_img:
        system_prompt = "Tu es une IA dotée de vision. Analyse l'image fournie avec précision. " + latex_instruction
    elif contexte:
        system_prompt = f"""Utilise ce contexte (PDF) pour répondre :
        ---
        {contexte}
        ---
        Si la réponse n'y est pas, utilise tes connaissances.
        {latex_instruction}
        """
    else:
        system_prompt = f"Tu es un assistant expert. {latex_instruction}"

    # 4. Préparation du message pour Mistral (Texte OU Vision)
    client = Mistral(api_key=api_key)
    
    if uploaded_img:
        # Format spécial pour Pixtral (Vision)
        base64_image = encode_image(uploaded_img)
        messages_api = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                ]
            }
        ]
    else:
        # Format classique (Texte / Chat)
        messages_api = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages:
            if m["role"] != "system":
                messages_api.append({"role": m["role"], "content": m["content"]})

    # 5. Réponse AI
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_resp = ""
        
        try:
            stream = client.chat.stream(model=model, messages=messages_api)
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_resp += content
                    placeholder.markdown(full_resp + "▌")
            
            # Affichage final + Sources
            placeholder.markdown(full_resp)
            
            # SI on a utilisé des sources PDF, on les affiche en petit
            if sources_utilisees:
                st.markdown("---")
                st.caption(f"📚 **Sources détectées :** {', '.join(sources_utilisees)}")
                with st.expander("Voir les extraits utilisés"):
                    st.text(contexte[:1000] + "...")

            st.session_state.messages.append({"role": "assistant", "content": full_resp})
            
        except Exception as e:
            st.error(f"Erreur : {e}")
