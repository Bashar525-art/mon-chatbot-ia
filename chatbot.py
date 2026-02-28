import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus | Excellence 2026", page_icon="⚖️", layout="wide")
DATE_COURANTE = "28 Février 2026"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
    /* On stylise la barre de chat officielle pour qu'elle soit dorée */
    [data-testid="stChatInput"] {{
        border: 1px solid #D4AF37 !important;
        border-radius: 20px !important;
    }}
    .metric-container {{
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "page" not in st.session_state: st.session_state.page = "📊 Cockpit"
if "fichiers_charges" not in st.session_state: st.session_state.fichiers_charges = []

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. SIDEBAR : TOUS LES OUTILS AU MÊME ENDROIT ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>📅 {DATE_COURANTE}</p>", unsafe_allow_html=True)
    
    st.write("---")
    # Menu de Navigation
    nav = st.radio("Navigation", ["📊 Cockpit Global", "🔬 Audit & Expertise"], label_visibility="collapsed")
    st.session_state.page = nav

    st.write("---")
    # ZONE DE FICHIERS DÉPLACÉE ICI POUR ÉVITER LES DOUBLES BARRES
    st.markdown("### 📂 Gestion des documents")
    uploaded = st.file_uploader("Ajouter des pièces au dossier", type=["pdf", "docx", "png", "jpg"], accept_multiple_files=True)
    if uploaded:
        st.session_state.fichiers_charges = [f.name for f in uploaded]
        st.success(f"{len(uploaded)} fichiers prêts.")

    st.write("---")
    if st.button("✨ Réinitialiser tout", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. PAGE : COCKPIT ---
if st.session_state.page == "📊 Cockpit Global":
    st.markdown("<h1 style='color:#D4AF37;'>Tableau de Bord Stratégique</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-container"><p>Documents au dossier</p><h2>{len(st.session_state.fichiers_charges)}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-container"><p>Requêtes IA</p><h2>{len(st.session_state.chat_history)//2}</h2></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-container"><p>Statut</p><h2 style="color:#00FF00;">Opérationnel</h2></div>', unsafe_allow_html=True)

    # Graphique Radar
    df_radar = pd.DataFrame({
        'Critère': ['Conformité', 'Social', 'Fiscal', 'PI', 'Risques'],
        'Score': [85, 70, 90, 80, 75]
    })
    fig = px.line_polar(df_radar, r='Score', theta='Critère', line_close=True)
    fig.update_traces(fill='toself', line_color='#D4AF37')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", polar=dict(bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True)

# --- 5. PAGE : AUDIT (UNE SEULE BARRE EN BAS) ---
elif st.session_state.page == "🔬 Audit & Expertise":
    st.markdown("<h1 style='color:#D4AF37;'>Analyse & Expertise IA</h1>", unsafe_allow_html=True)
    
    # Historique propre
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # LA SEULE ET UNIQUE BARRE (st.chat_input est toujours en bas de page)
    if prompt := st.chat_input("Posez votre question juridique ici..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="⚖️"):
            # L'IA prend en compte les fichiers chargés dans la sidebar
            context = f"Fichiers : {', '.join(st.session_state.fichiers_charges)}" if st.session_state.fichiers_charges else "Aucun fichier."
            
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {"role": "system", "content": f"Tu es Lex Nexus. Date : {DATE_COURANTE}. Contexte : {context}"},
                    {"role": "user", "content": prompt}
                ]
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()
