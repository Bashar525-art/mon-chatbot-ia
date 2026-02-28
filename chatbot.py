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

# --- 1. CONFIGURATION & DESIGN IMMERSIF ---
st.set_page_config(page_title="Lex Nexus | Supreme Legal AI", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background: #07080C; color: #E0E0E0; }
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3.5rem; }
    .glass-card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(212, 175, 55, 0.2); padding: 20px; border-radius: 15px; }
    .agent-box { border-left: 4px solid #D4AF37; padding-left: 15px; margin: 10px 0; background: rgba(212, 175, 55, 0.05); }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "vault" not in st.session_state: st.session_state.vault = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 3. FONCTIONS EXPERTES ---

def generate_flowchart_logic(analysis):
    """Simule la création d'un schéma logique de contrat"""
    st.markdown("### 🗺️ Flowchart Logique du Contrat")
    st.info("Génération du graphe de décision en cours...")
    st.code("Début -> Signature -> Paiement (J+30) -> Livraison -> Fin", language="mermaid")

def predict_justice_stats():
    """Module Axe 3 : Open Data Justice"""
    stats = pd.DataFrame({
        "Juridiction": ["Paris", "Lyon", "Marseille", "Bordeaux"],
        "Délai Moyen (mois)": [14, 11, 13, 10],
        "Indemnité Moyenne (€)": [15200, 12800, 11500, 13100]
    })
    return stats

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("MODULES SUPRÊMES", [
        "🏛️ Cockpit Prédictif", 
        "⚔️ Conseil de Guerre (Multi-Agents)", 
        "🤝 Négociation & Redline",
        "🗄️ Coffre-fort & Échéancier"
    ])
    if st.button("✨ RESET SYSTEM"): st.session_state.clear(); st.rerun()

# --- PAGE 1 : COCKPIT & DATA JUSTICE ---
if menu == "🏛️ Cockpit Prédictif":
    st.markdown("<p class='main-header'>Cockpit Lex Nexus</p>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown('<div class="glass-card"><h4>📊 Statistiques Jurisprudencielles (Live)</h4></div>', unsafe_allow_html=True)
        st.table(predict_justice_stats())
        
    with col_right:
        st.markdown('<div class="glass-card"><h4>⚖️ Probabilité de Succès</h4></div>', unsafe_allow_html=True)
        # Jauge interactive
        fig = go.Figure(go.Indicator(mode="gauge+number", value=78, gauge={'bar': {'color': "#D4AF37"}}))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=250)
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2 : MULTI-AGENTS (CONSEIL DE GUERRE) ---
elif menu == "⚔️ Conseil de Guerre (Multi-Agents)":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>Le Conseil des Experts</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Soumettre le dossier au conseil", type=["pdf", "docx"])
    
    if st.button("LANCER LE DÉBAT JURIDIQUE"):
        with st.spinner("Les agents débattent..."):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown('<div class="agent-box"><b>🛡️ L\'Avocat (Défense)</b><br>Je détecte 3 clauses limitant vos droits. Il faut les annuler.</div>', unsafe_allow_html=True)
            with col_b:
                st.markdown('<div class="agent-box"><b>🕵️ Le Procureur (Risques)</b><br>Attention à la clause 4.2, elle permet une rupture sans indemnité.</div>', unsafe_allow_html=True)
            with col_c:
                st.markdown('<div class="agent-box"><b>⚖️ Le Juge (Synthèse)</b><br>Le contrat est acceptable à 65% après révision de la clause de PI.</div>', unsafe_allow_html=True)
        
        # Ajout du Flowchart (Axe 2)
        generate_flowchart_logic("Analyse")
        

# --- PAGE 3 : NÉGOCIATION (REDLINE) ---
elif menu == "🤝 Négociation & Redline":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>Négociation Assistée</h2>", unsafe_allow_html=True)
    ton = st.select_slider("Ton de la négociation", options=["Diplomate", "Standard", "Ferme", "Agressif"])
    
    st.markdown("""
    | Clause Originale | Correction Lex Nexus | Argument de Négociation |
    | :--- | :--- | :--- |
    | "Responsabilité nulle" | "Responsabilité limitée à 2x le prix" | "Conformité Art. 1231 Code Civil" |
    """)
    st.button("📧 Générer le mail de réponse")

# --- PAGE 4 : COFFRE-FORT & CALENDRIER ---
elif menu == "🗄️ Coffre-fort & Échéancier":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>Échéancier de Veille</h2>", unsafe_allow_html=True)
    st.info("📅 Rappel : Renouvellement Contrat IT dans 12 jours.")
    st.write("---")
    if st.session_state.vault:
        st.dataframe(pd.DataFrame(st.session_state.vault))
