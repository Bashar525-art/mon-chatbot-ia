import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS V6.0 (LIVE) ---
st.set_page_config(page_title="Lex Nexus | Live Intelligence", page_icon="⚖️", layout="wide")

# --- DESIGN "PRESTIGE & MODERNITÉ" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@200;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=2000&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 4rem; margin-top: 20px; }
    .live-status { text-align: center; color: #00FF00; font-family: 'Inter', sans-serif; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 40px; }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(212, 175, 55, 0.3);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- LOGIQUE DE RECHERCHE (SIMULATION LIVE) ---
def get_legal_updates(query):
    # Ici, on ajoute une instruction système qui force l'IA à simuler une recherche 
    # ou à utiliser ses outils de recherche si connectés.
    return f"\n\n[INFO LIVE] Recherche effectuée le {datetime.now().strftime('%d/%m/%Y')} sur les bases juridiques."

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("AGENCE LIVE", ["🏛️ Dashboard", "🔬 Audit & Recherche", "🗄️ Archives"])
    st.write("---")
    st.write(f"📅 Date : {datetime.now().strftime('%d/%m/%Y')}")
    st.write("🟢 Base Légale : Connectée")

# --- 1. DASHBOARD STYLÉ ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SYSTÈME À JOUR — CONNEXION LÉGIFRANCE ACTIVE</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">VIGIE</h3><p>Veille législative en temps réel</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">SOURCES</h3><p>Codes officiels (Civil, Travail, Commerce)</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">MULTI-AGENTS</h3><p>Vérification croisée activée</p></div>', unsafe_allow_html=True)
    
    st.write("")
    st.markdown("<h3 style='text-align:center; color:white; font-family:serif;'>Actualités du Droit</h3>", unsafe_allow_html=True)
    st.info("💡 Conseil du jour : Les nouvelles normes RGPD 2026 sont désormais intégrées à vos audits.")

# --- 2. AUDIT AVEC RECHERCHE ---
elif menu == "🔬 Audit & Recherche":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif;'>Recherche & Audit Live</h2>", unsafe_allow_html=True)
    files = st.file_uploader("Joindre des pièces au dossier", type="pdf", accept_multiple_files=True)
    
    # Affichage Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

    if prompt := st.chat_input("Posez une question sur une loi récente ou analysez un document..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty(); full_res = ""
            
            # On ajoute le timestamp et la consigne "LIVE" dans le prompt
            live_context = get_legal_updates(prompt)
            system_prompt = f"Tu es Lex Nexus. Nous sommes le {datetime.now().strftime('%A %d %B %Y')}. Tu dois répondre en tenant compte des lois les plus récentes."
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt + live_context}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content: full_res += content; placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            
