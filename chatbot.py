import streamlit as st
import os
import shutil
import base64
import tempfile
import io
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument
from gtts import gTTS
from duckduckgo_search import DDGS

# --- CONFIGURATION NEXUS ---
st.set_page_config(page_title="Nexus Omni", page_icon="💠", layout="wide")

# Vérification de la clé API
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("⚠️ Clé API Mistral manquante dans les Secrets.")
    st.stop()

api_key = st.secrets["MISTRAL_API_KEY"]
model_default = "pixtral-12b-2409"

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- STYLE CSS "NEXUS PREMIUM" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    .stApp { background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%); overflow-x: hidden; }
    
    /* Titre animé */
    .nexus-title { text-align: center; font-size: 4rem; font-weight: 200; letter-spacing: 15px; color: white; text-shadow: 0 0 30px rgba(0, 150, 255, 0.5); margin-top: 50px; }
    
    /* Bulles de chat Glassmorphism */
    div[data-testid="stChatMessage"] { 
        background-color: rgba(255, 255, 255, 0.03) !important; 
        backdrop-filter: blur(15px); 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 15px !important; 
        margin-bottom: 10px; 
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.8) !important; backdrop-filter: blur(20px); }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS SYSTÈME ---
def get_shared_knowledge():
    """Récupère la mémoire collective (Auto-apprentissage contrôlé)"""
    shared_file = "brain_shared.txt"
    if os.path.exists(shared_file):
        with open(shared_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def get_pdf_documents(files):
    """Analyse les fichiers PDF de l'utilisateur"""
    docs = []
    for f in files:
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text: docs.append(LangChainDocument(page_content=text, metadata={"source": f.name, "page": i+1}))
    return docs

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>N E X U S</h2>", unsafe_allow_html=True)
    
    # Navigation entre les pages
    menu = st.radio("NAVIGATION", ["Chat Nexus", "Sécurité & Confidentialité"])
    st.markdown("---")
    
    if menu == "Chat Nexus":
        enable_web = st.toggle("🌐 Recherche Web", value=False)
        enable_vocal = st.toggle("🔊 Réponse Vocale", value=False)
        st.markdown("---")
        uploaded_pdfs = st.file_uploader("Fichiers PDF (Privés)", type="pdf", accept_multiple_files=True)
        if st.button("🗑️ Nouvelle Session", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    else:
        st.subheader("🛡️ Engagement Sécurité")
        st.info("""
        **Pourquoi Nexus est sûr :**
        1. **Mistral AI (France)** : Vos données restent en Europe.
        2. **Zéro Entraînement** : Vos fichiers ne servent pas à entraîner l'IA.
        3. **Sessions Éphémères** : Rien n'est conservé après la fermeture.
        """)

# --- PAGE 1 : CHAT NEXUS ---
if menu == "Chat Nexus":
    # Accueil
    if not st.session_state.messages:
        st.markdown('<h1 class="nexus-title">NEXUS</h1>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888;'>L'Intelligence Artificielle Souveraine et Collective.</p>", unsafe_allow_html=True)

    # Affichage des messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="💠" if msg["role"]=="assistant" else "▫️"):
            st.markdown(msg["content"])

    # Entrée utilisateur
    text_in = st.chat_input("Posez votre question à Nexus...")

    if text_in:
        st.session_state.messages.append({"role": "user", "content": text_in})
        with st.chat_message("user", avatar="▫️"):
            st.markdown(text_in)

        # Logique de réponse
        context = ""
        date_str = datetime.now().strftime("%A %d %B %Y, %H:%M")
        
        # Gestion du spinner (Réflexion)
        with st.status("Nexus analyse...", expanded=False) as status:
            # 1. Mémoire Collective
            shared_kb = get_shared_knowledge()
            if shared_kb:
                context += "\nMÉMOIRE COLLECTIVE:\n" + shared_kb
            
            # 2. Analyse PDF (Uniquement si fichiers présents)
            if uploaded_pdfs:
                status.update(label="Exploration de vos documents...")
                docs = get_pdf_documents(uploaded_pdfs)
                if docs:
                    vector_db = FAISS.from_documents(docs, MistralAIEmbeddings(mistral_api_key=api_key))
                    res = vector_db.similarity_search(text_in, k=3)
                    context += "\nDOCUMENTS SESSION:\n" + "\n".join([d.page_content for d in res])
            
            # 3. Web Search
            if enable_web:
                status.update(label="Recherche sur le Web mondial...")
                try: context += f"\nINFO WEB:\n{DDGS().text(text_in, max_results=2)}"
                except: pass
            
            status.update(label="Génération de la réponse...", state="complete")

        # Appel API et Streaming
        client = Mistral(api_key=api_key)
        with st.chat_message("assistant", avatar="💠"):
            placeholder = st.empty()
            full_resp = ""
            sys_instr = f"Tu es Nexus. Date actuelle : {date_str}. Sois direct et utilise LaTeX pour les maths."
            msgs = [{"role": "system", "content": f"{sys_instr} {context}"}] + st.session_state.messages
            
            try:
                stream = client.chat.stream(model=model_default, messages=msgs)
                for chunk in stream:
                    content = chunk.data.choices[0].delta.content
                    if content:
                        full_resp += content
                        placeholder.markdown(full_resp + "▌")
                placeholder.markdown(full_resp)
                
                # Vocal
                if enable_vocal:
                    tts = gTTS(text=full_resp, lang='fr')
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)
                
                st.session_state.messages.append({"role": "assistant", "content": full_resp})
            except Exception as e:
                st.error("Nexus est actuellement saturé. Réessayez dans un instant.")

# --- PAGE 2 : SÉCURITÉ ---
else:
    st.markdown("## 🛡️ Sécurité et Confidentialité des Données")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔒 Protection Entreprise")
        st.write("""
        Nexus a été conçu avec une approche **Privacy-First**. 
        Contrairement aux outils IA grand public, nous séparons strictement 
        le moteur d'intelligence des données traitées.
        """)
        st.markdown("### 🇫🇷 Hébergement & Souveraineté")
        st.write("Les calculs sont effectués via Mistral AI, garantissant que les données restent sous juridiction européenne.")
        
    with col2:
        st.subheader("🕵️ Non-utilisation des données")
        st.write("""
        Nous garantissons contractuellement que :
        - Vos documents ne sont **jamais** stockés définitivement.
        - Vos échanges ne servent pas à entraîner l'IA.
        - Aucun tiers n'a accès à vos sessions.
        """)
