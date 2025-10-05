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

st.set_page_config(page_title="E-commerce Chatbot 🤖", layout="centered")

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
    st.info("⚙️ Loading model and FAQ embeddings... Please wait.")
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
    # Always handle empty model
    if not st.session_state.model_loaded or st.session_state.model is None:
        # Return only greetings and business rules
        user_input_clean = clean_text(user_input)
        greet = greeting_response(user_input_clean)
        if greet:
            return greet
        biz = business_response(user_input_clean)
        if biz:
            return biz
        return "⚠️ Chatbot model failed to load. Please try again later."
    
    # Model is loaded, normal behavior
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
    
    return "Hmm 🤔 I’m not sure about that. Could you rephrase it?"

# ----------------------------
# --- Chat UI (native components + light theming) ---
# ----------------------------

# Minimal, safe CSS: gradient page background and subtle content card
st.markdown(
    """
    <style>
      .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
      }
      .block-container {
        background: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.10));
        border-radius: 18px;
        padding: 2rem 2rem 1rem 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align:center; color:#ffffff;'>🤖 E-commerce Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#e6e6e6;'>Always here to help you! 💫</p>", unsafe_allow_html=True)

st.divider()

# Seed with greeting if empty
if not st.session_state.messages:
    st.session_state.messages.append({"sender": "bot", "text": get_time_greeting()})

# Render chat messages with Streamlit chat components
for msg in st.session_state.messages:
    if msg.get("sender") == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(msg.get("text", ""))
    else:
        with st.chat_message("assistant", avatar="🛍️"):
            st.write(msg.get("text", ""))

# Quick replies
st.write("**Quick questions:**")
quick_replies = ["Return policy", "Shipping", "Discounts", "Payments", "Track order"]
cols = st.columns(len(quick_replies))
for i, label in enumerate(quick_replies):
    if cols[i].button(label, use_container_width=True, key=f"quick_{i}"):
        st.session_state.messages.append({"sender": "user", "text": label})
        bot_text = get_chatbot_reply(label)
        st.session_state.messages.append({"sender": "bot", "text": bot_text})
        st.rerun()

st.divider()

# Enter-to-send with native chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"sender": "user", "text": prompt})
    response_text = get_chatbot_reply(prompt)
    st.session_state.messages.append({"sender": "bot", "text": response_text})
    st.rerun()
