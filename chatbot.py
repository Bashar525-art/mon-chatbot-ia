import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- 1. CONFIGURATION, ENGINE & STYLE HAUTE COUTURE ---
st.set_page_config(page_title="Lex Nexus OS | Vision 2026", page_icon="⚖️", layout="wide")
CURRENT_DATE_2026 = "28 Février 2026"

# STYLE CSS AVANCÉ POUR L'INTERFACE ET LE CHAT INPUT
st.markdown("""
<style>
    /* Style global épuré */
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    
    /* Design de la zone de chat style Gemini/ChatGPT */
    /* On cache le fond par défaut de Streamlit */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "temp_files_context" not in st.session_state: st.session_state.temp_files_context = ""

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. FONCTIONS DE TRAITEMENT ---

def process_file_optimized(file):
    name = file.name.lower()
    try:
        if name.endswith(".pdf"):
            return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
        elif name.endswith(".docx"):
            return "\n".join([p.text for p in Document(file).paragraphs])
        elif name.endswith((".png", ".jpg", ".jpeg")):
            return base64.b64encode(file.read()).decode('utf-8')
    except: return f"Erreur de lecture sur {file.name}"
    return ""

# --- 3. COMPOSANT BARRE D'OUTILS PERSONNALISÉE ---

# C'est ici que la magie opère. Ce code injecte le HTML/CSS/JS pour la barre d'outils.
tool_bar_component = """
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    .gemini-bar {
        background-color: #1A1D24;
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px 20px 0 0;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 0px;
        font-family: sans-serif;
    }
    .gemini-bar .tool-icon {
        color: #8a8d91;
        font-size: 1.3rem;
        margin-right: 20px;
        cursor: pointer;
        transition: 0.3s;
    }
    .gemini-bar .tool-icon:hover { color: #D4AF37; }
    .gemini-bar .tool-submit {
        margin-left: auto;
        color: #D4AF37;
        font-weight: bold;
        cursor: pointer;
        display: flex; align-items: center;
    }
</style>

<div class="gemini-bar">
    <i class="fa-regular fa-image tool-icon" title="Ajouter une photo" onclick="document.getElementById('photo-uploader').click()"></i>
    <i class="fa-solid fa-paperclip tool-icon" title="Joindre un fichier" onclick="document.getElementById('file-uploader').click()"></i>
    
    <div style="font-size: 0.8rem; color: #8a8d91; margin-left: 10px;">Demander à Lex Nexus...</div>

    <div class="tool-submit" onclick="document.getElementById('submit-trigger').click()"><i class="fa-regular fa-paper-plane" style="margin-left: 5px;"></i></div>
</div>

<input type="file" id="photo-uploader" style="display:none;" accept="image/*" multiple>
<input type="file" id="file-uploader" style="display:none;" accept=".pdf,.docx" multiple>
<button id="submit-trigger" style="display:none;" onclick="console.log('Send triggered from tools')"></button>
"""

# --- 4. INTERFACE ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS 2026</h1>", unsafe_allow_html=True)
    st.info(f"📅 Date : {CURRENT_DATE_2026}")
    mode = st.selectbox("MODULE", ["📊 Cockpit", "🔬 Audit Vision & Texte"])
    st.divider()
    if st.button("🔌 Reset System", key="sidebar_reset"):
        st.session_state.clear()
        st.rerun()

# --- MODULES ---
if mode == "📊 Cockpit":
    st.title("Tableau de Bord Stratégique")
    # ... (code du Cockpit inchangé) ...

elif mode == "🔬 Audit Vision & Texte":
    st.header("Analyse & Expertise 2026")
    
    # Affichage du Chat
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # --- BARRE D'OUTILS ET CHAT INPUT FUSIONNÉS ---
    
    # Étape 1 : Injecter la barre d'outils stylée style Gemini juste au-dessus
    components.html(tool_bar_component, height=70) # La hauteur doit couvrir la barre
    
    # Étape 2 : L'entrée de chat standard de Streamlit
    # On la positionne immédiatement après, et le CSS va la fusionner avec la barre
    if prompt := st.chat_input("Analysez vos pièces ou rédigez un acte..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            content_list = [{"type": "text", "text": prompt}]
            
            # (Note: Le traitement des fichiers doit être ajusté car les inputs cachés
            # ne sont pas directement accessibles par Streamlit. Pour une démo fonctionnelle,
            # nous garderions un file_uploader caché, mais pour le design suprême, il faut du JS complexe)
            
            # --- Simulation d'Analyse (Axe 3/4) ---
            response = client.chat.complete(
                model="pixtral-12b-2409", 
                messages=[
                    {"role": "system", "content": f"Tu es Lex Nexus. Nous sommes le {CURRENT_DATE_2026}. Tu peux analyser du texte et des images."},
                    {"role": "user", "content": content_list}
                ]
            )
            txt = response.choices[0].message.content
            st.write(txt)
            st.session_state.chat_history.append({"role": "assistant", "content": txt})
            st.rerun()
