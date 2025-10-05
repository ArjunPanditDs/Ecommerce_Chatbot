import streamlit as st
from datetime import datetime
from utils import clean_text, greeting_response, business_response
from models import load_data, load_model_and_embeddings
from chatbot_core import chatbot_response
import pandas as pd
import traceback
import os

# --- Paths & Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "faq_with_intent.csv")

st.set_page_config(page_title="E-commerce Chatbot 🤖", layout="wide")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

# --- Load Model ---
if not st.session_state.model_loaded:
    st.info("⚙️ Loading model and FAQ embeddings... Please wait.")
    try:
        df = load_data(file_path)
        model, question_embeddings = load_model_and_embeddings(df)
        st.session_state.model_loaded = True
        st.success("✅ Model loaded successfully!")
    except Exception as e:
        st.error("❌ Failed to load model or data!")
        traceback.print_exc()
        df, model, question_embeddings = None, None, None

# --- Helper Functions ---
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
    if not st.session_state.model_loaded:
        return "⚠️ Chatbot model failed to load. Please try again later."
    
    user_input = clean_text(user_input)
    greet = greeting_response(user_input)
    if greet:
        return greet

    biz = business_response(user_input)
    if biz:
        return biz

    ml_reply = chatbot_response(user_input, model, df, question_embeddings)
    if ml_reply:
        return ml_reply

    return "Hmm 🤔 I’m not sure about that. Could you rephrase it?"

# --- UI Styling ---
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
    height: 70vh;
    overflow-y: auto;
}
.user-msg { text-align: right; margin-bottom:10px; }
.bot-msg { text-align: left; margin-bottom:10px; }
.msg-content {
    display: inline-block;
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 70%;
}
.user-msg .msg-content { background: linear-gradient(135deg, #00ff6a, #00c3ff); color:white; }
.bot-msg .msg-content { background: rgba(255,255,255,0.85); color:black; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 E-commerce FAQ Chatbot")

chat_container = st.container()

# --- First greeting ---
if not st.session_state.messages:
    st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})

# --- Display chat messages ---
with chat_container:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["sender"] == "user":
            st.markdown(
                f"<div class='user-msg'><div class='msg-content'>{msg['text']}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='bot-msg'><div class='msg-content'>{msg['text']}</div></div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Input form ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...")
    submit_btn = st.form_submit_button("Send")

if submit_btn and user_input.strip():
    st.session_state.messages.append({"sender": "user", "text": user_input})
    reply = get_chatbot_reply(user_input)
    st.session_state.messages.append({"sender": "bot", "text": reply})
