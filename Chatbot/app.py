import streamlit as st
from datetime import datetime
from utils import clean_text, greeting_response, business_response
from models import load_data, load_model_and_embeddings
from chatbot_core import chatbot_response
import pandas as pd
import traceback
import os

# --- Load Model & Data ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "faq_with_intent.csv")

st.set_page_config(page_title="E-commerce Chatbot 🤖", layout="centered")

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
    max-width: 80%;
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

# --- Initialize Chatbot ---
st.info("⚙️ Loading model and FAQ embeddings... Please wait.")
try:
    df = load_data(file_path)
    model, question_embeddings = load_model_and_embeddings(df)
    st.success("✅ Model loaded successfully!")
except Exception as e:
    st.error("❌ Failed to load model or data!")
    traceback.print_exc()
    df, model, question_embeddings = None, None, None

# --- Session State for chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    if not model or df is None:
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

# --- Chat Interface ---
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

# Display existing messages
for msg in st.session_state.messages:
    if msg["sender"] == "user":
        st.markdown(f"<div class='user-msg'><div class='msg-content'>{msg['text']}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'><div class='msg-content'>{msg['text']}</div></div>", unsafe_allow_html=True)

# Input box
user_input = st.text_input("Type your message here...", key="input_box")

if st.button("Send") and user_input.strip():
    # Add user message
    st.session_state.messages.append({"sender": "user", "text": user_input})
    
    # Bot reply
    reply = get_chatbot_reply(user_input)
    st.session_state.messages.append({"sender": "bot", "text": reply})
    
    # Rerun to display updated messages
    st.experimental_rerun()

# First greeting if chat is empty
if not st.session_state.messages:
    greeting = get_time_greeting()
    st.session_state.messages.append({"sender": "bot", "text": greeting})
    st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)
