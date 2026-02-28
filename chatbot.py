import streamlit as st
import pandas as pd
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus Prime", page_icon="⚖️", layout="wide")
CURRENT_DATE_2026 = "28 Février 2026"

# Suppression visuelle des éléments Streamlit inutiles
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    /* Cache l'input par défaut de Streamlit pour éviter le doublon */
    .stChatInput { display: none !important; }
    
    .chat-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        max-width: 900px;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. LE COMPOSANT BARRE UNIQUE ---
# Ce code crée la barre et envoie la valeur à Streamlit quand on appuie sur Entrée ou l'avion
def custom_chat_bar():
    chat_html = f"""
    <div id="wrapper" style="font-family: 'Inter', sans-serif;">
        <div style="background: #1A1D24; border: 1px solid rgba(212, 175, 55, 0.4); border-radius: 25px; padding: 10px 20px; display: flex; align-items: center;">
            <i class="fas fa-image" style="color: #8a8d91; margin-right: 15px; cursor: pointer;"></i>
            <i class="fas fa-paperclip" style="color: #8a8d91; margin-right: 15px; cursor: pointer;"></i>
            <input type="text" id="userInput" placeholder="Demander à Lex Nexus..." 
                style="background: transparent; border: none; color: white; flex-grow: 1; outline: none; font-size: 16px;">
            <i class="fas fa-paper-plane" id="sendBtn" style="color: #D4AF37; cursor: pointer; margin-left: 10px;"></i>
        </div>
    </div>
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    <script>
        const input = document.getElementById('userInput');
        const btn = document.getElementById('sendBtn');
        
        function sendToStreamlit() {{
            const val = input.value;
            if (val) {{
                window.parent.postMessage({{
                    type: 'streamlit:set_widget_value',
                    data: val,
                    widgetId: 'chat_input_value'
                }}, '*');
                input.value = '';
            }}
        }}

        input.addEventListener('keypress', (e) => {{ if (e.key === 'Enter') sendToStreamlit(); }});
        btn.addEventListener('click', sendToStreamlit);
    </script>
    """
    # On utilise un champ texte invisible pour récupérer la valeur du JS
    res = components.html(chat_html, height=70)
    return st.text_input("", key="chat_input_value", label_visibility="collapsed")

# --- 3. INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37;'>LEX NEXUS 2026</h1>", unsafe_allow_html=True)
    mode = st.selectbox("MODULE", ["🔬 Audit Vision & Texte", "📊 Cockpit"])

if mode == "🔬 Audit Vision & Texte":
    st.header("Analyse & Expertise 2026")
    
    # Zone d'affichage des messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # La barre unique en bas
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    user_query = custom_chat_bar()
    st.markdown('</div>', unsafe_allow_html=True)

    # Logique de réponse
    if user_query and (not st.session_state.chat_history or user_query != st.session_state.chat_history[-1].get("content")):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.chat_message("assistant"):
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {"role": "system", "content": f"Tu es Lex Nexus en 2026."},
                    {"role": "user", "content": user_query}
                ]
            )
            ans = response.choices[0].message.content
            st.write(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()
