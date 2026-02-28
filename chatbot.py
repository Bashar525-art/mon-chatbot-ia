import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO

# --- 1. CONFIGURATION & CORE ENGINE ---
st.set_page_config(page_title="Lex Nexus OS | 2026 Edition", page_icon="⚖️", layout="wide")

# FIX DATE : On définit la date de référence pour tout le système
# On force l'année 2026 pour que l'IA ne divague plus
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

# Initialisation
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "legal_scores" not in st.session_state: st.session_state.legal_scores = {"Conformité": 85, "Risque": 20, "PI": 90}

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#D4AF37;'>LEX NEXUS 2026</h1>", unsafe_allow_html=True)
    st.info(f"📅 Date Système : {CURRENT_DATE_2026}")
    mode = st.selectbox("MODULE", ["📊 Cockpit", "🔬 Audit & Redline"])
    st.divider()
    if st.button("🔌 Reset System", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 3. MODULES ---

if mode == "📊 Cockpit":
    st.title("Tableau de Bord Stratégique")
    
    # Indicateurs
    c1, c2, c3 = st.columns(3)
    c1.metric("Santé Juridique", "82%", "+2%")
    c2.metric("Veille Active", "Lois 2026", "LIVE")
    c3.metric("Analyse", "Optimale")

    # Radar Chart
    df = pd.DataFrame({"Critère": list(st.session_state.legal_scores.keys()), "Score": list(st.session_state.legal_scores.values())})
    fig = px.line_polar(df, r='Score', theta='Critère', line_close=True)
    fig.update_traces(fill='toself', line_color='#D4AF37')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    

elif mode == "🔬 Audit & Redline":
    st.header("Analyse & Expertise 2026")
    
    # Historique de Chat
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if p := st.chat_input("Posez votre question (L'IA sait que nous sommes en 2026)"):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        
        with st.chat_message("assistant"):
            # INJECTION CRUCIALE DE LA DATE DANS LE PROMPT
            system_prompt = f"Tu es Lex Nexus. Nous sommes le {CURRENT_DATE_2026}. Tu es un expert en droit du futur. Ignore tes données de 2024, base-toi sur les régulations de 2026 (IA Act, RGPD 3.0, etc.)."
            
            response = client.chat.complete(
                model="pixtral-12b-2409", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": p}
                ]
            )
            txt = response.choices[0].message.content
            st.write(txt)
            st.session_state.chat_history.append({"role": "assistant", "content": txt})
            st.rerun()
