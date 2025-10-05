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

st.set_page_config(
    page_title="E-commerce Chatbot 🤖", 
    layout="centered"
)

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
if "last_input" not in st.session_state:
    st.session_state.last_input = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ----------------------------
# --- Load Model & Data ---
# ----------------------------
if not st.session_state.model_loaded:
    with st.spinner("⚙️ Loading model and FAQ embeddings... Please wait."):
        try:
            st.session_state.df = load_data(file_path)
            st.session_state.model, st.session_state.question_embeddings = load_model_and_embeddings(st.session_state.df)
            st.session_state.model_loaded = True
            st.success("✅ Model loaded successfully!")
        except Exception as e:
            st.error("❌ Failed to load model or data! Chatbot will only answer greetings or fallback responses.")
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
    if not st.session_state.model_loaded or st.session_state.model is None:
        user_input_clean = clean_text(user_input)
        greet = greeting_response(user_input_clean)
        if greet:
            return greet
        biz = business_response(user_input_clean)
        if biz:
            return biz
        return "⚠️ Chatbot model failed to load. Please try again later."

    user_input_clean = clean_text(user_input)
    greet = greeting_response(user_input_clean)
    if greet:
        return greet
    biz = business_response(user_input_clean)
    if biz:
        return biz

    ml_reply = chatbot_response(
        user_input_clean,
        st.session_state.model,
        st.session_state.df,
        st.session_state.question_embeddings
    )
    if ml_reply:
        return ml_reply

    return "Hmm 🤔 I'm not sure about that. Could you rephrase it?"

# ----------------------------
# --- Pure Streamlit UI ---
# ----------------------------

# Header
st.title("🤖 E-commerce Assistant")
st.caption("Always here to help you! 💫")

# Add first greeting if no messages
if not st.session_state.messages:
    st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})

# Chat container with auto-height (Streamlit handles scrolling)
chat_container = st.container()

with chat_container:
    # Display all messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["sender"] == "user":
            # User message - using Streamlit's native styling
            with st.chat_message("user"):
                st.write(msg['text'])
                st.caption(f"Sent at {datetime.now().strftime('%H:%M')}")
        else:
            # Bot message - using Streamlit's native styling
            with st.chat_message("assistant"):
                st.write(msg['text'])
                st.caption(f"Sent at {datetime.now().strftime('%H:%M')}")

# Quick replies
st.subheader("💡 Quick Questions")

quick_cols = st.columns(5)
quick_replies = ["Returns", "Shipping", "Discounts", "Payments", "Tracking"]

for i, reply in enumerate(quick_replies):
    with quick_cols[i]:
        if st.button(reply, key=f"quick_{i}", use_container_width=True):
            st.session_state.messages.append({"sender": "user", "text": reply})
            bot_reply = get_chatbot_reply(reply)
            st.session_state.messages.append({"sender": "bot", "text": bot_reply})
            st.session_state.input_key += 1
            st.rerun()

# Input section - Using Streamlit's chat input (supports Enter key)
user_input = st.chat_input("💬 Type your message here...")

if user_input:
    if user_input.strip() and st.session_state.last_input != user_input.strip():
        st.session_state.last_input = user_input.strip()
        st.session_state.messages.append({"sender": "user", "text": user_input.strip()})
        reply = get_chatbot_reply(user_input.strip())
        st.session_state.messages.append({"sender": "bot", "text": reply})
        st.session_state.input_key += 1
        st.rerun()

# Add some space at bottom
st.write("")
st.write("")