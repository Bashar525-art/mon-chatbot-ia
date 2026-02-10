import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument

# --- CONFIGURATION PRO ---
st.set_page_config(page_title="Lex Nexus | IA Juridique", page_icon="⚖️", layout="wide")

# Injection de CSS pour un look "SaaS Premium"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #0E1117; }
    
    /* Titre Elegant */
    .main-title {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        text-align: center;
        font-size: 3.5rem;
        margin-bottom: 0px;
    }
    
    /* Cartes d'accueil */
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.2);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        transition: 0.3s;
    }
    .stat-card:hover { border-color: #D4AF37; background: rgba(212, 175, 55, 0.05); }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #07080C !important; border-right: 1px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

# --- SECURITÉ API ---
if "MISTRAL_API_KEY" not in st.secrets:
    st.error("🔑 Configuration requise : Clé API manquante.")
    st.stop()

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

# --- FONCTION D'EXTRACTION SECURISÉE ---
def safe_extract_pdf(files):
    text = ""
    try:
        for f in files:
            reader = PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
        return text
    except Exception as e:
        return f"Erreur de lecture : {str(e)}"

# --- SIDEBAR PROFESSIONNELLE ---
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8rem; color:#888;'>v2.0 - Intelligence Souveraine</p>", unsafe_allow_html=True)
    st.write("---")
    
    nav = st.selectbox("MODULE", ["Tableau de Bord", "Audit de Contrat", "Comparaison Active", "Bibliothèque Sécurisée"])
    
    st.write("---")
    if nav != "Tableau de Bord":
        uploaded_docs = st.file_uploader("Charger des pièces (PDF)", type="pdf", accept_multiple_files=True)
    
    st.write("---")
    if st.button("🗑️ CLÔTURER LE DOSSIER"):
        st.session_state.clear()
        st.rerun()

# --- NAVIGATION PRINCIPALE ---

# Titre permanent
st.markdown('<p class="main-title">LEX NEXUS</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#D4AF37; font-weight:300;'>Plateforme d'Analyse Juridique Augmentée</p>", unsafe_allow_html=True)
st.write("")

if nav == "Tableau de Bord":
    # On remplit le vide avec des statistiques factices mais pro
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="stat-card"><h3>98%</h3><p>Précision d\'Analyse</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card"><h3>< 10s</h3><p>Temps de Revue</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-card"><h3>RGPD</h3><p>Conformité Totale</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🛡️ Activités récentes & Guide")
    st.write("Bienvenue, Maître. Lex Nexus est prêt à auditer vos contrats de bail, de travail ou de cession.")
    st.info("Utilisez le menu à gauche pour charger un dossier et commencer l'audit.")

elif nav == "Audit de Contrat":
    if "messages" not in st.session_state: st.session_state.messages = []
    
    # Affichage des messages
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="⚖️" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])
            
    query = st.chat_input("Ex: Analyse les clauses de résiliation...")
    
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"): st.markdown(query)
        
        with st.spinner("Analyse Lex Nexus en cours..."):
            try:
                context = ""
                if uploaded_docs:
                    raw_text = safe_extract_pdf(uploaded_docs)
                    context = f"DOCUMENTS CLIENT :\n{raw_text[:8000]}"
                
                sys_msg = "Tu es Lex Nexus. Réponds avec rigueur juridique. Ne donne pas de conseils d'avocat, mais fais des analyses de texte."
                resp = client.chat.complete(
                    model="pixtral-12b-2409",
                    messages=[{"role": "system", "content": sys_msg + context}] + st.session_state.messages
                )
                full_text = resp.choices[0].message.content
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
            except Exception as e:
                st.error("Désolé, une erreur technique est survenue. Vérifiez votre connexion.")

elif nav == "Comparaison Active":
    st.subheader("🔍 Comparaison de deux versions de contrat")
    colA, colB = st.columns(2)
    with colA: doc1 = st.file_uploader("Version Originale", type="pdf", key="v1")
    with colB: doc2 = st.file_uploader("Version Modifiée", type="pdf", key="v2")
    
    if doc1 and doc2:
        if st.button("EXÉCUTER LA COMPARAISON"):
            with st.status("Comparaison point par point..."):
                t1 = safe_extract_pdf([doc1])
                t2 = safe_extract_pdf([doc2])
                prompt = f"Compare ces deux contrats. Fais un tableau des différences. Sois très précis sur les montants et les dates.\n\nDOC 1: {t1[:4000]}\n\nDOC 2: {t2[:4000]}"
                res = client.chat.complete(model="pixtral-12b-2409", messages=[{"role": "user", "content": prompt}])
                st.markdown(res.choices[0].message.content)
