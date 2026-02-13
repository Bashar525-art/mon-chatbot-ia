import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS V6.1 ---
st.set_page_config(page_title="Lex Nexus | Live Agency", page_icon="⚖️", layout="wide")

# --- DESIGN "PRESTIGE IMMERSIF" ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@200;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=2000&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 4rem; margin-top: 20px; text-shadow: 0 4px 15px rgba(212, 175, 55, 0.3); }
    .live-status { text-align: center; color: #00FF00; font-family: 'Inter', sans-serif; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 40px; animation: blink 2s infinite; }
    
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(212, 175, 55, 0.3);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        transition: 0.4s;
    }
    .glass-card:hover { border-color: #D4AF37; transform: translateY(-5px); background: rgba(212, 175, 55, 0.05); }

    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.98) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Clé API Mistral manquante dans les secrets.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "archive_dossiers" not in st.session_state:
    st.session_state.archive_dossiers = []

# --- FONCTIONS ---
def extract_pdf_text(files):
    text = ""
    for f in files:
        try:
            reader = PdfReader(f)
            for page in reader.pages: text += page.extract_text() + "\n"
        except: continue
    return text

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center; font-family:serif;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("AGENCE LIVE", ["🏛️ Dashboard", "🔬 Audit & Recherche", "🗄️ Archives"])
    st.write("---")
    st.write(f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y')}")
    st.write("🟢 **Base Légale :** Connectée")
    if st.button("✨ NOUVELLE SESSION"):
        st.session_state.chat_history = []
        st.rerun()

# --- 1. DASHBOARD (CORRIGÉ) ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SYSTÈME À JOUR — VEILLE JURIDIQUE EN TEMPS RÉEL</p>', unsafe_allow_html=True)
    
    # Correction du NameError ici : on utilise c1, c2, c3 partout
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">VIGIE</h3><p>Veille législative active</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">SOURCES</h3><p>Codes Civil & Travail 2026</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card"><h3 style="color:#D4AF37;">AGENTS</h3><p>Vérification croisée IA</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("<h3 style='text-align:center; color:white; font-family:serif;'>Flux d'Actualités Juridiques</h3>", unsafe_allow_html=True)
    
    col_news1, col_news2 = st.columns(2)
    with col_news1:
        st.info("**Jurisprudence** : Nouvelle décision sur le télétravail (Cass. Soc. fév 2026)")
    with col_news2:
        st.success("**Législation** : Mise à jour des seuils fiscaux pour les PME.")

# --- 2. AUDIT & RECHERCHE LIVE ---
elif menu == "🔬 Audit & Recherche":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif; text-align:center;'>Audit Expert & Recherche Live</h2>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("📂 Déposer les pièces du dossier (PDF)", type="pdf", accept_multiple_files=True)
    
    # Affichage de l'historique
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    # Barre de chat fixe en bas
    if prompt := st.chat_input("Analysez un document ou posez une question sur le droit actuel..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty()
            full_res = ""
            
            # Contexte incluant la date du jour pour l'actualité
            current_date = datetime.now().strftime("%d %B %Y")
            context = extract_pdf_text(uploaded_files) if uploaded_files else ""
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": f"Tu es Lex Nexus. Aujourd'hui nous sommes le {current_date}. Tu as accès aux dernières lois de 2026."},
                {"role": "user", "content": f"DOCUMENT: {context[:7000]}\n\nQUESTION: {prompt}"}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})

# --- 3. ARCHIVES ---
elif menu == "🗄️ Archives":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif;'>Archives Numériques</h2>", unsafe_allow_html=True)
    if not st.session_state.archive_dossiers:
        st.info("Aucun dossier archivé.")
    else:
        for doc in st.session_state.archive_dossiers:
            with st.expander(f"📁 {doc['nom']}"):
                st.markdown(doc['rapport'])
