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

st.set_page_config(page_title="E-commerce Chatbot 🤖", layout="wide")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Load Model ---
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
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

# --- Chat UI ---
st.title("🤖 E-commerce FAQ Chatbot")

chat_container = st.container()

# Add first greeting if empty
if not st.session_state.messages:
    st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})

with chat_container:
    for msg in st.session_state.messages:
        if msg["sender"] == "user":
            st.markdown(
                f"<div style='text-align:right; margin-bottom:10px;'>"
                f"<span style='background: linear-gradient(135deg, #00ff6a, #00c3ff); "
                f"color:white; padding:10px 15px; border-radius:15px; max-width:70%; display:inline-block;'>{msg['text']}</span>"
                f"</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='text-align:left; margin-bottom:10px;'>"
                f"<span style='background: rgba(255,255,255,0.85); "
                f"color:black; padding:10px 15px; border-radius:15px; max-width:70%; display:inline-block;'>{msg['text']}</span>"
                f"</div>", unsafe_allow_html=True)

# Input box
user_input = st.text_input("Type your message here...", key="input_box")

if user_input:
    # Add user message
    st.session_state.messages.append({"sender": "user", "text": user_input})
    
    # Add bot reply
    reply = get_chatbot_reply(user_input)
    st.session_state.messages.append({"sender": "bot", "text": reply})
    
    # Clear input box
    st.session_state.input_box = ""
    
    # Rerun the script naturally (Streamlit auto reruns on input)
    st.experimental_set_query_params(dummy=datetime.now())  # Forces update without experimental_rerun
