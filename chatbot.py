import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO

# --- 1. CONFIGURATION & STYLE LUXE ORIGINAL ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=2000');
        background-size: cover;
        background-attachment: fixed;
        color: #E0E0E0;
    }
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 4rem; margin-top: 20px; }
    
    /* Retour aux grandes cartes stylées */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.4);
        backdrop-filter: blur(15px);
        padding: 40px 20px;
        border-radius: 20px;
        text-align: center;
        transition: 0.4s;
    }
    .glass-card:hover { transform: translateY(-10px); border-color: #D4AF37; background: rgba(212, 175, 55, 0.08); }

    /* Correction Zone Drag & Drop */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #D4AF37 !important;
        background: rgba(212, 175, 55, 0.05) !important;
        border-radius: 15px !important;
    }
    
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.98) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "legal_scores" not in st.session_state:
    st.session_state.legal_scores = {"Conformité": 99.4, "Risque": 45, "Souveraineté": 100}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. FONCTIONS ---
def read_file_content(file):
    name = file.name.lower()
    try:
        if name.endswith(".pdf"):
            return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
        elif name.endswith(".docx"):
            return "\n".join([p.text for p in Document(file).paragraphs])
        elif name.endswith(".txt"):
            return file.read().decode()
    except: return ""
    return ""

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("NAVIGATION", ["🏛️ Dashboard", "🔬 Audit Expert"])
    st.write("---")
    if st.button("✨ RÉINITIALISER"):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD ORIGINAL ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00FF00; letter-spacing:3px;'>● SYSTÈME DE VEILLE CONNECTÉ 2026</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="glass-card"><h2 style="color:#D4AF37;">99.4%</h2><p>PRÉCISION JURIDIQUE</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="glass-card"><h2 style="color:#D4AF37;">FRANCE</h2><p>SOUVERAINETÉ TECH</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="glass-card"><h2 style="color:#D4AF37;">ACTIF</h2><p>ANALYSE MULTI-AGENTS</p></div>', unsafe_allow_html=True)
    
    st.write("")
    st.markdown("<h3 style='text-align:center; font-family:serif;'>BIENVENUE, MAÎTRE.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#D4AF37;'>Votre portail vers l'excellence juridique augmentée est prêt.</p>", unsafe_allow_html=True)

# --- 6. AUDIT EXPERT (FIX DRAG & DROP) ---
elif menu == "🔬 Audit Expert":
    st.markdown("<h2 style='text-align:center; color:#D4AF37; font-family:serif;'>Audit & Analyse de Documents</h2>", unsafe_allow_html=True)
    
    # Zone de dépôt de fichiers
    uploaded_files = st.file_uploader("Déposez ou glissez vos fichiers ici (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Posez votre question sur les documents..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            context = ""
            if uploaded_files:
                for f in uploaded_files: context += f"\n--- {f.name} ---\n{read_file_content(f)}\n"
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": f"Tu es Lex Nexus. Expert juridique 2026."},
                {"role": "user", "content": f"DOCS:\n{context[:8000]}\n\nQUESTION: {prompt}"}
            ])
            full_res = ""
            placeholder = st.empty()
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
