import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="UltraBrain AI", layout="wide")

# CSS pour fixer le micro en bas
st.markdown("""
    <style>
    .stChatInputContainer { position: fixed; bottom: 30px; }
    .main .block-container { padding-bottom: 150px; }
    #mic-btn-container { position: fixed; bottom: 100px; right: 50px; z-index: 999; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 UltraBrain AI")

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage du chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Micro Fixe (Bouton simple)
def mic_simple():
    html_code = """
    <div id="mic-btn-container">
        <button id="m-btn" style="background:red; border:none; border-radius:50%; width:50px; height:50px; cursor:pointer; color:white; font-weight:bold;">🎤</button>
    </div>
    <script>
        const btn = document.getElementById('m-btn');
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'fr-FR';
        btn.onclick = () => { recognition.start(); btn.style.background = 'green'; };
        recognition.onresult = (e) => {
            const t = e.results[0][0].transcript;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
        };
    </script>
    """
    return components.html(html_code, height=0)

audio_text = mic_simple()
user_text = st.chat_input("Écris ici...")

# Logique d'envoi
final_msg = audio_text if audio_text else user_text

if final_msg:
    st.session_state.messages.append({"role": "user", "content": final_msg})
    st.rerun()
