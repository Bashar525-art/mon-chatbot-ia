import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from docx import Document

# --- 1. CONFIGURATION ÉLÉGANTE ---
st.set_page_config(page_title="Lex Nexus | Excellence 2026", page_icon="⚖️", layout="wide")

# Date fixée pour l'immersion 2026
DATE_COURANTE = "28 Février 2026"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
    
    /* Design des cartes du Cockpit */
    .metric-container {{
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    /* Sidebar Prestige */
    section[data-testid="stSidebar"] {{
        background-color: #111418 !important;
        border-right: 1px solid #D4AF37;
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "mes_documents" not in st.session_state: st.session_state.mes_documents = []
if "page" not in st.session_state: st.session_state.page = "📊 Cockpit"

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. BARRE DE NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>📅 {DATE_COURANTE}</p>", unsafe_allow_html=True)
    st.write("---")
    
    if st.button("📊 Cockpit Global", use_container_width=True):
        st.session_state.page = "📊 Cockpit"
        st.rerun()
        
    if st.button("🔬 Audit & Expertise", use_container_width=True):
        st.session_state.page = "🔬 Audit"
        st.rerun()
        
    st.write("---")
    if st.button("✨ Réinitialiser tout", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. PAGE : COCKPIT (RÉEL ET PROPRE) ---
if st.session_state.page == "📊 Cockpit":
    st.markdown("<h1 style='color:#D4AF37;'>Tableau de Bord Stratégique</h1>", unsafe_allow_html=True)
    
    # Statistiques RÉELLES
    nb_docs = len(st.session_state.mes_documents)
    nb_echanges = len(st.session_state.chat_history) // 2
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-container"><p>Dossiers Analysés</p><h2>{nb_docs}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-container"><p>Requêtes IA</p><h2>{nb_echanges}</h2></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-container"><p>Statut Veille</p><h2 style="color:#00FF00;">Actif</h2></div>', unsafe_allow_html=True)

    st.write("---")
    
    col_radar, col_news = st.columns([1.5, 1])
    with col_radar:
        st.subheader("⚖️ Analyse de Santé Juridique")
        # Radar basé sur des data types
        df_radar = pd.DataFrame({
            'Critère': ['Conformité', 'Social', 'Fiscal', 'PI', 'Risques'],
            'Score': [85, 70, 90, 80, 75]
        })
        fig = px.line_polar(df_radar, r='Score', theta='Critère', line_close=True)
        fig.update_traces(fill='toself', line_color='#D4AF37')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", polar=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)
                
    with col_news:
        st.subheader("📢 Veille 2026")
        st.info("**IA Act** : Mise en conformité obligatoire avant juin.")
        st.warning("**Cyber-sécurité** : Renforcement des amendes RGPD.")

# --- 5. PAGE : AUDIT & EXPERTISE (DESIGN GEMINI PUR) ---
elif st.session_state.page == "🔬 Audit":
    st.markdown("<h1 style='color:#D4AF37;'>Analyse & Expertise IA</h1>", unsafe_allow_html=True)
    
    # 1. Zone de dépôt de documents
    with st.expander("📂 Télécharger les pièces du dossier (PDF, Images, Word)", expanded=True):
        fichiers = st.file_uploader("Glissez vos documents ici", type=["pdf", "docx", "png", "jpg"], accept_multiple_files=True)
        if fichiers:
            st.session_state.mes_documents = [f.name for f in fichiers]
            st.success(f"✅ {len(fichiers)} documents chargés au dossier.")

    st.write("---")

    # 2. Historique de discussion
    for msg in st.session_state.chat_history:
        avatar = "⚖️" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # 3. Saisie Unique (Look Gemini)
    if prompt := st.chat_input("Posez votre question juridique ou demandez un audit..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="⚖️"):
            # Simulation d'analyse IA avec contexte
            context = f"Documents chargés : {', '.join(st.session_state.mes_documents)}"
            system_msg = f"Tu es Lex Nexus. Date : {DATE_COURANTE}. Utilise ce contexte : {context}"
            
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}]
            )
            reponse_texte = response.choices[0].message.content
            st.markdown(reponse_texte)
            st.session_state.chat_history.append({"role": "assistant", "content": reponse_texte})
            st.rerun()
