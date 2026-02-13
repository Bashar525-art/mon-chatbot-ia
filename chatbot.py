import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

# STYLE CSS (CHAT FIXE ET DESIGN)
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1f2c, #090a0f); color: #E0E0E0; }
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3rem; margin-bottom: 0px; }
    .sub-header { font-family: 'Inter', sans-serif; text-align: center; color: #8a8d91; letter-spacing: 5px; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 40px; }
    
    /* Style des bulles de chat */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 10px; margin-bottom: 10px; }
    
    /* Barre latérale */
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.95) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Clé API Mistral manquante.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "archive_dossiers" not in st.session_state:
    st.session_state.archive_dossiers = []

# --- FONCTION EXTRACTION ---
def extract_pdf_text(files):
    text = ""
    for f in files:
        try:
            reader = PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        except: continue
    return text

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("NAVIGATION", ["🏛️ Dashboard", "🔬 Audit Expert", "🗄️ Archives"])
    st.write("---")
    if st.button("🗑️ NOUVELLE SESSION"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">L\'EXCELLENCE DU DROIT AUGMENTÉ</p>', unsafe_allow_html=True)

# --- PAGE AUDIT EXPERT ---
if menu == "🔬 Audit Expert":
    # 1. Zone de documents (ne bloque plus le chat)
    uploaded_files = st.file_uploader("📂 Déposer vos pièces jointes (Optionnel)", type="pdf", accept_multiple_files=True)
    
    # 2. Affichage de l'historique (au centre)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar="⚖️" if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

    # 3. BARRE DE CHAT FIXE EN BAS (st.chat_input)
    # Elle est toujours visible, peu importe où on est sur la page
    if prompt := st.chat_input("Votre question juridique ou instruction d'audit..."):
        
        # Affichage du message utilisateur
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Réponse de l'IA avec STREAMING pour la vitesse
        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty() # Zone pour l'affichage progressif
            full_response = ""
            
            # Récupération du contexte
            context = ""
            if uploaded_files:
                context = f"CONTEXTE (Fichiers joints) :\n{extract_pdf_text(uploaded_files)[:8000]}\n\n"

            # Appel API en mode Stream
            try:
                stream_response = client.chat.stream(
                    model="pixtral-12b-2409",
                    messages=[
                        {"role": "system", "content": "Tu es Lex Nexus, expert en droit. Réponds avec précision."},
                        {"role": "user", "content": context + prompt}
                    ]
                )
                
                for chunk in stream_response:
                    content = chunk.data.choices[0].delta.content
                    if content:
                        full_response += content
                        placeholder.markdown(full_response + "▌") # Effet d'écriture
                
                placeholder.markdown(full_response) # Texte final
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                
                # Archivage auto si documents présents
                if uploaded_files:
                    st.session_state.archive_dossiers.append({"id": f"AUD-{datetime.now().strftime('%M%S')}", "nom": uploaded_files[0].name, "rapport": full_response, "date": datetime.now().strftime("%d/%m")})
            
            except Exception as e:
                st.error("Une erreur technique est survenue. Veuillez réessayer.")

# --- AUTRES PAGES (Dashboard, Archives) ---
elif menu == "🏛️ Dashboard":
    st.image("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1000", use_container_width=True)
    st.markdown("### Bienvenue, Maître. Lex Nexus est prêt pour vos analyses.")

elif menu == "🗄️ Archives":
    st.markdown("### 🗄️ Historique des Travaux")
    for doc in st.session_state.archive_dossiers:
        with st.expander(f"📁 {doc['id']} | {doc['nom']}"):
            st.markdown(doc['rapport'])
