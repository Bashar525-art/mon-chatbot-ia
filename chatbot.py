import streamlit as st
import streamlit.components.v1 as components

# 1. Configuration et Style CSS (Fixe le micro et la barre de saisie)
st.set_page_config(page_title="UltraBrain AI", layout="wide")

st.markdown("""
    <style>
    /* Fixe la zone de texte en bas */
    div[data-testid="stChatInputContainer"] {
        position: fixed;
        bottom: 30px;
        z-index: 1000;
    }
    
    /* Espace pour ne pas cacher les messages */
    .main .block-container {
        padding-bottom: 180px;
    }

    /* Style du bouton micro flottant en bas à droite */
    #mic-button-float {
        position: fixed;
        bottom: 100px;
        right: 50px;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
with st.sidebar:
    st.title("📁 Fichiers & Outils")
    st.file_uploader("Ajouter un PDF", type="pdf")
    st.file_uploader("Ajouter une Image", type=["jpg", "png", "jpeg"])
    st.divider()
    st.toggle("Recherche Internet", value=True)
    st.toggle("Lire les réponses", value=True)

# 3. Titre
st.title("🧠 UltraBrain AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages existants
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Le Composant Micro (JS optimisé pour éviter le chargement infini)
def mic_component():
    html_code = """
    <div id="mic-button-float">
        <button id="mic-btn" style="border:none; background:#ff4b4b; border-radius:50%; width:60px; height:60px; cursor:pointer; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);">
            <svg viewBox="0 0 24 24" width="30" height="30" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        </button>
    </div>
    <script>
        const btn = document.getElementById('mic-btn');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'fr-FR';

            btn.onclick = () => {
                btn.style.background = '#00ff00';
                recognition.start();
            };

            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                btn.style.background = '#ff4b4b';
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
            };
            
            recognition.onerror = () => { btn.style.background = '#ff4b4b'; };
            recognition.onend = () => { btn.style.background = '#ff4b4b'; };
        } else {
            btn.style.display = 'none';
            console.error("Navigateur non compatible");
        }
    </script>
    """
    return components.html(html_code, height=0)

# Appel du micro (il reste fixe grâce au CSS)
audio_result = mic_component()

# 5. Logique d'envoi
query = st.chat_input("Posez votre question...")

# Si on reçoit de l'audio, on l'utilise comme message
if audio_result and audio_result != "":
    # On vérifie si ce n'est pas le même que le dernier pour éviter les boucles
    if "last_audio" not in st.session_state or st.session_state.last_audio != audio_result:
        st.session_state.last_audio = audio_result
        query = audio_result

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # Réponse fictive
    with st.chat_message("assistant"):
        res = f"Je vous écoute ! Vous avez dit : {query}"
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
    
    st.rerun()
