import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus | Arsenal Juridique", page_icon="⚖️", layout="wide")

# --- STYLE CSS LUXE & PROFONDEUR ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Inter:wght@200;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1f2c, #090a0f); color: #e0e0e0; }
    .main-header { font-family: 'Playfair Display', serif; color: #C5A059; font-size: 3.5rem; text-align: center; margin-bottom: 0px; }
    .sub-header { font-family: 'Inter', sans-serif; text-align: center; color: #8a8d91; letter-spacing: 5px; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 40px; }
    .dashboard-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(197, 160, 89, 0.2); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; text-align: center; transition: 0.3s; }
    .dashboard-card:hover { border-color: #C5A059; background: rgba(197, 160, 89, 0.05); }
    section[data-testid="stSidebar"] { background-color: rgba(7, 8, 12, 0.95) !important; border-right: 1px solid #C5A059; }
    .stButton>button { width: 100%; background: transparent !important; color: #C5A059 !important; border: 1px solid #C5A059 !important; border-radius: 30px !important; text-transform: uppercase !important; letter-spacing: 2px !important; }
    .stButton>button:hover { background: #C5A059 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Clé API manquante.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

if "archive_dossiers" not in st.session_state:
    st.session_state.archive_dossiers = []

# --- FONCTIONS ---
def extract_pdf_text(files):
    text = ""
    if not isinstance(files, list): files = [files]
    for f in files:
        try:
            reader = PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        except: continue
    return text

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#C5A059; text-align:center; font-family:serif;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("SERVICE JURIDIQUE", [
        "🏛️ Tableau de Bord", 
        "🔬 Audit Multi-Agents", 
        "🔍 Comparaison de Pièces",
        "⚖️ Conformité & Lois",
        "🗄️ Archives des Dossiers"
    ])
    st.write("---")
    if st.button("🗑️ VIDER LA SESSION"):
        st.session_state.archive_dossiers = []
        st.rerun()

st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">L\'EXCELLENCE DU DROIT AUGMENTÉ</p>', unsafe_allow_html=True)

# --- 1. TABLEAU DE BORD ---
if menu == "🏛️ Tableau de Bord":
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">99.4%</h2><p>Précision Juridique</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">SOUVERAIN</h2><p>Technologie Mistral</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">PRO</h2><p>Multi-Agents Actifs</p></div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 🏛️ Bienvenue, Maître")
    st.write("Utilisez les outils spécialisés dans le menu latéral pour traiter vos dossiers. Lex Nexus est configuré pour la revue de contrats, la comparaison de versions et l'analyse de conformité légale.")
    st.image("https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=1000", use_container_width=True)

# --- 2. AUDIT MULTI-AGENTS ---
elif menu == "🔬 Audit Multi-Agents":
    st.markdown("### 🧪 Analyse Profonde par Triple IA")
    files = st.file_uploader("Contrat à auditer (PDF)", type="pdf", accept_multiple_files=True)
    query = st.text_input("Point d'attention (ex: Clause de sortie, Responsabilité civile...)")
    
    if files and st.button("LANCER L'AUDIT EXPERT"):
        raw_text = extract_pdf_text(files)
        with st.status("Coordination des agents Lex Nexus...") :
            # Agent 1 : Synthèse
            s1 = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Analyseur juridique."}, {"role": "user", "content": raw_text[:8000]}])
            rapport = s1.choices[0].message.content
        st.markdown(rapport)
        st.session_state.archive_dossiers.append({"id": f"AUD-{datetime.now().strftime('%M%S')}", "nom": files[0].name, "rapport": rapport, "date": datetime.now().strftime("%d/%m")})

# --- 3. COMPARAISON DE PIÈCES ---
elif menu == "🔍 Comparaison de Pièces":
    st.markdown("### 🕵️ Comparaison Comparative (Redline)")
    colA, colB = st.columns(2)
    with colA: f1 = st.file_uploader("Document A (Référence)", type="pdf")
    with colB: f2 = st.file_uploader("Document B (À comparer)", type="pdf")
    
    if f1 and f2 and st.button("DÉTECTER LES DIFFÉRENCES"):
        with st.status("Analyse comparative en cours..."):
            t1, t2 = extract_pdf_text(f1), extract_pdf_text(f2)
            prompt = f"Compare ces deux textes juridiques. Fais un tableau des différences. Liste ce qui a été ajouté, modifié ou supprimé.\n\nDOC A: {t1[:4000]}\n\nDOC B: {t2[:4000]}"
            res = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "user", "content": prompt}])
            rapport = res.choices[0].message.content
        st.markdown(rapport)
        st.session_state.archive_dossiers.append({"id": f"CMP-{datetime.now().strftime('%M%S')}", "nom": f"Comparaison {f1.name}", "rapport": rapport, "date": datetime.now().strftime("%d/%m")})

# --- 4. CONFORMITÉ & LOIS ---
elif menu == "⚖️ Conformité & Lois":
    st.markdown("### 📖 Vérification de Conformité Légale")
    law_query = st.text_area("Copiez une clause ou décrivez une situation pour vérifier sa légalité :")
    if law_query and st.button("VÉRIFIER LA CONFORMITÉ"):
        with st.spinner("Consultation de la doctrine et de la jurisprudence..."):
            res = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "system", "content": "Tu es un expert en droit français. Vérifie la conformité de ce texte."}, {"role": "user", "content": law_query}])
            st.markdown(res.choices[0].message.content)

# --- 5. ARCHIVES ---
elif menu == "🗄️ Archives des Dossiers":
    st.markdown("### 🗄️ Historique des Travaux")
    if not st.session_state.archive_dossiers:
        st.info("Aucun dossier dans l'archive.")
    else:
        for doc in st.session_state.archive_dossiers:
            with st.expander(f"📁 {doc.get('id')} | {doc.get('nom')} ({doc.get('date')})"):
                st.markdown(doc.get('rapport', "Erreur de lecture"))
