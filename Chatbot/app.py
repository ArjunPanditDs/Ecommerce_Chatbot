import streamlit as st
from datetime import datetime
from utils import clean_text, greeting_response, business_response
from models import load_data, load_model_and_embeddings
from chatbot_core import chatbot_response
import traceback
import os

# ----------------------------
# --- App Setup ---
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "faq_with_intent.csv")

st.set_page_config(page_title="E-commerce Chatbot 🤖", layout="wide")

# ----------------------------
# --- Session State ---
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "model" not in st.session_state:
    st.session_state.model = None
if "df" not in st.session_state:
    st.session_state.df = None
if "question_embeddings" not in st.session_state:
    st.session_state.question_embeddings = None

# ----------------------------
# --- Load Model & Data ---
# ----------------------------
if not st.session_state.model_loaded:
    if not os.path.exists(file_path):
        st.error(f"❌ Data file not found at: {file_path}")
    else:
        st.info("⚙️ Loading model and FAQ embeddings... Please wait.")
        try:
            st.session_state.df = load_data(file_path)
            st.session_state.model, st.session_state.question_embeddings = load_model_and_embeddings(st.session_state.df)
            if st.session_state.model is None:
                raise ValueError("Model returned None")
            st.session_state.model_loaded = True
            st.success("✅ Model loaded successfully!")
        except Exception as e:
            st.session_state.model_loaded = False
            st.error(f"❌ Failed to load model or data: {e}")
            traceback.print_exc()

# ----------------------------
# --- Helper Functions ---
# ----------------------------
def get_time_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning! 🌅 How can I help you today?"
    elif 12 <= hour < 17:
        return "Good afternoon! 🌤 How can I help you today?"
    elif 17 <= hour < 22:
        return "Good evening! 🌙 What can I assist you with?"
    else:
        return "Hello there! 🌙 Burning the midnight oil, huh?"

def get_chatbot_reply(user_input):
    user_input_clean = clean_text(user_input)
    
    # Greeting or business rules first
    greet = greeting_response(user_input_clean)
    if greet:
        return greet

    biz = business_response(user_input_clean)
    if biz:
        return biz

    # ML reply only if model loaded
    if st.session_state.model_loaded and st.session_state.model:
        try:
            ml_reply = chatbot_response(
                user_input_clean,
                st.session_state.model,
                st.session_state.df,
                st.session_state.question_embeddings
            )
            if ml_reply:
                return ml_reply
        except Exception as e:
            st.error(f"⚠️ Error generating ML reply: {e}")
            traceback.print_exc()

    # Fallback
    return "⚠️ Chatbot ML model not available. Please ask general questions or try later."

# ----------------------------
# --- Chat UI Styling ---
# ----------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    font-family: 'Helvetica Neue', Arial, sans-serif;
}
.chat-box {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
}
.user-msg {
    text-align: right;
    margin-bottom: 10px;
}
.bot-msg {
    text-align: left;
    margin-bottom: 10px;
}
.msg-content {
    display: inline-block;
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
}
.user-msg .msg-content {
    background: linear-gradient(135deg, #00ff6a, #00c3ff);
    color: white;
}
.bot-msg .msg-content {
    background: rgba(255, 255, 255, 0.85);
    color: black;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 E-commerce FAQ Chatbot")

chat_container = st.container()

# Add first greeting if empty
if not st.session_state.messages:
    st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})

# ----------------------------
# --- Display Chat Messages ---
# ----------------------------
with chat_container:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["sender"] == "user":
            st.markdown(
                f"<div class='user-msg'><div class='msg-content'>{msg['text']}</div></div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='bot-msg'><div class='msg-content'>{msg['text']}</div></div>",
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# --- Input Form ---
# ----------------------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input_temp = st.text_input("Type your message here...", placeholder="Ask me about orders, warranty, etc.")
    submit_btn = st.form_submit_button("Send")

if submit_btn and user_input_temp.strip():
    # Add user message
    st.session_state.messages.append({"sender": "user", "text": user_input_temp})
    # Add bot reply
    reply = get_chatbot_reply(user_input_temp)
    st.session_state.messages.append({"sender": "bot", "text": reply})
    # Force rerun to refresh chat
    st.experimental_set_query_params(dummy=datetime.now())
