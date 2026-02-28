import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO

# --- 1. CONFIGURATION & CORE ENGINE ---
st.set_page_config(page_title="Lex Nexus OS", page_icon="⚖️", layout="wide")

# Style "Obsidian Night" : Plus léger pour le navigateur
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

# Initialisation silencieuse et robuste
for key in ["legal_scores", "chat_history", "vault"]:
    if key not in st.session_state:
        if key == "legal_scores": st.session_state[key] = {"Conformité": 85, "Risque": 20, "PI": 90}
        else: st.session_state[key] = []

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. LOGIQUE DE NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37;'>LEX NEXUS OS</h1>", unsafe_allow_html=True)
    mode = st.selectbox("MODULE", ["📊 Cockpit", "🔬 Audit & Redline", "⚔️ Conseil de Guerre", "🗄️ Coffre-fort"])
    st.divider()
    if st.button("🔌 Redémarrer le Système", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 3. MODULES ---

if mode == "📊 Cockpit":
    st.title("Tableau de Bord Stratégique")
    
    # KPIs Flash
    c1, c2, c3 = st.columns(3)
    c1.metric("Indice de Santé", f"{sum(st.session_state.legal_scores.values())//3}%")
    c2.metric("Alertes 2026", "3 Actives")
    c3.metric("Dossiers", len(st.session_state.vault))

    # Graphique Radar
    df = pd.DataFrame({"Critère": list(st.session_state.legal_scores.keys()), "Score": list(st.session_state.legal_scores.values())})
    fig = px.line_polar(df, r='Score', theta='Critère', line_close=True)
    fig.update_traces(fill='toself', line_color='#D4AF37')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    
elif mode == "🔬 Audit & Redline":
    st.header("Audit & Négociation Assistée")
    
    file = st.file_uploader("Glisser le contrat ici", type=["pdf", "docx"])
    
    if file:
        st.success(f"Document '{file.name}' chargé.")
        # Simuler une analyse de Redline (Axe 4)
        st.markdown("### 🤝 Propositions de Négociation")
        col_a, col_b = st.columns(2)
        with col_a:
            st.error("**Clause Risquée** : Responsabilité illimitée.")
        with col_b:
            st.success("**Correction Lex Nexus** : Plafonnement à 150% du montant du contrat.")
            
    # Chat Interactif
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if p := st.chat_input("Une question sur le droit en 2026 ?"):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("assistant"):
            response = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "user", "content": p}])
            txt = response.choices[0].message.content
            st.write(txt)
            st.session_state.chat_history.append({"role": "assistant", "content": txt})

elif mode == "⚔️ Conseil de Guerre":
    st.header("Multi-Agent Simulation")
    st.info("Ce module simule un arbitrage entre plusieurs experts juridiques.")
    if st.button("Lancer la Simulation"):
        st.markdown('<div class="legal-card">🕵️ **L\'Avocat (Défense)** : Le risque de nullité est élevé.</div>', unsafe_allow_html=True)
        st.markdown('<div class="legal-card">⚖️ **Le Juge (Arbitre)** : Une médiation est recommandée sous 15 jours.</div>', unsafe_allow_html=True)
