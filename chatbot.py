import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from docx import Document
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus | Agence Juridique", page_icon="⚖️", layout="wide")

# --- DESIGN "PRESTIGE CLAIR" (CORRIGÉ POUR ÉVITER LES BUGS) ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background-color: #0A0B10;
        background-image: linear-gradient(rgba(10, 11, 16, 0.9), rgba(10, 11, 16, 0.9)), url('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=2000');
        background-size: cover;
        color: #E0E0E0;
    }
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3.5rem; margin-bottom: 0px; padding-top: 20px; }
    .live-status { text-align: center; color: #00FF00; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 30px; }

    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Fix pour la barre de chat qui doit être visible */
    .stChatInputContainer { padding-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "archive_dossiers" not in st.session_state: st.session_state.archive_dossiers = []

# --- LECTEUR MULTI-FORMAT ---
def read_file_content(file):
    name = file.name.lower()
    try:
        if name.endswith(".pdf"):
            return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
        elif name.endswith(".docx"):
            return "\n".join([p.text for p in Document(file).paragraphs])
        elif name.endswith(".txt"):
            return file.read().decode()
        elif name.endswith((".png", ".jpg", ".jpeg")):
            return f"[Contenu visuel détecté dans {file.name}]"
    except: return f"[Erreur de lecture : {file.name}]"
    return ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("AGENCE LIVE", ["🏛️ Dashboard", "🔬 Audit Multi-Format", "🗄️ Archives"])
    st.write("---")
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    if st.button("✨ NOUVELLE SESSION"):
        st.session_state.chat_history = []; st.rerun()

# --- NAVIGATION ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SYSTÈME EN LIGNE — BASE JURIDIQUE 2026</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">VIGIE</h3><p>Veille législative active</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">SOURCES</h3><p>Multi-Formats (Docx, PDF, Image)</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">AGENTS</h3><p>Analyse IA certifiée</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("<h3 style='text-align:center;'>Bienvenue, Maître. L'agence est prête.</h3>", unsafe_allow_html=True)

elif menu == "🔬 Audit Multi-Format":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>Expertise Multi-Format</h2>", unsafe_allow_html=True)
    
    # Drag and drop pour TOUT type de fichier
    files = st.file_uploader("Contrats, documents, images...", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=True)
    
    # Affichage historique
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    # CHAT INPUT (Toujours en bas)
    if prompt := st.chat_input("Votre instruction..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty(); full_res = ""
            context = ""
            if files:
                for f in files: context += f"\n--- {f.name} ---\n{read_file_content(f)}\n"
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": "Tu es Lex Nexus. Expert juridique multi-format."},
                {"role": "user", "content": f"DOCUMENTS:\n{context[:8000]}\n\nQUESTION: {prompt}"}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            if files:
                st.session_state.archive_dossiers.append({"nom": files[0].name, "rapport": full_res})

elif menu == "🗄️ Archives":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>Dossiers Archivés</h2>", unsafe_allow_html=True)
    for doc in st.session_state.archive_dossiers:
        with st.expander(f"📁 {doc['nom']}"): st.markdown(doc['rapport'])
