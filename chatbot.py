import streamlit as st
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="UltraBrain AI", layout="wide")

# CSS pour fixer le micro et la barre de texte en bas
st.markdown("""
    <style>
    /* Fixe la barre d'entrée texte */
    div[data-testid="stChatInputContainer"] {
        position: fixed;
        bottom: 30px;
        z-index: 1000;
        background-color: #0e1117;
    }
    
    /* Espace en bas pour éviter que les messages soient cachés */
    .main .block-container {
        padding-bottom: 180px;
    }

    /* Bouton micro flottant */
    #mic-float {
        position: fixed;
        bottom: 100px;
        right: 50px;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# Barre latérale
with st.sidebar:
    st.title("📁 Fichiers & Outils")
    st.file_uploader("Ajouter un PDF", type="pdf")
    st.file_uploader("Ajouter une Image", type=["jpg", "png", "jpeg"])
    st.divider()
    st.toggle("Recherche Internet", value=True)
    st.toggle("Lire les réponses", value=True)

st.title("🧠 UltraBrain AI")

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Composant Micro JS
def mic_ui():
    js_code = """
    <div id="mic-float">
        <button id="btn-m" style="border:none; background:#ff4b4b; border-radius:50%; width:60px; height:60px; cursor:pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <svg viewBox="0 0 24 24" width="30" height="30" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        </button>
    </div>
    <script>
        const btn = document.getElementById('btn-m');
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'fr-FR';
        btn.onclick = () => { btn.style.background = '#00ff00'; recognition.start(); };
        recognition.onresult = (e) => {
            const t = e.results[0][0].transcript;
            btn.style.background = '#ff4b4b';
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
        };
        recognition.onend = () => { btn.style.background = '#ff4b4b'; };
    </script>
    """
    return components.html(js_code, height=0)

# Récupération de l'audio
audio_val = mic_ui()

# Entrée texte
user_input = st.chat_input("Écris ton message ici...")

# Si on a de l'audio ou du texte
prompt = None
if audio_val:
    prompt = audio_val
elif user_input:
    prompt = user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Réponse IA (Exemple)
    with st.chat_message("assistant"):
        response = f"J'ai bien reçu : {prompt}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
