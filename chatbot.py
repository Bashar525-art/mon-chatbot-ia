import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO

# --- 1. STYLE & CONFIG ---
st.set_page_config(page_title="Lex Nexus | Enterprise AI", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background: #0A0B10; color: #E0E0E0; }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.3); padding: 20px; border-radius: 15px; }
    .status-live { color: #00FF00; font-size: 0.8rem; font-weight: bold; animation: blink 2s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "vault" not in st.session_state:
    st.session_state.vault = [] # Stockage des dossiers
if "legal_scores" not in st.session_state:
    st.session_state.legal_scores = {"Conformité": 80, "Risque": 30, "PI": 70, "Social": 65, "Fiscalité": 75}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. FONCTIONS TECHNIQUES ---
def plot_prediction_gauge(probability):
    """Jauge de probabilité de gain (Axe 4)"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability,
        title = {'text': "Probabilité de Gain (Contentieux)", 'font': {'color': "#D4AF37", 'size': 20}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#D4AF37"},
            'steps': [
                {'range': [0, 40], 'color': "rgba(255, 0, 0, 0.3)"},
                {'range': [40, 70], 'color': "rgba(255, 165, 0, 0.3)"},
                {'range': [70, 100], 'color': "rgba(0, 255, 0, 0.3)"}],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white", 'family': "Inter"})
    return fig

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("MENU EXPERT", ["🏛️ Cockpit & Prédiction", "🔬 Audit & Signature", "🗄️ Coffre-fort Client"])
    st.write("---")
    if st.button("✨ CLEAR ALL"):
        st.session_state.clear(); st.rerun()

# --- PAGE 1 : DASHBOARD & PRÉDICTION ---
if menu == "🏛️ Cockpit & Prédiction":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif;'>Intelligence Prédictive</h2>", unsafe_allow_html=True)
    
    col_gauge, col_stats = st.columns([1.5, 1])
    
    with col_gauge:
        # On simule une probabilité basée sur les dossiers actuels
        prob = 72 if len(st.session_state.vault) > 0 else 0
        st.plotly_chart(plot_prediction_gauge(prob), use_container_width=True)
        
        
    with col_stats:
        st.markdown('<div class="glass-card"><h4>Prochaines Échéances</h4>', unsafe_allow_html=True)
        if not st.session_state.vault:
            st.write("Aucun contrat en veille.")
        else:
            for item in st.session_state.vault:
                st.write(f"📅 **{item['expiration']}** : {item['nom']}")

# --- PAGE 2 : AUDIT & SIGNATURE ---
elif menu == "🔬 Audit & Signature":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif;'>Audit & Scellé Numérique</h2>", unsafe_allow_html=True)
    files = st.file_uploader("Déposer le contrat", type=["pdf", "docx"])
    
    if prompt := st.chat_input("Analysez et sécurisez ce contrat..."):
        with st.chat_message("assistant", avatar="⚖️"):
            full_res = "Analyse en cours... (Simulation de l'expertise 2026)"
            st.markdown(full_res)
            
            # AXE 2 : Simulation de Signature
            st.success("✅ Document certifié conforme par Lex Nexus IA. Scellé numérique apposé.")
            
            # AXE 3 : Ajout auto au coffre-fort avec date fictive
            if files:
                new_doc = {
                    "nom": files[0].name,
                    "date_audit": datetime.now().strftime("%d/%m/%Y"),
                    "expiration": (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"),
                    "statut": "Signé / Sécurisé"
                }
                st.session_state.vault.append(new_doc)
                st.info(f"Dossier '{files[0].name}' ajouté au Coffre-fort (Échéance : 2027)")

# --- PAGE 3 : COFFRE-FORT CLIENT ---
elif menu == "🗄️ Coffre-fort Client":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif;'>Gestion des Dossiers Permanents</h2>", unsafe_allow_html=True)
    
    if not st.session_state.vault:
        st.info("Le coffre-fort est vide. Auditez un document pour le sauvegarder.")
    else:
        df_vault = pd.DataFrame(st.session_state.vault)
        st.table(df_vault)
        st.download_button("📥 Exporter le Registre (CSV)", df_vault.to_csv(), "registre_legal.csv")
