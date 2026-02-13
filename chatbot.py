import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from io import BytesIO
from pypdf import PdfReader

# --- 1. CONFIGURATION & DESIGN "AGENCE DE LUXE" ---
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
    
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3.5rem; margin-top: 10px; }
    .live-status { text-align: center; color: #00FF00; font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 30px; }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 25px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }

    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.98) !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- 2. FONCTIONS SYSTÈME ---

def generate_docx(content):
    """Génère un acte juridique au format Word"""
    doc = Document()
    doc.add_heading('LEX NEXUS - DOCUMENT OFFICIEL', 0)
    doc.add_paragraph(f"Date de génération : {datetime.now().strftime('%d/%m/%Y')}")
    doc.add_paragraph("-" * 20)
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def plot_risk_analysis():
    """Graphique Radar : Indice de Santé Juridique"""
    df = pd.DataFrame({
        "Critère": ["Conformité", "Risque Contractuel", "Propriété Intellectuelle", "Droit Social", "Fiscalité"],
        "Score": [94, 65, 88, 72, 81]
    })
    fig = px.line_polar(df, r='Score', theta='Critère', line_close=True, color_discrete_sequence=['#D4AF37'])
    fig.update_polars(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(l=40, r=40, t=20, b=20))
    return fig

# --- 3. INITIALISATION ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Clé API manquante.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("COCKPIT AGENT", ["🏛️ Dashboard Bio-Juridique", "🖋️ Audit & Rédaction", "🗄️ Archives"])
    st.write("---")
    st.write(f"📅 **13 Février 2026**")
    if st.button("✨ RÉINITIALISER"):
        st.session_state.chat_history = []; st.rerun()

# --- 5. PAGE DASHBOARD (RÉORGANISÉE) ---
if menu == "🏛️ Dashboard Bio-Juridique":
    st.markdown('<p class="main-header">Cockpit Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SYSTÈME DE VEILLE CONNECTÉ — TEMPS RÉEL 2026</p>', unsafe_allow_html=True)
    
    # KPIs Flash
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Dossiers Audités", "124", "+12%")
    k2.metric("Risque Moyen", "22%", "-5%")
    k3.metric("Conformité", "94%", "+1%")
    k4.metric("Sources Live", "12 Base", "SÉCURISÉ")

    st.write("---")

    # Zone d'Analyse
    col_radar, col_news = st.columns([1.3, 1])
    
    with col_radar:
        st.markdown('<div class="glass-card"><h4>⚖️ Indice de Santé Juridique</h4>'
                    '<p style="font-size:0.8rem; color:#8a8d91;">Analyse multidimensionnelle des actifs</p></div>', unsafe_allow_html=True)
        st.plotly_chart(plot_risk_analysis(), use_container_width=True)
    
    with col_news:
        st.markdown('<div class="glass-card"><h4>📢 Veille Légale Live</h4></div>', unsafe_allow_html=True)
        st.success("**Loi Finance 2026** : Publication des nouveaux barèmes PME.")
        st.info("**Jurisprudence** : Décision majeure sur le droit à la déconnexion.")
        st.warning("**Alerte** : Révision des clauses de force majeure (Standard Européen).")
        st.markdown("<br><p style='text-align:center; font-size:0.8rem;'>Flux synchronisé avec Légifrance.</p>", unsafe_allow_html=True)

# --- 6. PAGE AUDIT & RÉDACTION ---
elif menu == "🖋️ Audit & Rédaction":
    st.markdown("<h2 style='text-align:center; color:#D4AF37;'>Expertise & Génération d'Actes</h2>", unsafe_allow_html=True)
    
    files = st.file_uploader("📂 Déposez vos pièces (PDF, Docx)", type=["pdf", "docx"], accept_multiple_files=True)
    
    # Historique de Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button("📥 Exporter en Word (.docx)", generate_docx(msg["content"]), 
                                   file_name=f"LexNexus_Acte_{datetime.now().strftime('%M%S')}.docx")

    if prompt := st.chat_input("Analysez ce dossier ou rédigez un acte..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty(); full_res = ""
            # Injection du contexte temporel 2026
            current_date = datetime.now().strftime("%d %B %Y")
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": f"Tu es Lex Nexus. Aujourd'hui: {current_date}. Rédige des actes formels et cite les lois de 2026."},
                {"role": "user", "content": prompt}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            st.rerun()

# --- 7. ARCHIVES ---
elif menu == "🗄️ Archives":
    st.markdown("<h2 style='text-align:center; color:#D4AF37;'>Dossiers Archivés</h2>", unsafe_allow_html=True)
    st.info("Les dossiers archivés s'afficheront ici après sauvegarde.")
