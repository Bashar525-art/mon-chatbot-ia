import streamlit as st
import os
import shutil
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- CONFIGURATION ---
if "MISTRAL_API_KEY" in st.secrets:
    api_key = st.secrets["MISTRAL_API_KEY"]
else:
    st.error("Clé API introuvable. Configurez .streamlit/secrets.toml")
    st.stop()

model = "open-mistral-nemo" 

st.set_page_config(page_title="UltraBrain AI", page_icon="🧠", layout="wide")

# --- LE STYLE (Design Dark Mode) ---
st.markdown("""
<style>
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF9068);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .stChatMessage {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

INDEX_FOLDER = "faiss_index_mistral"

# --- FONCTIONS ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)
    st.title("⚙️ Contrôle")
    mode = st.selectbox("🧠 Personnalité :", ["🎓 Professeur Pédagogue", "⚖️ Juriste Expert", "💻 Développeur Senior", "🍳 Chef Cuisinier"])
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Charge un PDF (Optionnel)", type="pdf")
    if st.button("🗑️ Reset Mémoire", type="primary"):
        st.session_state.messages = []
        if os.path.exists(INDEX_FOLDER):
            shutil.rmtree(INDEX_FOLDER)
        st.rerun()

# --- MAIN ---
st.title("🧠 UltraBrain AI")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Salut ! Envoie un PDF ou pose une question (Maths, Recettes, etc.)."}]

vector_db = None
if uploaded_file:
    raw_text = get_pdf_text(uploaded_file)
    if raw_text:
        vector_db = get_vector_store(raw_text, api_key)
        if vector_db:
            st.toast("✅ Document lu !", icon="🧠")

for msg in st.session_state.messages:
    icone = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icone):
        st.markdown(msg["content"])

if question := st.chat_input("Message..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    contexte = ""
    if vector_db:
        docs = vector_db.similarity_search(question, k=4)
        contexte = "\n".join([d.page_content for d in docs])

    # --- DEFINITION DES ROLES ---
    if "Professeur" in mode: role_prompt = "Tu es un prof pédagogue."
    elif "Juriste" in mode: role_prompt = "Tu es un juriste formel."
    elif "Développeur" in mode: role_prompt = "Tu es un codeur expert."
    else: role_prompt = "Tu es un assistant utile."

    # --- INSTRUCTION LATEX (Le secret pour les belles maths) ---
    latex_instruction = """
    RÈGLE ABSOLUE POUR LES MATHÉMATIQUES :
    Tu DOIS utiliser le format LaTeX pour TOUTES les expressions mathématiques, nombres complexes ou variables.
    - Pour les formules dans le texte : utilise un seul dollar. Exemple : $x^2 + y^2 = z^2$
    - Pour les formules importantes : utilise deux dollars pour les centrer. Exemple : $$ E = mc^2 $$
    - N'écris JAMAIS "x^2" ou "1/2" en texte brut. Utilise toujours LaTeX : $x^2$, $\\frac{1}{2}$.
    """

    if contexte:
        system_prompt = f"""{role_prompt}
        {latex_instruction}
        
        Voici le contexte du PDF :
        ---
        {contexte}
        ---
        Consigne : Utilise le contexte en priorité. Si la réponse n'y est pas, utilise tes connaissances générales.
        """
    else:
        system_prompt = f"{role_prompt}\n{latex_instruction}\n(Réponds avec tes connaissances générales)."

    client = Mistral(api_key=api_key)
    msgs = [{"role": "system", "content": system_prompt}]
    msgs.extend([m for m in st.session_state.messages if m["role"] != "system"])

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_resp = ""
        stream = client.chat.stream(model=model, messages=msgs)
        for chunk in stream:
            content = chunk.data.choices[0].delta.content
            if content:
                full_resp += content
                placeholder.markdown(full_resp + "▌")
        placeholder.markdown(full_resp)
        st.session_state.messages.append({"role": "assistant", "content": full_resp})
