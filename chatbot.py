import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from mistralai import Mistral

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Lex Nexus | Cockpit", page_icon="⚖️", layout="wide")

# Forcer la date en 2026 pour l'IA
DATE_SYSTEME = "28 Février 2026"

st.markdown(f"""
<style>
    /* Fond sombre et texte clair */
    .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
    
    /* Cacher les éléments inutiles de Streamlit */
    [data-testid="stChatInput"] {{ display: none !important; }}
    footer {{visibility: hidden;}}
    
    /* Style du Cockpit (Cartes) */
    .metric-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }}
    
    /* BARRE DE SAISIE FIXE EN BAS (Style Gemini) */
    .fixed-input-container {{
        position: fixed;
        bottom: 20px;
        left: 55%;
        transform: translateX(-50%);
        width: 70%;
        background: #1A1D24;
        border: 1px solid #D4AF37;
        border-radius: 30px;
        padding: 8px 20px;
        display: flex;
        align-items: center;
        z-index: 9999;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
</style>
""", unsafe_allow_html=True)

# Initialisation des données
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "page" not in st.session_state: st.session_state.page = "📊 Cockpit"

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. SIDEBAR (NAVIGATION) ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.info(f"📅 Date : {DATE_SYSTEME}")
    
    # Boutons de navigation qui fonctionnent vraiment
    if st.button("📊 Cockpit Global", use_container_width=True):
        st.session_state.page = "📊 Cockpit"
        st.rerun()
    if st.button("🔬 Audit & Vision", use_container_width=True):
        st.session_state.page = "🔬 Audit"
        st.rerun()
        
    st.divider()
    if st.button("✨ Reset"):
        st.session_state.clear()
        st.rerun()

# --- 3. PAGE : COCKPIT (ENFIN VISIBLE) ---
if st.session_state.page == "📊 Cockpit":
    st.title("Cockpit Juridique Stratégique")
    
    # KPIs en haut
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>Santé Globale</h3><h2 style="color:#D4AF37;">84%</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>Niveau de Risque</h3><h2 style="color:#FF4B4B;">Bas</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>Dossiers Ouverts</h3><h2 style="color:#00FF00;">12</h2></div>', unsafe_allow_html=True)

    st.write("---")
    
    # Graphique Radar pour montrer que c'est du sérieux
    left, right = st.columns([1.5, 1])
    with left:
        df_radar = pd.DataFrame({
            'Critère': ['Conformité', 'Social', 'Fiscal', 'PI', 'Contractuel'],
            'Score': [80, 65, 90, 75, 85]
        })
        fig = px.line_polar(df_radar, r='Score', theta='Critère', line_close=True)
        fig.update_traces(fill='toself', line_color='#D4AF37')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    
    with right:
        st.subheader("📢 Alertes 2026")
        st.warning("Nouvelle directive IA Act : Mise à jour nécessaire sous 12 jours.")
        st.info("Jurisprudence : Le secret des affaires renforcé par la cour d'appel.")

# --- 4. PAGE : AUDIT (AVEC BARRE GEMINI FIXE) ---
elif st.session_state.page == "🔬 Audit":
    st.header("Analyse & Expertise IA")
    
    # Zone de chat (on laisse de la place en bas pour la barre fixe)
    chat_space = st.container()
    with chat_space:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        st.write("<br><br><br><br><br><br>", unsafe_allow_html=True) # Espace pour ne pas cacher le dernier msg

    # BARRE DE SAISIE GEMINI
    with st.form(key="chat_bar", clear_on_submit=True):
        # On simule la barre stylée avec des colonnes Streamlit
        c1, c2, c3, c4 = st.columns([0.5, 0.5, 8, 1])
        c1.markdown("🖼️") # Photo
        c2.markdown("📎") # Fichier
        query = c3.text_input("", placeholder="Demandez n'importe quoi à Lex Nexus...", label_visibility="collapsed")
        submit = c4.form_submit_button("✉️")

    if submit and query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        with st.chat_message("assistant"):
            sys_prompt = f"Tu es Lex Nexus. Nous sommes le {DATE_SYSTEME}. Réponds en expert juridique de 2026."
            res = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": query}]
            )
            reponse_ia = res.choices[0].message.content
            st.write(reponse_ia)
            st.session_state.chat_history.append({"role": "assistant", "content": reponse_ia})
            st.rerun()

    # Uploader caché pour les fichiers
    st.file_uploader("Upload", type=["pdf", "png", "jpg"], label_visibility="collapsed")
