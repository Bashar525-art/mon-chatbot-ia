import streamlit as st
import pandas as pd
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO
import base64

# --- 1. CONFIGURATION & STYLE SUPRÊME ---
st.set_page_config(page_title="Lex Nexus Prime", page_icon="⚖️", layout="wide")
CURRENT_DATE_2026 = "28 Février 2026"

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* CACHE LA BARRE GRISE DE STREAMLIT DEFINITIVEMENT */
    footer {visibility: hidden;}
    [data-testid="stChatInput"] { display: none !important; }

    /* STYLE DE TA BARRE DORÉE UNIQUE */
    .custom-chat-wrapper {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 85%;
        max-width: 800px;
        background: #1A1D24;
        border: 1px solid rgba(212, 175, 55, 0.5);
        border-radius: 30px;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        z-index: 9999;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .custom-input {
        background: transparent;
        border: none;
        color: white;
        flex-grow: 1;
        outline: none;
        font-size: 16px;
        margin: 0 15px;
    }

    .icon-btn { color: #8a8d91; font-size: 1.2rem; cursor: pointer; transition: 0.3s; }
    .icon-btn:hover { color: #D4AF37; }
    .send-btn { color: #D4AF37; font-size: 1.3rem; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS 2026</h1>", unsafe_allow_html=True)
    st.write(f"📅 **{CURRENT_DATE_2026}**")
    mode = st.selectbox("MODULE", ["🔬 Audit Vision & Texte", "📊 Cockpit"])
    if st.button("🔌 Reset System"):
        st.session_state.clear()
        st.rerun()

# --- 3. LOGIQUE DU CHAT ---
if mode == "🔬 Audit Vision & Texte":
    st.header("Analyse & Expertise 2026")

    # Affichage des messages existants
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # LA BARRE UNIQUE (On utilise un formulaire Streamlit caché derrière le design HTML)
    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([0.5, 0.5, 8, 1])
        with cols[0]: st.markdown("🖼️") # Icône Photo
        with cols[1]: st.markdown("📎") # Icône Trombone
        user_input = cols[2].text_input("", placeholder="Demander à Lex Nexus...", label_visibility="collapsed")
        submit = cols[3].form_submit_button("✉️")

    if submit and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {"role": "system", "content": f"Tu es Lex Nexus. Date: {CURRENT_DATE_2026}. Expert Juridique."},
                    {"role": "user", "content": user_input}
                ]
            )
            ans = response.choices[0].message.content
            st.write(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

    # Ajout d'un petit uploader discret pour que les icônes servent à quelque chose
    st.file_uploader("Ajouter des pièces jointes", type=["pdf", "png", "jpg"], label_visibility="collapsed")
