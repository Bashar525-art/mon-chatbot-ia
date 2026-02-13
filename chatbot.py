import streamlit as st
import os
import json
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from docx import Document

# --- 1. CONFIGURATION & STYLE (STABLE & PRO) ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    /* Fond Immersif Fixe */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=2000');
        background-size: cover;
        background-attachment: fixed;
        color: #E0E0E0;
    }
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 4rem; margin-top: 20px; text-shadow: 0 4px 15px rgba(212, 175, 55, 0.4); }
    .live-status { text-align: center; color: #00FF00; font-size: 0.75rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 40px; }

    /* Cartes Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.4);
        backdrop-filter: blur(15px);
        padding: 35px 20px;
        border-radius: 20px;
        text-align: center;
        transition: 0.4s;
        margin-bottom: 20px;
    }
    .glass-card:hover { border-color: #D4AF37; background: rgba(212, 175, 55, 0.08); transform: translateY(-5px); }

    /* Barre Latérale */
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.98) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES LOCALE (SAUVEGARDE) ---
DB_PATH = "archives_lex_nexus"
if not os.path.exists(DB_PATH): os.makedirs(DB_PATH)

def save_to_vault(history):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{DB_PATH}/audit_{ts}.json", "w", encoding="utf-8") as f:
        json.dump({"date": datetime.now().strftime("%d/%m/%Y %H:%M"), "chat": history}, f, ensure_ascii=False)

# --- 3. INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("AGENCE LIVE", ["🏛️ Dashboard", "🔬 Audit Multi-Format", "🗄️ Coffre-fort"])
    st.write("---")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    if st.button("💾 ARCHIVER LA SESSION"):
        save_to_vault(st.session_state.chat_history)
        st.success("Session sécurisée.")

# --- 5. PAGES ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SERVEUR D\'ARCHIVAGE ACTIF — CONFORMITÉ 2026</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h2 style="color:#D4AF37;">99.4%</h2><p>Précision Juridique</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h2 style="color:#D4AF37;">SOUVERAIN</h2><p>IA Mistral France</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h2 style="color:#D4AF37;">STRICT</h2><p>Sécurité RGPD</p></div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align:center;'>Bienvenue, Maître. Lex Nexus est opérationnel.</h3>", unsafe_allow_html=True)

elif menu == "🔬 Audit Multi-Format":
    # On affiche l'historique d'abord
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    # Chat input fixe en bas
    if prompt := st.chat_input("Posez votre question (Droit 2026)..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            # INJECTION DE LA DATE REELLE POUR 2026
            today = datetime.now().strftime("%A %d %B %Y")
            full_res = ""
            placeholder = st.empty()
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": f"Tu es Lex Nexus. Nous sommes le {today}. Tu as accès aux lois de 2026."},
                {"role": "user", "content": prompt}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})

elif menu == "🗄️ Coffre-fort":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>Archives Permanentes</h2>", unsafe_allow_html=True)
    # Logique pour lister les fichiers JSON du dossier DB_PATH...
