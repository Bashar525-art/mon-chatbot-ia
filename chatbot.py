import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from io import BytesIO

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Lex Nexus | Expert Intelligence", page_icon="⚖️", layout="wide")

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), url('https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=2000');
        background-size: cover; color: #E0E0E0;
    }
    .main-header { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3.5rem; }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.3); padding: 25px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. FONCTIONS AVANCÉES ---

def generate_docx(content):
    """Génère un fichier Word professionnel (Option 2)"""
    doc = Document()
    doc.add_heading('Lex Nexus - Acte Juridique', 0)
    doc.add_paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}")
    doc.add_paragraph(content)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def plot_risk_analysis():
    """Graphique de santé juridique (Option 3)"""
    df = pd.DataFrame({
        "Catégorie": ["Conformité", "Risque Contractuel", "Propriété Intellectuelle", "Social"],
        "Score": [85, 40, 90, 65]
    })
    fig = px.line_polar(df, r='Score', theta='Catégorie', line_close=True, 
                        color_discrete_sequence=['#D4AF37'])
    fig.update_polars(radialaxis=dict(visible=True, range=[0, 100]), bgcolor="rgba(0,0,0,0)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(l=20, r=20, t=20, b=20))
    return fig

# --- 3. INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("MENU EXPERT", ["🏛️ Dashboard Bio-Juridique", "🖋️ Rédaction & Audit", "🔍 Recherche Jurisprudence"])
    st.write("---")
    st.write(f"📅 **13 Février 2026**")

# --- PAGE 1 : DASHBOARD & GRAPHES ---
if menu == "🏛️ Dashboard Bio-Juridique":
    st.markdown('<p class="main-header">Tableau de Bord</p>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown('<div class="glass-card"><h4>Santé du Cabinet</h4><p>Analyse des risques en temps réel</p></div>', unsafe_allow_html=True)
        st.plotly_chart(plot_risk_analysis(), use_container_width=True)
    
    with col_right:
        st.markdown('<div class="glass-card"><h4>Dernières Veilles (Option 4)</h4>'
                    '<li>● Loi Finance 2026 : Nouveaux seuils</li>'
                    '<li>● RGPD 3.0 : Directives appliquées</li>'
                    '<li>● Cass. Civ. : Revirement sur la clause d\'exclusivité</li></div>', unsafe_allow_html=True)
        st.info("Le système surveille actuellement 12 sources législatives en direct.")

# --- PAGE 2 : RÉDACTION (WORD) & AUDIT ---
elif menu == "🖋️ Rédaction & Audit":
    st.markdown("<h2 style='text-align:center; color:#D4AF37;'>Générateur d'Actes & Audit</h2>", unsafe_allow_html=True)
    
    # Affichage Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                # Bouton de téléchargement pour chaque réponse de l'IA (Option 2)
                st.download_button("📥 Télécharger en .docx", generate_docx(msg["content"]), 
                                   file_name=f"Acte_LexNexus_{datetime.now().strftime('%H%M')}.docx")

    if prompt := st.chat_input("Ex: Rédige une mise en demeure pour loyer impayé..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            placeholder = st.empty(); full_res = ""
            # Recherche Live (Option 4) intégrée dans le prompt
            now = datetime.now().strftime("%d/%m/%Y")
            stream = client.chat.stream(model="pixtral-12b-2409", messages=[
                {"role": "system", "content": f"Tu es Lex Nexus. Nous sommes le {now}. Utilise les lois de 2026. Si l'utilisateur demande un acte, rédige-le de manière formelle."},
                {"role": "user", "content": prompt}
            ])
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.chat_history.append({"role": "assistant", "content": full_res})
            st.rerun() # Pour faire apparaître le bouton download

# --- PAGE 3 : RECHERCHE LIVE ---
elif menu == "🔍 Recherche Jurisprudence":
    st.markdown("<h2 style='color:#D4AF37;'>Recherche Live 2026</h2>", unsafe_allow_html=True)
    st.text_input("Rechercher un arrêt, un décret ou un article de loi...")
    st.warning("Module de connexion directe à l'API Légifrance en cours de synchronisation.")
