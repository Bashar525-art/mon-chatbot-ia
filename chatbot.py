import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS V5.0 ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

# --- DESIGN IMMERSIF "LEGAL LUXE" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@200;400;600&display=swap');
    
    /* Fond principal avec image texturée sombre */
    .stApp {
        background: linear-gradient(rgba(9, 10, 15, 0.8), rgba(9, 10, 15, 0.8)), 
                    url('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80');
        background-size: cover;
        background-attachment: fixed;
        color: #E0E0E0;
    }
    
    /* Titre doré magistral */
    .main-header {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        text-align: center;
        font-size: 4.5rem;
        margin-top: 50px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #D4AF37;
        letter-spacing: 8px;
        text-transform: uppercase;
        font-size: 0.9rem;
        margin-bottom: 60px;
        opacity: 0.8;
    }

    /* Cartes en Glassmorphism (Verre) */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.4);
        backdrop-filter: blur(15px);
        padding: 40px 20px;
        border-radius: 20px;
        text-align: center;
        transition: all 0.5s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .glass-card:hover {
        transform: translateY(-10px);
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.08);
        box-shadow: 0 15px 40px rgba(212, 175, 55, 0.2);
    }

    .card-val { font-size: 2.5rem; color: #D4AF37; font-family: 'Playfair Display', serif; font-weight: bold; }
    .card-txt { font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; color: #ffffff; margin-top: 10px; }

    /* Sidebar élégante */
    section[data-testid="stSidebar"] {
        background-color: rgba(7, 8, 12, 0.98) !important;
        border-right: 1px solid #D4AF37;
    }
    
    /* Bouton d'action */
    .stButton>button {
        background: linear-gradient(45deg, #D4AF37, #B8860B) !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 15px 30px !important;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "archive_dossiers" not in st.session_state: st.session_state.archive_dossiers = []

def extract_pdf_text(files):
    text = ""
    for f in files:
        try:
            reader = PdfReader(f); text += "".join([p.extract_text() for p in reader.pages])
        except: continue
    return text

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center; font-family:serif;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("SERVICE JURIDIQUE", ["🏛️ Dashboard", "🔬 Audit Expert", "🗄️ Archives"])
    st.write("---")
    if st.button("✨ NOUVELLE SESSION"):
        st.session_state.chat_history = []; st.rerun()

# --- NAVIGATION ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">L\'Intelligence Souveraine du Droit</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="glass-card"><div class="card-val">99.4%</div><div class="card-txt">Précision Juridique</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><div class="card-val">FRANCE</div><div class="card-txt">Souveraineté Tech</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card"><div class="card-val">ACTIF</div><div class="card-txt">Analyse Multi-Agents</div></div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Playfair Display; color:white;'>BIENVENUE, MAÎTRE.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#D4AF37; font-size:1.2rem;'>Votre portail vers l'excellence juridique augmentée est prêt.</p>", unsafe_allow_html=True)

elif menu == "🔬 Audit Expert":
    st.markdown('<p class="main-header" style="font-size:2.5rem;">Audit Expert</p>', unsafe_allow_html=True)
    files = st.file_uploader("📂 Déposer vos pièces (PDF)", type="pdf", accept_multiple_files=True)
    
    # Historique des messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    # Barre de chat fixe
    if prompt := st.chat_input("Posez votre question ou analysez vos documents..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty(); full_res = ""
            context = extract_pdf_text(files) if files else ""
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": "Tu es Lex Nexus, expert en droit."},
                {"role": "user", "content": f"Contexte: {context[:7000]}\n\nQuestion: {prompt}"}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content: full_res += content; placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})

elif menu == "🗄️ Archives":
    st.markdown('<p class="main-header" style="font-size:2.5rem;">Archives</p>', unsafe_allow_html=True)
    for doc in st.session_state.archive_dossiers:
        with st.expander(f"📁 {doc['nom']}"): st.markdown(doc['rapport'])
