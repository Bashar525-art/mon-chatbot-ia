import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

# (Garder le bloc CSS Or & Noir ici...)
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700&family=Inter:wght@200;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1f2c, #090a0f); color: #e0e0e0; }
    .main-header { font-family: 'Playfair Display', serif; color: #C5A059; font-size: 3.5rem; text-align: center; margin-bottom: 0px; }
    .sub-header { font-family: 'Inter', sans-serif; text-align: center; color: #8a8d91; letter-spacing: 5px; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 40px; }
    .dashboard-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(197, 160, 89, 0.2); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; text-align: center; }
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.95) !important; border-right: 1px solid #C5A059; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Clé API manquante.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

if "archive_dossiers" not in st.session_state:
    # On initialise avec une archive vide pour éviter les KeyError
    st.session_state.archive_dossiers = []

# --- FONCTIONS ---
def extract_pdf_text(files):
    text = ""
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted: text += extracted + "\n"
    return text

def multi_agent_audit(text_contrat, query):
    with st.status("Analyse en cours par les agents Lex Nexus...") :
        # Agent 1 : Extraction
        s1 = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Analyseur juridique."}, {"role": "user", "content": text_contrat[:6000]}])
        data = s1.choices[0].message.content
        # Agent 2 : Synthèse
        s2 = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Rédacteur de rapport de luxe."}, {"role": "user", "content": f"Fais un rapport sur : {data}. Question : {query}"}])
        return s2.choices[0].message.content

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#C5A059; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    menu = st.radio("NAVIGATION", ["Tableau de Bord", "Audit Multi-Agents", "Archives des Dossiers"])
    if st.button("🗑️ VIDER LA SESSION"):
        st.session_state.archive_dossiers = []
        st.rerun()

st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">INTELLIGENCE JURIDIQUE SUPRÊME</p>', unsafe_allow_html=True)

if menu == "Tableau de Bord":
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">99.4%</h2><p>Précision</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">FRANCE</h2><p>Souveraineté</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">SSL</h2><p>Sécurité</p></div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1000", use_container_width=True)

elif menu == "Audit Multi-Agents":
    files = st.file_uploader("Fichiers PDF", type="pdf", accept_multiple_files=True)
    query = st.text_input("Instruction")
    if files and st.button("LANCER L'AUDIT"):
        raw_text = extract_pdf_text(files)
        rapport = multi_agent_audit(raw_text, query)
        st.markdown(rapport)
        # On enregistre avec toutes les clés nécessaires pour éviter l'erreur
        st.session_state.archive_dossiers.append({
            "id": f"DS-{datetime.now().strftime('%M%S')}", 
            "nom": files[0].name, 
            "rapport": rapport,
            "date": datetime.now().strftime("%d/%m/%Y")
        })

elif menu == "Archives des Dossiers":
    st.markdown("### 🗄️ Historique des Analyses")
    if not st.session_state.archive_dossiers:
        st.info("Aucune archive disponible.")
    else:
        for doc in st.session_state.archive_dossiers:
            with st.expander(f"📁 {doc.get('id', 'N/A')} | {doc.get('nom', 'Document')} ({doc.get('date', '')})"):
                # Utilisation sécurisée de .get() pour éviter KeyError
                st.markdown(doc.get('rapport', "Contenu non trouvé."))
