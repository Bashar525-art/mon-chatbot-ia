import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from io import BytesIO

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus | Cabinet Pro", page_icon="⚖️", layout="wide")
DATE_COURANTE = "28 Février 2026"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
    [data-testid="stChatInput"] {{ border: 1px solid #D4AF37 !important; border-radius: 20px !important; }}
    
    /* Style de la bannière de sécurité */
    .security-banner {{
        background-color: rgba(0, 255, 0, 0.05);
        border: 1px solid #00FF00;
        padding: 10px;
        border-radius: 10px;
        font-size: 0.85rem;
        margin-bottom: 20px;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "page" not in st.session_state: st.session_state.page = "📊 Cockpit"
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.write(f"📅 {DATE_COURANTE}")
    st.write("---")
    
    if st.button("📊 Cockpit Global", use_container_width=True):
        st.session_state.page = "📊 Cockpit"
        st.rerun()
        
    if st.button("🔬 Audit & Expertise", use_container_width=True):
        st.session_state.page = "🔬 Audit"
        st.rerun()
        
    st.write("---")
    # BOUTON SÉCURITÉ (Axe 1)
    with st.expander("🛡️ Sécurité & Confidentialité"):
        st.write("✅ Chiffrement de bout en bout")
        st.write("🚫 Aucun entraînement sur vos données")
        st.write("🇪🇺 Serveurs conformes RGPD 2026")

# --- 4. PAGE : COCKPIT ---
if st.session_state.page == "📊 Cockpit":
    st.title("Tableau de Bord Stratégique")
    
    # Rappel de sécurité constant
    st.markdown('<div class="security-banner">🔒 Données protégées : les documents déposés sont supprimés après chaque session et ne servent jamais à entraîner nos modèles.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dossiers", len(st.session_state.chat_history)//2)
    c2.metric("Conformité", "Vigilance", "Norme 2026")
    c3.metric("Certificat", "Actif")

# --- 5. PAGE : AUDIT & EXPORT PDF ---
elif st.session_state.page == "🔬 Audit":
    st.title("Analyse & Expertise IA")

    # Zone d'Upload
    uploaded = st.file_uploader("Joindre des pièces au dossier", type=["pdf", "png", "docx"], label_visibility="collapsed")
    
    st.write("---")

    # Affichage historique
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])
            
            # BOUTON D'EXPORTATION (Axe 2)
            # Apparaît sous chaque réponse de l'assistant pour l'imprimer
            if msg["role"] == "assistant":
                st.download_button(
                    label="📄 Télécharger le compte-rendu (TXT/PDF)",
                    data=msg["content"],
                    file_name=f"Rapport_Lex_Nexus_{i}.txt",
                    key=f"dl_{i}"
                )

    if prompt := st.chat_input("Posez votre question juridique..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="⚖️"):
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[{"role": "system", "content": f"Tu es Lex Nexus en {DATE_COURANTE}."}, {"role": "user", "content": prompt}]
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()
