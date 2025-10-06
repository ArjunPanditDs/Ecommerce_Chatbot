import streamlit as st
from datetime import datetime
from utils import clean_text, greeting_response, business_response
from models import load_data, load_model_and_embeddings
from chatbot_core import chatbot_response
import traceback
import os
import database  # Database import

# ----------------------------
# --- App Setup ---
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "faq_with_intent.csv")

st.set_page_config(
    page_title="E-commerce Chatbot 🤖", 
    layout="centered"
)

# Hide sidebar and header elements
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    #stDecoration {display: none;}
</style>
""", unsafe_allow_html=True)

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

    try:
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
    
    except Exception as e:
        # Fallback to rule-based responses
        user_input_clean = clean_text(user_input)
        greet = greeting_response(user_input_clean)
        if greet:
            return greet
        biz = business_response(user_input_clean)
        if biz:
            return biz
        return "Hmm 🤔 I'm not sure about that. Could you rephrase it?"

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
if "session_id" not in st.session_state:
    # Generate unique session ID for database
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.now()))}"

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
            
            # Load previous chat history from database
            try:
                previous_messages = database.get_chat_history(st.session_state.session_id)
                if previous_messages:
                    st.session_state.messages = previous_messages
                else:
                    # Add first greeting if no previous messages
                    st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})
            except Exception as db_error:
                st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})
                
        except Exception as e:
            st.session_state.model_loaded = False
            st.error("❌ Failed to load model or data! Chatbot will only answer greetings or fallback responses.")
            if not st.session_state.messages:
                st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})

# ----------------------------
# --- Streamlit UI ---
# ----------------------------

# Clean Header - Only chatbot name
st.markdown("<h1 style='text-align: center;'>🤖 E-commerce Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Always here to help you! 💫</p>", unsafe_allow_html=True)

# Chat container
chat_container = st.container()

with chat_container:
    # Display all messages
    for msg in st.session_state.messages:
        if msg["sender"] == "user":
            with st.chat_message("user"):
                st.write(msg['text'])
                st.caption(f"Sent at {datetime.now().strftime('%H:%M')}")
        else:
            with st.chat_message("assistant"):
                st.write(msg['text'])
                st.caption(f"Sent at {datetime.now().strftime('%H:%M')}")

# Input section - Using Streamlit's chat input
user_input = st.chat_input("💬 Type your message here...")

if user_input:
    if user_input.strip() and st.session_state.last_input != user_input.strip():
        st.session_state.last_input = user_input.strip()
        
        # Add user message to chat
        st.session_state.messages.append({"sender": "user", "text": user_input.strip()})
        
        # Get bot reply
        reply = get_chatbot_reply(user_input.strip())
        st.session_state.messages.append({"sender": "bot", "text": reply})
        
        # Save to database (silently in background)
        try:
            database.save_chat(st.session_state.session_id, user_input.strip(), reply)
        except Exception as e:
            pass  # Silent fail - database saves in background
        
        st.rerun()

# Add some space at bottom
st.write("")
st.write("")