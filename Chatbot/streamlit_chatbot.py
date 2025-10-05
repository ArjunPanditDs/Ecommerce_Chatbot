from flask import Flask, request, jsonify, render_template
from models import load_data, load_model_and_embeddings
from chatbot_core import chatbot_response
from utils import clean_text, greeting_response, business_response
from datetime import datetime
import traceback
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "faq_with_intent.csv")
# df = pd.read_csv(file_path)


app = Flask(__name__)

print("⚙️ Initializing Chatbot System...")
try:
    df = load_data(file_path)
    model, question_embeddings = load_model_and_embeddings(df)
    print("✅ Model and FAQ embeddings loaded successfully!")
except Exception as e:
    print("❌ Error while loading model/data:")
    traceback.print_exc()
    df, model, question_embeddings = None, None, None


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


@app.route("/")
def home():
    greeting = get_time_greeting()
    return render_template("index.html", greeting=greeting)


@app.route("/get", methods=["POST"])
def get_bot_response():
    try:
        user_msg = request.form.get("msg", "").strip()
        if not user_msg:
            return jsonify({"reply": "Please type something 😅"})
        bot_reply = get_chatbot_reply(user_msg)
        return jsonify({"reply": bot_reply})
    except Exception as e:
        print("⚠️ Error during chat response:", e)
        traceback.print_exc()
        return jsonify({"reply": "Oops! Something went wrong 😔"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=False, use_reloader=False)
