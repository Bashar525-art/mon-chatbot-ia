import streamlit as st
import os
from datetime import datetime
from mistralai import Mistral
from pypdf import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="Lex Nexus | Intelligence Suprême", page_icon="⚖️", layout="wide")

# (Garder le CSS précédent ici...)

# --- SIMULATION BASE DE DONNÉES (Étape 2) ---
if "archive_dossiers" not in st.session_state:
    st.session_state.archive_dossiers = [
        {"id": "DS-2026-001", "nom": "Contrat Bail - ImmoProp", "date": "05/02/2026", "statut": "Analysé"},
        {"id": "DS-2026-002", "nom": "Cession Parts - Projet Alpha", "date": "09/02/2026", "statut": "En attente"}
    ]

# --- MOTEUR MULTI-AGENTS (Étape 3) ---
def multi_agent_audit(text_contrat, query):
    client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])
    
    # 1. Agent Analyseur
    with st.status("Agent 1 : Extraction des clauses clés..."):
        step1 = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[{"role": "system", "content": "Extrais uniquement les faits : dates, montants, parties et obligations."},
                      {"role": "user", "content": text_contrat[:5000]}]
        )
        data_brute = step1.choices[0].message.content

    # 2. Agent Critique (Risques)
    with st.status("Agent 2 : Identification des risques juridiques..."):
        step2 = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[{"role": "system", "content": "Tu es un avocat spécialisé en litiges. Trouve les pièges dans ces données."},
                      {"role": "user", "content": data_brute}]
        )
        risques = step2.choices[0].message.content

    # 3. Agent Rédacteur (Synthèse Finale)
    with st.status("Agent 3 : Rédaction du rapport final..."):
        final = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[{"role": "system", "content": "Synthétise le travail de tes collègues en un rapport de luxe pour un client exigeant."},
                      {"role": "user", "content": f"Données: {data_brute}\nRisques: {risques}\nQuestion client: {query}"}]
        )
    return final.choices[0].message.content

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#C5A059; text-align:center;'>LEX NEXUS</h1>", unsafe_allow_width=True)
    menu = st.radio("NAVIGATION", ["📜 Mes Dossiers (Archive)", "🔬 Audit Multi-Agents", "🛡️ Sécurité"])

if menu == "📜 Mes Dossiers (Archive)":
    st.markdown("### 🗄️ Bibliothèque des Dossiers Sauvegardés")
    st.write("Retrouvez ici vos analyses précédentes.")
    
    for d in st.session_state.archive_dossiers:
        with st.expander(f"📁 {d['id']} | {d['nom']}"):
            st.write(f"**Date d'analyse :** {d['date']}")
            st.write(f"**Statut :** {d['statut']}")
            st.button("Ouvrir l'archive", key=d['id'])

elif menu == "🔬 Audit Multi-Agents":
    st.markdown("### 🤖 Système Expert Multi-Agents")
    st.info("Ce mode utilise trois instances d'IA spécialisées pour une analyse croisée sans erreur.")
    
    file = st.file_uploader("Déposer le contrat pour audit profond", type="pdf")
    instr = st.text_input("Instruction spécifique (ex: Focus sur la clause de non-concurrence)")
    
    if file and st.button("LANCER L'AUDIT TRIPLE ACTION"):
        reader = PdfReader(file)
        text = "".join([p.extract_text() for p in reader.pages])
        
        rapport = multi_agent_audit(text, instr)
        st.markdown("---")
        st.markdown("#### ⚖️ RAPPORT D'EXPERTISE FINAL")
        st.write(rapport)
        
        # Sauvegarde automatique dans l'archive
        new_doc = {"id": f"DS-2026-00{len(st.session_state.archive_dossiers)+1}", "nom": file.name, "date": "10/02/2026", "statut": "Analysé"}
        st.session_state.archive_dossiers.append(new_doc)
        st.success("Rapport archivé avec succès.")
