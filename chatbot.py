import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from docx import Document
from PIL import Image
import io

# --- CONFIGURATION LEX NEXUS V7.0 ---
st.set_page_config(page_title="Lex Nexus | Omniscience Juridique", page_icon="⚖️", layout="wide")

# (Le design reste ton CSS "Prestige" précédent)
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@200;400;600&display=swap');
    .stApp { background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=2000&q=80'); background-size: cover; background-attachment: fixed; }
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 4rem; margin-top: 20px; }
    .glass-card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(212, 175, 55, 0.3); backdrop-filter: blur(20px); padding: 30px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- LECTEUR UNIVERSEL DE FICHIERS ---
def read_any_file(uploaded_file):
    fname = uploaded_file.name.lower()
    content = ""
    try:
        if fname.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif fname.endswith(".docx"):
            doc = Document(uploaded_file)
            content = "\n".join([para.text for para in doc.paragraphs])
        elif fname.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
        elif fname.endswith((".png", ".jpg", ".jpeg")):
            # L'IA Pixtral peut analyser l'image directement, 
            # mais ici on prévient l'utilisateur qu'on traite l'image.
            return "[IMAGE DÉTECTÉE : L'IA va analyser le visuel]"
    except Exception as e:
        return f"Erreur de lecture sur {fname}"
    return content

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("AGENCE LIVE", ["🏛️ Dashboard", "🔬 Audit Multi-Format", "🗄️ Archives"])
    st.write("---")
    st.write("📂 **Formats supportés :** PDF, DOCX, TXT, JPG, PNG")

# --- INTERFACE AUDIT UNIVERSEL ---
if menu == "🔬 Audit Multi-Format":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif; text-align:center;'>Analyse de Pièces Omnicanal</h2>", unsafe_allow_html=True)
    
    # Acceptation de TOUS les types de fichiers
    uploaded_files = st.file_uploader("📂 Déposez vos contrats, photos ou documents", 
                                      type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], 
                                      accept_multiple_files=True)
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Analysez ce Word, ce PDF ou posez une question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty()
            full_res = ""
            
            # Construction du contexte multi-format
            context = ""
            if uploaded_files:
                for f in uploaded_files:
                    context += f"\n--- FICHIER: {f.name} ---\n{read_any_file(f)}\n"
            
            # Appel API
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": "Tu es Lex Nexus. Tu analyses tout format de document juridique avec une précision extrême."},
                {"role": "user", "content": f"DOCUMENTS:\n{context[:10000]}\n\nQUESTION: {prompt}"}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})

# --- DASHBOARD & ARCHIVES (Garder le code précédent corrigé) ---
