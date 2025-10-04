import re

# ============================
# Text Preprocessing
# ============================
def clean_text(text):
    """Cleans and normalizes text"""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ============================
# Rule-Based Responses
# ============================
def rule_based_response(user_input):
    greetings = ["hello", "hi", "hey", "namaste"]
    farewells = ["bye", "goodbye", "see you", "exit"]
    thanks = ["thank", "thanks", "thank you"]

    text = user_input.lower()

    if any(word in text for word in greetings):
        return "Hey there! 👋 How can I help you today?"
    elif any(word in text for word in thanks):
        return "You're most welcome! 😊"
    elif any(word in text for word in farewells):
        return "Goodbye! 👋 Hope to chat again soon!"
    else:
        return None
