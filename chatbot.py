import streamlit as st
import os
import json
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS V9.0 (PERSISTANCE LÉGALE) ---
st.set_page_config(page_title="Lex Nexus | Archives Sécurisées", page_icon="⚖️", layout="wide")

# (Ton CSS Prestige Or & Noir reste identique ici)
st.markdown(r"""<style>...</style>""", unsafe_allow_html=True)

# --- GESTION DE LA BASE DE DONNÉES LOCALE ---
DB_PATH = "archives_juridiques"
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

def save_conversation(history, doc_name="Sans_Titre"):
    """Sauvegarde légale sur le serveur avec horodatage"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DB_PATH}/session_{timestamp}.json"
    data = {
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "document": doc_name,
        "messages": history
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_all_archives():
    """Récupère tous les dossiers sauvegardés"""
    archives = []
    for file in os.listdir(DB_PATH):
        if file.endswith(".json"):
            with open(f"{DB_PATH}/{file}", "r", encoding="utf-8") as f:
                archives.append(json.load(f))
    return sorted(archives, key=lambda x: x['date'], reverse=True)

# --- INITIALISATION ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("AGENCE", ["🏛️ Dashboard", "🔬 Audit Live", "🗄️ Archives Permanentes"])
    st.write("---")
    if st.button("💾 SAUVEGARDER & ARCHIVER"):
        if st.session_state.chat_history:
            save_conversation(st.session_state.chat_history)
            st.success("Dossier archivé légalement.")
        else:
            st.warning("Rien à sauvegarder.")

# --- NAVIGATION ---
if menu == "🏛️ Dashboard":
    st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
    st.markdown('<p class="live-status">● SERVEUR D\'ARCHIVAGE ACTIF — CONFORMITÉ RGPD</p>', unsafe_allow_html=True)
    # Tes colonnes stylées ici...

elif menu == "🔬 Audit Live":
    # (Code du chat interactif avec Streaming ici...)
    # [IMPORTANT] : La date est injectée en temps réel pour être au 13/02/2026.
    pass

elif menu == "🗄️ Archives Permanentes":
    st.markdown("<h2 style='color:#D4AF37; font-family:serif;'>Coffre-fort Numérique</h2>", unsafe_allow_html=True)
    archives = load_all_archives()
    
    if not archives:
        st.info("Le coffre-fort est vide.")
    else:
        for arc in archives:
            with st.expander(f"📁 Session du {arc['date']} | {arc.get('document')}"):
                for m in arc['messages']:
                    st.write(f"**{m['role'].upper()}** : {m['content']}")
                st.download_button("📥 Exporter en JSON", json.dumps(arc), file_name="archive_legal.json")
                
