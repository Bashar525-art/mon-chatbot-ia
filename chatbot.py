import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from mistralai import Mistral
from docx import Document
from pypdf import PdfReader
from io import BytesIO
import base64

# --- 1. CONFIGURATION, ENGINE & STYLE PRESTIGE ---
st.set_page_config(page_title="Lex Nexus OS | Vision 2026", page_icon="⚖️", layout="wide")
CURRENT_DATE_2026 = "28 Février 2026"

# STYLE CSS AVANCÉ POUR LA BARRE D'OUTILS ET L'INTERFACE
st.markdown("""
<style>
    /* Style global */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    
    /* Design de la barre d'outils style Gemini/ChatGPT */
    [data-testid="stChatInput"] {
        background-color: #1A1D24 !important;
        border-radius: 20px !important;
        padding-left: 20px !important;
        margin-top: -20px !important; /* Pour compenser la barre d'outils au-dessus */
    }

    /* Conteneur pour la barre d'outils au-dessus du chat input */
    .chat-tools-bar {
        background-color: #1A1D24;
        border-radius: 15px 15px 0 0;
        padding: 10px 15px;
        margin-bottom: 0px;
        display: flex;
        align-items: center;
        width: calc(100% - 2rem); /* Pour l'aligner avec l'input */
        max-width: 1000px; /* Exemple de largeur max pour la centrer */
        margin-left: auto; margin-right: auto; /* Centrage */
        border: 1px solid rgba(212, 175, 55, 0.2);
    }
    
    .tool-icon {
        color: #8a8d91;
        font-size: 1.2rem;
        margin-right: 15px;
        cursor: pointer;
        transition: 0.3s;
    }
    
    .tool-icon:hover { color: #D4AF37; }
    
    .tool-submit {
        margin-left: auto;
        color: #D4AF37;
        font-weight: bold;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "temp_text_input" not in st.session_state: st.session_state.temp_text_input = ""

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- 2. FONCTIONS DE TRAITEMENT ---

def process_file(file):
    name = file.name.lower()
    try:
        if name.endswith(".pdf"):
            return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
        elif name.endswith(".docx"):
            return "\n".join([p.text for p in Document(file).paragraphs])
        elif name.endswith((".png", ".jpg", ".jpeg")):
            return base64.b64encode(file.read()).decode('utf-8')
    except: return f"Erreur de lecture sur {file.name}"
    return ""

def generate_redline(content):
    # Simulation de Redline (Axe 4)
    if "Responsabilité nulle" in content:
        return ("Responsabilité illimitée.", "Plafonnement à 150% du montant du contrat.")
    return (None, None)

# --- 3. INTERFACE ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS 2026</h1>", unsafe_allow_html=True)
    st.info(f"📅 Date : {CURRENT_DATE_2026}")
    mode = st.selectbox("MODULE", ["📊 Cockpit", "🔬 Audit Vision & Texte"])
    st.divider()
    if st.button("🔌 Reset System"):
        st.session_state.clear()
        st.rerun()

if mode == "📊 Cockpit":
    st.title("Tableau de Bord Stratégique")
    c1, c2, c3 = st.columns(3)
    c1.metric("Santé Juridique", "88%", "+5%")
    c2.metric("Analyse Vision", "Activée", "LIVE")
    c3.metric("Dossiers Audités", len(st.session_state.chat_history)//2)
    
    # Graphique Radar
    df_radar = pd.DataFrame({
        "Critère": ["Conformité", "Risque Contractuel", "Propriété Intellectuelle"],
        "Score": [90, 60, 85]
    })
    fig_radar = px.line_polar(df_radar, r='Score', theta='Critère', line_close=True)
    fig_radar.update_traces(fill='toself', line_color='#D4AF37')
    fig_radar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_radar, use_container_width=True)

elif mode == "🔬 Audit Vision & Texte":
    st.header("Analyse Multisensorielle")
    
    # Affichage Chat
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # --- BARRE D'OUTILS STYLÉE STYLE GEMINI/ChatGPT ---
    st.markdown("""
        <div class="chat-tools-bar">
            <i class="fa fa-image tool-icon" title="Ajouter une photo"></i>
            <i class="fa fa-paperclip tool-icon" title="Joindre un fichier"></i>
            <div class="tool-submit">✉️</div>
        </div>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    """, unsafe_allow_html=True)

    # Zone de téléchargement (utilisée par la barre d'outils)
    # L'uploader est là, mais caché visuellement (car stylé par la barre d'outils ci-dessus)
    files = st.file_uploader(
        "Déposez vos pièces", 
        type=["pdf", "docx", "png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        label_visibility="collapsed" # Caché par défaut pour un look épuré
    )
    
    # Entrée Chat Standard
    # On la positionne après l'uploader pour qu'elle semble "liée" à la barre d'outils
    if prompt := st.chat_input("Analysez ces pièces ou rédigez un acte..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # Construction du contexte (Texte + Images)
            content_list = [{"type": "text", "text": prompt}]
            
            if files:
                for f in files:
                    processed = process_file(f)
                    if f.name.lower().endswith((".png", ".jpg", ".jpeg")):
                        # C'est une image : IA Vision
                        content_list.append({
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{processed}"
                        })
                    else:
                        # C'est du texte : PDF/DOCX
                        content_list[0]["text"] += f"\n\nCONTENU DU FICHIER {f.name}:\n{processed}"
            
            # IA Request
            response = client.chat.complete(
                model="pixtral-12b-2409", 
                messages=[
                    {"role": "system", "content": f"Tu es Lex Nexus. Nous sommes le {CURRENT_DATE_2026}. Tu peux analyser du texte et des images."},
                    {"role": "user", "content": content_list}
                ]
            )
            txt = response.choices[0].message.content
            st.write(txt)
            st.session_state.chat_history.append({"role": "assistant", "content": txt})
            st.rerun()
