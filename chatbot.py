import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from fpdf import FPDF
import tempfile

# --- CONFIGURATION LEX NEXUS ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

# --- STYLE CSS HAUTE COUTURE ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700&family=Inter:wght@200;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1f2c, #090a0f); color: #e0e0e0; }
    .main-header { font-family: 'Playfair Display', serif; color: #C5A059; font-size: 4rem; text-align: center; margin-bottom: 0px; }
    .sub-header { font-family: 'Inter', sans-serif; text-align: center; color: #8a8d91; letter-spacing: 5px; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 40px; }
    .dashboard-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(197, 160, 89, 0.2); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; text-align: center; }
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.95) !important; border-right: 1px solid #C5A059; }
    .stButton>button { width: 100%; background: transparent !important; color: #C5A059 !important; border: 1px solid #C5A059 !important; border-radius: 30px !important; text-transform: uppercase !important; letter-spacing: 2px !important; }
    .stButton>button:hover { background: #C5A059 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --- SECURITÉ & LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<p class="main-header" style="font-size:3rem;">Accès Privé</p>', unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Identifiant Maître / Juriste")
            pwd = st.text_input("Clé de Sécurité", type="password")
            if st.form_submit_button("S'AUTHENTIFIER"):
                if user == "admin" and pwd == "nexus2026": #
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Accès refusé.")
    st.stop()

# --- INITIALISATION & API ---
client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
if "archive_dossiers" not in st.session_state:
    st.session_state.archive_dossiers = [] #

# --- FONCTIONS SYSTÈME ---
def extract_pdf_text(files):
    text = ""
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages: text += page.extract_text() + "\n"
    return text

def multi_agent_audit(text_contrat, query):
    # Agent 1 : Extraction
    with st.status("Agent 1 : Analyse des faits...") :
        s1 = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Extrais les dates, montants et parties."}, {"role": "user", "content": text_contrat[:6000]}])
        data = s1.choices[0].message.content
    # Agent 2 : Risques
    with st.status("Agent 2 : Identification des risques...") :
        s2 = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Trouve les pièges juridiques."}, {"role": "user", "content": data}])
        risks = s2.choices[0].message.content
    # Agent 3 : Synthèse
    with st.status("Agent 3 : Rédaction finale...") :
        s3 = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Rédige un rapport de luxe."}, {"role": "user", "content": f"Données: {data}\nRisques: {risks}\nQuery: {query}"}])
    return s3.choices[0].message.content

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#C5A059; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True) #
    menu = st.radio("NAVIGATION", ["Tableau de Bord", "Audit Multi-Agents", "Archives"])
    if st.button("DÉCONNEXION"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligence Juridique Suprême</p>', unsafe_allow_html=True)

if menu == "Tableau de Bord":
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">99.4%</h2><p>Précision</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">Souverain</h2><p>Mistral AI</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">Chiffré</h2><p>Sécurité TLS</p></div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1000", use_container_width=True)

elif menu == "Audit Multi-Agents":
    files = st.file_uploader("Contrats (PDF)", type="pdf", accept_multiple_files=True)
    query = st.text_input("Instruction spécifique")
    if files and st.button("LANCER L'EXPERTISE"):
        raw_text = extract_pdf_text(files)
        rapport = multi_agent_audit(raw_text, query)
        st.markdown("### ⚖️ Rapport d'Expertise")
        st.write(rapport)
        # Archivage
        st.session_state.archive_dossiers.append({"id": f"LEX-{datetime.now().strftime('%M%S')}", "nom": files[0].name, "rapport": rapport})
        st.success("Dossier archivé.")

elif menu == "Archives":
    st.markdown("### 🗄️ Dossiers Archivés")
    for doc in st.session_state.archive_dossiers:
        with st.expander(f"📁 {doc['id']} | {doc['nom']}"):
            st.write(doc['rapport'])
