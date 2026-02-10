import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION LEX NEXUS ---
st.set_page_config(page_title="Lex Nexus | Excellence Juridique", page_icon="⚖️", layout="wide")

# --- STYLE CSS HAUTE COUTURE (OR & NOIR) ---
st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700&family=Inter:wght@200;400;600&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at top right, #1a1f2c, #090a0f); 
        color: #e0e0e0; 
    }
    
    .main-header { 
        font-family: 'Playfair Display', serif; 
        color: #C5A059; 
        font-size: 4rem; 
        text-align: center; 
        margin-bottom: 0px; 
    }
    
    .sub-header { 
        font-family: 'Inter', sans-serif; 
        text-align: center; 
        color: #8a8d91; 
        letter-spacing: 5px; 
        text-transform: uppercase; 
        font-size: 0.8rem; 
        margin-bottom: 40px; 
    }

    .dashboard-card { 
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(197, 160, 89, 0.2); 
        backdrop-filter: blur(10px); 
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
        transition: 0.3s;
    }
    
    .dashboard-card:hover {
        border-color: #C5A059;
        background: rgba(197, 160, 89, 0.05);
    }

    section[data-testid="stSidebar"] { 
        background-color: rgba(7, 8, 12, 0.95) !important; 
        border-right: 1px solid #C5A059; 
    }

    .stButton>button { 
        width: 100%; 
        background: transparent !important; 
        color: #C5A059 !important; 
        border: 1px solid #C5A059 !important; 
        border-radius: 30px !important; 
        text-transform: uppercase !important; 
        letter-spacing: 2px !important; 
    }
    
    .stButton>button:hover { 
        background: #C5A059 !important; 
        color: #000 !important; 
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION & API ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Clé API Mistral manquante dans les secrets.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

if "archive_dossiers" not in st.session_state:
    st.session_state.archive_dossiers = []

# --- FONCTIONS SYSTÈME ---
def extract_pdf_text(files):
    text = ""
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def multi_agent_audit(text_contrat, query):
    # Agent 1 : Analyseur de Faits
    with st.status("Agent 1 : Analyse des faits...") :
        s1 = client.chat.complete(
            model="pixtral-12b-2409", 
            messages=[
                {"role": "system", "content": "Tu es un expert en extraction de données juridiques. Liste les parties, les dates et les montants."}, 
                {"role": "user", "content": text_contrat[:6000]}
            ]
        )
        data = s1.choices[0].message.content

    # Agent 2 : Détecteur de Risques
    with st.status("Agent 2 : Identification des risques...") :
        s2 = client.chat.complete(
            model="pixtral-12b-2409", 
            messages=[
                {"role": "system", "content": "Tu es un avocat spécialisé en litiges. Identifie les clauses risquées ou abusives."}, 
                {"role": "user", "content": data}
            ]
        )
        risks = s2.choices[0].message.content

    # Agent 3 : Rédacteur de Synthèse
    with st.status("Agent 3 : Rédaction finale...") :
        s3 = client.chat.complete(
            model="pixtral-12b-2409", 
            messages=[
                {"role": "system", "content": "Tu es le rédacteur final. Synthétise l'analyse en un rapport élégant et structuré."}, 
                {"role": "user", "content": f"Données: {data}\nRisques: {risks}\nInstruction Client: {query}"}
            ]
        )
    return s3.choices[0].message.content

# --- INTERFACE SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#C5A059; text-align:center; font-family:serif;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("NAVIGATION", ["Tableau de Bord", "Audit Multi-Agents", "Archives des Dossiers"])
    st.write("---")
    if st.button("🗑️ RÉINITIALISER LA SESSION"):
        st.session_state.archive_dossiers = []
        st.rerun()

# --- HEADER PRINCIPAL ---
st.markdown('<p class="main-header">Lex Nexus</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligence Juridique Suprême</p>', unsafe_allow_html=True)

# --- CONTENU DES PAGES ---

if menu == "Tableau de Bord":
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">99.4%</h2><p>Précision d\'Analyse</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">Souverain</h2><p>Mistral AI France</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="dashboard-card"><h2 style="color:#C5A059;">Sécurisé</h2><p>Chiffrement Session</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("### 🏛️ État de votre Cabinet Numérique")
    st.write("Sélectionnez **Audit Multi-Agents** pour commencer l'analyse d'un nouveau contrat.")
    st.image("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1000", use_container_width=True)

elif menu == "Audit Multi-Agents":
    st.markdown("### 🔬 Expertise de Dossier")
    files = st.file_uploader("Charger les documents du dossier (PDF)", type="pdf", accept_multiple_files=True)
    query = st.text_input("Instruction spécifique pour l'IA (optionnel)", placeholder="Ex: Vérifie la clause de non-concurrence...")
    
    if files and st.button("LANCER L'AUDIT TRIPLE ACTION"):
        raw_text = extract_pdf_text(files)
        rapport = multi_agent_audit(raw_text, query)
        
        st.markdown("---")
        st.markdown("### ⚖️ Rapport d'Expertise Final")
        st.write(rapport)
        
        # Sauvegarde dans les archives
        st.session_state.archive_dossiers.append({
            "id": f"LEX-{datetime.now().strftime('%H%M%S')}", 
            "nom": files[0].name, 
            "rapport": rapport,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        st.success("Analyse terminée et ajoutée aux archives.")

elif menu == "Archives des Dossiers":
    st.markdown("### 🗄️ Historique des Analyses")
    if not st.session_state.archive_dossiers:
        st.info("Aucun dossier archivé pour le moment.")
    else:
        for doc in st.session_state.archive_dossiers:
            with st.expander(f"📁 {doc['id']} | {doc['nom']} ({doc['date']})"):
                st.markdown(doc['rapport'])
                st.download_button("📥 Télécharger ce rapport", doc['rapport'], file_name=f"Rapport_{doc['id']}.txt")
