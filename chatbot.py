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

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Lex Nexus | Dynamic Intelligence", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), 
                    url('https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=2000');
        background-size: cover; background-attachment: fixed; color: #E0E0E0;
    }
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3.5rem; }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.3); padding: 25px; border-radius: 15px; backdrop-filter: blur(10px); }
</style>
""", unsafe_allow_html=True)

# --- 2. GESTION DES SCORES DYNAMIQUES ---
# Initialise les scores par défaut si c'est la première fois
if "legal_scores" not in st.session_state:
    st.session_state.legal_scores = {
        "Conformité": 70, "Risque Contractuel": 50, 
        "Propriété Intellectuelle": 60, "Droit Social": 55, "Fiscalité": 65
    }

def update_scores_from_ai(analysis_text):
    """Simule l'extraction de scores depuis l'analyse de l'IA (en situation réelle, on demanderait à l'IA un JSON)"""
    # Ici, on simule une amélioration des scores suite à l'audit
    for key in st.session_state.legal_scores:
        if st.session_state.legal_scores[key] < 95:
            st.session_state.legal_scores[key] += 5 

# --- 3. FONCTIONS VISUELLES ---
def plot_risk_analysis():
    df = pd.DataFrame({
        "Critère": list(st.session_state.legal_scores.keys()),
        "Score": list(st.session_state.legal_scores.values())
    })
    fig = px.line_polar(df, r='Score', theta='Critère', line_close=True, color_discrete_sequence=['#D4AF37'])
    fig.update_polars(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(l=40, r=40, t=20, b=20))
    return fig

# --- 4. INITIALISATION MISTRAL ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 5. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("COCKPIT", ["🏛️ Dashboard Dynamique", "🖋️ Audit & Rédaction"])
    st.write("---")
    st.write(f"📅 **13 Février 2026**")
    if st.button("🔄 RESET ANALYSE"):
        st.session_state.legal_scores = {"Conformité": 70, "Risque Contractuel": 50, "Propriété Intellectuelle": 60, "Droit Social": 55, "Fiscalité": 65}
        st.session_state.chat_history = []
        st.rerun()

# --- PAGE DASHBOARD ---
if menu == "🏛️ Dashboard Dynamique":
    st.markdown('<p class="main-header">Cockpit Lex Nexus</p>', unsafe_allow_html=True)
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Santé Globale", f"{sum(st.session_state.legal_scores.values())//5}%", "+3%")
    k2.metric("Dossiers en cours", len(st.session_state.chat_history)//2, "Live")
    k3.metric("État du Serveur", "Optimal", "2026")

    st.write("---")
    col_radar, col_desc = st.columns([1.5, 1])
    
    with col_radar:
        st.plotly_chart(plot_risk_analysis(), use_container_width=True)
    
    with col_desc:
        st.markdown('<div class="glass-card"><h4>Interprétation du Radar</h4></div>', unsafe_allow_html=True)
        for critere, score in st.session_state.legal_scores.items():
            color = "green" if score > 80 else "orange" if score > 50 else "red"
            st.markdown(f"**{critere}** : :{color}[{score}%]")
        st.info("💡 Les scores augmentent à chaque fois que vous passez un contrat à l'audit.")

# --- PAGE AUDIT ---
elif menu == "🖋️ Audit & Rédaction":
    st.markdown("<h2 style='text-align:center; color:#D4AF37;'>Expertise & Scoring Live</h2>", unsafe_allow_html=True)
    
    files = st.file_uploader("📂 Déposez un document pour analyse et mise à jour du radar", type=["pdf", "docx"])
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Analysez ce contrat..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty(); full_res = ""
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": "Tu es Lex Nexus. Analyse le document et propose des améliorations juridiques."},
                {"role": "user", "content": prompt}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            
            # MISE À JOUR AUTOMATIQUE DU RADAR
            update_scores_from_ai(full_res)
            st.success("Radar de santé juridique mis à jour sur le Dashboard !")
            st.rerun()
