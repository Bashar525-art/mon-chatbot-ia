import streamlit as st
import streamlit.components.v1 as components

# 1. Configuration de la page
st.set_page_config(page_title="UltraBrain AI", layout="wide")

# 2. CSS Personnalisé pour fixer l'interface
st.markdown("""
    <style>
    /* Fixe la barre d'entrée de texte tout en bas */
    div[data-testid="stChatInputContainer"] {
        position: fixed;
        bottom: 20px;
        left: 0;
        right: 0;
        padding: 10px 5%;
        z-index: 1000;
        background: transparent;
    }

    /* Crée un espace en bas de la page pour que le dernier message ne soit pas caché */
    .main .block-container {
        padding-bottom: 200px;
    }

    /* Style du bouton micro flottant */
    #mic-container {
        position: fixed;
        bottom: 90px;
        right: 30px;
        z-index: 1001;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Fonction pour le Micro (JavaScript / Web Speech API)
def speech_recognition_widget():
    # Ce composant crée un bouton micro qui reste "devant toi"
    html_code = """
    <div id="mic-container">
        <button id="start-record" style="
            background-color: #ff4b4b;
            border: none;
            color: white;
            padding: 15px;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
        </button>
    </div>

    <script>
        const btn = document.getElementById('start-record');
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'fr-FR';
        recognition.continuous = false;

        btn.onclick = () => {
            btn.style.backgroundColor = '#00ff00'; // Devient vert pendant l'écoute
            recognition.start();
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            btn.style.backgroundColor = '#ff4b4b';
            // Envoi du texte reconnu à Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: transcript
            }, '*');
        };

        recognition.onerror = () => {
            btn.style.backgroundColor = '#ff4b4b';
        };
        
        recognition.onend = () => {
            btn.style.backgroundColor = '#ff4b4b';
        };
    </script>
    """
    # On place le composant dans l'app
    return components.html(html_code, height=0)

# 4. Barre latérale (Sidebar)
with st.sidebar:
    st.header("📁 Fichiers & Outils")
    st.file_uploader("Ajouter un PDF (Cours, Doc...)", type="pdf")
    st.file_uploader("Ajouter une Image", type=["jpg", "png", "jpeg"])
    st.markdown("---")
    st.toggle("🌍 Recherche Internet", value=True)
    st.toggle("🔊 Lire les réponses", value=True)

# 5. Titre principal
st.title("🔮 UltraBrain AI")
st.caption("Assistant polyvalent - Micro fixe activé")

# 6. Gestion de l'historique du chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Affichage du Micro fixe
# Le composant est invisible mais le JS place le bouton en bas à droite via le CSS
audio_input = speech_recognition_widget()

# 8. Logique d'entrée (Texte ou Audio)
user_input = st.chat_input("Écris ton message ici...")

# Priorité à l'audio si détecté
final_query = audio_input if audio_input else user_input

if final_query:
    # Message Utilisateur
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(final_query)

    # Réponse IA
    with st.chat_message("assistant"):
        response = f"J'ai bien reçu votre message : '{final_query}'. Comment puis-je vous aider ?"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rafraîchir pour vider le buffer audio
    st.rerun()
