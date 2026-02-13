import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from docx import Document

# --- CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus | Live Agency", page_icon="⚖️", layout="wide")

# --- DESIGN PRESTIGE RETRAVAILLÉ ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@200;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                    url('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=2000&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 4rem; margin-top: 20px; text-shadow: 0 4px 15px rgba(212, 175, 55, 0.4); }
    .live-status { text-align: center; color: #00FF00; font-size: 0.75rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 40px; animation: blink 2s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

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

    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.98) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "archive_dossiers" not in st.session_state: st.session_state.archive_dossiers = []

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center; font-family:serif;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("AGENCE LIVE", ["🏛️ Dashboard", "🔬 Audit & Recherche", "🗄️ Archives"])
    st.write("---")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    if st.button("✨ NOUVELLE SESSION"):
        st.session_state.chat_history = []; st.rerun()

# --- 1. DASHBOARD STYLÉ ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SYSTÈME EN LIGNE — ACTUALITÉ JURIDIQUE 2026</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h2 style="color:#D4AF37;">99.4%</h2><p>Précision Juridique</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h2 style="color:#D4AF37;">FRANCE</h2><p>Souveraineté Live</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h2 style="color:#D4AF37;">24h/24</h2><p>Veille Active</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("<h3 style='text-align:center; color:white; font-family:serif;'>Bienvenue, Maître.</h3>", unsafe_allow_html=True)

# --- 2. AUDIT & RECHERCHE (DATE FIXÉE) ---
elif menu == "🔬 Audit & Recherche":
    uploaded_files = st.file_uploader("📂 Déposer vos pièces jointes", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            # C'est ici qu'on force la date réelle !
            now = datetime.now().strftime("%A %d %B %Y")
            system_msg = f"Tu es Lex Nexus. Aujourd'hui nous sommes le {now}. Tu réponds avec les lois à jour de 2026."
            
            placeholder = st.empty(); full_res = ""
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
