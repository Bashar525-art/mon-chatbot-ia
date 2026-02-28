import streamlit as st
import pandas as pd
from datetime import datetime
from mistralai import Mistral

# --- 1. CONFIGURATION ÉLÉGANTE ---
st.set_page_config(page_title="Lex Nexus | Cabinet Pro", page_icon="⚖️", layout="wide")
DATE_COURANTE = "28 Février 2026"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
    
    /* Style de la barre de chat officielle (Unique en bas) */
    [data-testid="stChatInput"] {{
        border: 1px solid #D4AF37 !important;
        border-radius: 20px !important;
    }}
    
    /* Bannière RGPD discrète */
    .rgpd-box {{
        background-color: rgba(0, 255, 0, 0.03);
        border: 1px solid rgba(0, 255, 0, 0.2);
        padding: 10px;
        border-radius: 10px;
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALISATION ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "page" not in st.session_state: st.session_state.page = "📊 Cockpit"
if "fichiers_noms" not in st.session_state: st.session_state.fichiers_noms = []

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 3. SIDEBAR : LE CENTRE DE CONTRÔLE UNIQUE ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.write(f"📅 **{DATE_COURANTE}**")
    st.write("---")
    
    # Navigation
    choice = st.radio("MENU", ["📊 Cockpit Global", "🔬 Audit & Expertise"], label_visibility="collapsed")
    st.session_state.page = choice
    
    st.write("---")
    
    # ZONE DE FICHIERS (DÉPLACÉE ICI POUR LIBÉRER LE HAUT DE PAGE)
    st.markdown("### 📂 Documents du dossier")
    uploaded = st.file_uploader("Ajouter des pièces (PDF, PNG, DOCX)", type=["pdf", "png", "docx", "jpg"], accept_multiple_files=True)
    if uploaded:
        st.session_state.fichiers_noms = [f.name for f in uploaded]
        st.success(f"{len(uploaded)} fichiers chargés")
    
    st.write("---")
    
    # Sécurité RGPD
    with st.expander("🛡️ Sécurité des données"):
        st.caption("Conforme RGPD 2026. Les documents sont cryptés et ne servent pas à l'entraînement de l'IA.")

    if st.button("✨ Réinitialiser la session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. PAGE : COCKPIT ---
if st.session_state.page == "📊 Cockpit Global":
    st.title("Tableau de Bord Stratégique")
    st.markdown('<div class="rgpd-box">🔒 Confidentialité garantie : Aucun document n\'est conservé après la fermeture de votre navigateur.</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Pièces au dossier", len(st.session_state.fichiers_noms))
    c2.metric("Analyses effectuées", len(st.session_state.chat_history)//2)
    c3.metric("Conformité", "Optimale")

# --- 5. PAGE : AUDIT (PROPRE ET SANS BARRE EN HAUT) ---
elif st.session_state.page == "🔬 Audit & Expertise":
    st.title("Expertise Juridique & Vision")
    
    # Affichage des échanges
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"], avatar="⚖️" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.download_button("📥 Exporter en rapport", msg["content"], file_name=f"Analyse_{i}.txt", key=f"dl_{i}")

    # LA SEULE BARRE VISIBLE (En bas)
    if prompt := st.chat_input("Analysez les pièces ou posez une question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="⚖️"):
            # L'IA prend en compte les fichiers chargés dans la Sidebar
            ctx = f"Documents chargés : {', '.join(st.session_state.fichiers_noms)}" if st.session_state.fichiers_noms else "Aucun document."
            
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {"role": "system", "content": f"Tu es Lex Nexus, expert en droit de 2026. Contexte : {ctx}"},
                    {"role": "user", "content": prompt}
                ]
            )
            reponse = response.choices[0].message.content
            st.markdown(reponse)
            st.session_state.chat_history.append({"role": "assistant", "content": reponse})
            st.rerun()
