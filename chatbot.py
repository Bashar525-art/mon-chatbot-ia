import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO
import base64

# --- 1. CONFIGURATION & ENGINE ---
st.set_page_config(page_title="Lex Nexus OS | Vision 2026", page_icon="⚖️", layout="wide")
CURRENT_DATE_2026 = "28 Février 2026"

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .legal-card { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; border-radius: 10px; 
        border-left: 5px solid #D4AF37;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. FONCTIONS DE TRAITEMENT ---

def process_file(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
    elif name.endswith(".docx"):
        return "\n".join([p.text for p in Document(file).paragraphs])
    elif name.endswith((".png", ".jpg", ".jpeg")):
        # On encode l'image en base64 pour l'envoyer à l'IA
        return base64.b64encode(file.read()).decode('utf-8')
    return file.read().decode()

# --- 3. INTERFACE ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#D4AF37;'>LEX NEXUS 2026</h1>", unsafe_allow_html=True)
    st.info(f"📅 Date : {CURRENT_DATE_2026}")
    mode = st.selectbox("MODULE", ["📊 Cockpit", "🔬 Audit Vision & Texte"])
    if st.button("🔌 Reset System"):
        st.session_state.clear()
        st.rerun()

if mode == "📊 Cockpit":
    st.title("Tableau de Bord Stratégique")
    c1, c2, c3 = st.columns(3)
    c1.metric("Santé Juridique", "88%", "+5%")
    c2.metric("Analyse Vision", "Activée", "LIVE")
    c3.metric("Dossiers", len(st.session_state.chat_history)//2)

elif mode == "🔬 Audit Vision & Texte":
    st.header("Analyse Multisensorielle")
    
    # Ajout des formats d'image ici
    uploaded_files = st.file_uploader("Déposez Contrats ou Photos (PDF, DOCX, PNG, JPG)", 
                                     type=["pdf", "docx", "png", "jpg", "jpeg"], 
                                     accept_multiple_files=True)

    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if p := st.chat_input("Analysez ces pièces..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            messages = [
                {"role": "system", "content": f"Tu es Lex Nexus. Nous sommes le {CURRENT_DATE_2026}. Tu peux analyser du texte et des images."},
                {"role": "user", "content": []}
            ]
            
            # Construction du message avec contenu mixte (Texte + Images)
            content_list = [{"type": "text", "text": p}]
            
            if uploaded_files:
                for f in uploaded_files:
                    processed = process_file(f)
                    if f.name.lower().endswith((".png", ".jpg", ".jpeg")):
                        content_list.append({
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{processed}"
                        })
                    else:
                        content_list[0]["text"] += f"\n\nCONTENU DU FICHIER {f.name}:\n{processed}"
            
            messages[1]["content"] = content_list
            
            response = client.chat.complete(model="pixtral-12b-2409", messages=messages)
            txt = response.choices[0].message.content
            st.write(txt)
            st.session_state.chat_history.append({"role": "assistant", "content": txt})
            st.rerun()
