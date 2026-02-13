import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Lex Nexus | Cockpit Juridique", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.9)), 
                    url('https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=2000');
        background-size: cover;
        background-attachment: fixed;
        color: #E0E0E0;
    }
    
    /* Zone de Drag & Drop stylisée */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #D4AF37 !important;
        background: rgba(212, 175, 55, 0.05) !important;
        border-radius: 15px !important;
        padding: 40px !important;
    }

    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3.5rem; }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.3); padding: 25px; border-radius: 15px; backdrop-filter: blur(10px); }
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.98) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "legal_scores" not in st.session_state:
    st.session_state.legal_scores = {"Conformité": 74, "Risque": 45, "PI": 82, "Social": 61, "Fiscalité": 78}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. FONCTIONS TECHNIQUES ---
def read_file_content(file):
    name = file.name.lower()
    try:
        if name.endswith(".pdf"):
            return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
        elif name.endswith(".docx"):
            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        elif name.endswith(".txt"):
            return file.read().decode()
    except: return f"Erreur de lecture sur {file.name}"
    return ""

def generate_docx(content):
    doc = Document()
    doc.add_heading('LEX NEXUS - DOCUMENT OFFICIEL', 0)
    doc.add_paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}")
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("NAVIGATION", ["🏛️ Dashboard", "🔬 Audit & Rédaction"])
    st.write("---")
    if st.button("✨ RÉINITIALISER TOUT"):
        st.session_state.clear()
        st.rerun()

# --- 5. PAGE DASHBOARD ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Cockpit Lex Nexus</p>', unsafe_allow_html=True)
    
    # KPIs
    k1, k2, k3 = st.columns(3)
    scores = st.session_state.legal_scores
    k1.metric("Santé Juridique", f"{sum(scores.values())//len(scores)}%", "+2%")
    k2.metric("Risque Détecté", f"{100 - scores.get('Risque', 50)}%", "-4%")
    k3.metric("Dossiers Audités", len(st.session_state.chat_history)//2, "Live")

    st.write("---")
    
    # Radar Chart
    df = pd.DataFrame({"Critère": list(scores.keys()), "Score": list(scores.values())})
    fig = px.line_polar(df, r='Score', theta='Critère', line_close=True, color_discrete_sequence=['#D4AF37'])
    fig.update_polars(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# --- 6. PAGE AUDIT (ZONE DRAG & DROP) ---
elif menu == "🔬 Audit & Rédaction":
    st.markdown("<h2 style='text-align:center; color:#D4AF37;'>Déposez vos documents pour expertise</h2>", unsafe_allow_html=True)
    
    # Zone de dépôt massive
    uploaded_files = st.file_uploader(
        "GLISSEZ VOS FICHIERS ICI (PDF, DOCX, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True,
        label_visibility="collapsed" # On cache le label pour un look plus épuré
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} fichier(s) prêt(s) pour l'analyse.")

    # Affichage Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button("📥 Télécharger en Word", generate_docx(msg["content"]), file_name="LexNexus_Document.docx")

    if prompt := st.chat_input("Analysez ces documents ou posez votre question juridique..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            context = ""
            if uploaded_files:
                for f in uploaded_files: context += f"\n--- {f.name} ---\n{read_file_content(f)}\n"
            
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": f"Tu es Lex Nexus. Expert juridique 2026. Analyse et rédige."},
                {"role": "user", "content": f"DOCS:\n{context[:8000]}\n\nQUESTION: {prompt}"}
            ])
            full_res = ""
            placeholder = st.empty()
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            
            # Mise à jour des scores pour le radar
            for k in st.session_state.legal_scores:
                st.session_state.legal_scores[k] = min(100, st.session_state.legal_scores[k] + 2)
            st.rerun()
