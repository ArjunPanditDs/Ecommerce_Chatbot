import re
from spellchecker import SpellChecker

def clean_text(text):
    """
    Cleans input text: removes extra spaces, special chars, and lowercases it.
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def greeting_response(text):
    """
    Handles casual user greetings and emotions.
    """
    text = clean_text(text)

    if any(word in text for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "good night"]):  # good night add kiya
        return "Good day! 🌞 How can I help you today?"
    elif "how are you" in text:
        return "I'm doing great 😄 Thanks for asking! How about you?"
    elif any(word in text for word in ["what's up", "whatsup", "wassup"]):
        return "Just chilling in the digital realm ⚡ Waiting for your next question!"
    elif any(word in text for word in ["not good", "sad", "bad day"]):
        return "Oh no 😔 Want to talk about it? Or should I cheer you up with something fun?"
    else:
        return None

def rule_based_response(text):
    """
    Handles quick FAQ-like rule-based responses (delivery, warranty, etc.)
    """
    text = clean_text(text)
    # Exit / Goodbye intent
    if any(word in text for word in ["bye", "goodbye", "exit", "stop", "see you", "tata", "thank you"]):
        return "Goodbye! 👋 Hope to chat with you again soon."

    # --- Bot Introduction ---
    elif any(phrase in text for phrase in ["who are you", "what are you", "your name", "who made you","who created you","who makes you" "who is mohit", "about mohit"]):  # Add more variations
        return "I am a chatbot for e-commerce, created by Mr. Mohit and his team 'The Data Decoders' with the help of mr. Santosh sir (Sandy)🤖."
    
    elif any(phrase in text for phrase in ["warranty", "guarantee", "product warranty", "warranty claim"]):
        return (
            "Most products come with a standard manufacturer warranty 🧾.\n"
            "You can view warranty details on the product page or contact our support for warranty claims."
        )
    elif any(phrase in text for phrase in ["return", "refund", "replace", "replacement"]):
        return (
            "You can request a return or refund within 7 days of delivery 📦.\n"
            "Visit 'My Orders' → Select item → Choose 'Return/Refund'."
        )
    elif any(phrase in text for phrase in ["delivery", "shipping", "track order", "status", "tracking", "track"]):  # tracking add kiya
        return (
            "You can track your order via the 'Track Order' section 🚚.\n"
            "Delivery usually takes 3–5 business days."
        )
    elif any(phrase in text for phrase in ["payment", "transaction", "upi", "card", "failed payment"]):
        return (
            "We support multiple payment options — UPI, cards, and wallets 💳.\n"
            "If a payment failed, your amount will auto-refund in 3–5 days."
        )
    elif any(phrase in text for phrase in ["cancel order", "order cancel", "cancel my order"]):
        return (
            "You can cancel an order before it ships 🚫.\n"
            "Go to 'My Orders' → Select order → Tap 'Cancel'."
        )
        # --- Bot Introduction ---
    else:
        return None


def business_response(text):
    """
    Detailed rule-based responses for e-commerce topics.
    """
    text = clean_text(text)

    if any(phrase in text for phrase in ["refund policy", "return policy", "how to return", "initiate return"]):
        return (
            "Our Return & Refund Policy allows returns within 7–10 days 🧾.\n"
            "Go to 'My Orders' → select your item → click 'Return/Replace'."
        )
    elif any(phrase in text for phrase in ["delivery time", "track my order", "shipping charge", "order delayed"]):
        return (
            "You can track your order anytime from 'My Orders' 🚚.\n"
            "Delivery usually takes 3–5 business days depending on your location."
        )
    elif any(phrase in text for phrase in ["cancel my order", "order cancellation", "cancel request"]):
        return (
            "You can cancel your order before it’s shipped 📦.\n"
            "Go to 'My Orders' → select product → tap 'Cancel'."
        )
    elif any(phrase in text for phrase in ["replace", "exchange", "defective", "damaged", "wrong item"]):
        return (
            "Sorry about that 😔 You can request a replacement via 'My Orders' → 'Return/Replace'."
        )
    elif any(phrase in text for phrase in ["payment failed", "money not refunded", "transaction issue"]):
        return (
            "If your payment failed 💳, wait 2–3 business days for auto-refund. "
            "If delayed, contact your bank with the transaction ID."
        )
    elif any(phrase in text for phrase in ["discount", "offer", "coupon", "promo code", "sale"]):
        return (
            "🔥 You can find all offers in our 'Deals & Offers' section. "
            "Apply valid promo codes during checkout to save more!"
        )
    elif any(phrase in text for phrase in ["forgot password", "can't login", "login issue"]):
        return (
            "If you forgot your password 🔐, click 'Forgot Password' and reset it easily."
        )
    elif any(phrase in text for phrase in ["stock", "out of stock", "when available"]):
        return (
            "Enable 'Notify Me' on the product page 🛒 — we'll alert you once it's back in stock!"
        )
    elif any(phrase in text for phrase in ["change address", "edit order", "update address"]):
        return (
            "You can update shipping details before your order ships 🏠.\n"
            "Go to 'My Orders' → select order → 'Edit Address'."
        )
    elif any(phrase in text for phrase in ["contact", "help", "support", "complaint"]):
        return (
            "Our support team is available 24×7 📞. Reach us via Live Chat or the Help Center!"
        )
    elif any(phrase in text for phrase in ["product details", "specifications", "price of", "how much"]):
        return (
            "All product details, price, and specs are available on the product page 📋."
        )
    else:
        return None


spell = SpellChecker()

def correct_spelling(text):
    """
    Correct spelling of the input text using SpellChecker
    Returns the corrected text or original text if correction fails
    """
    try:
        # Check if text is valid
        if not text or not isinstance(text, str) or text.strip() == "":
            return text
            
        words = text.split()
        corrected_words = []
        
        for word in words:
            try:
                # Get corrected word
                corrected_word = spell.correction(word)
                
                # If correction returns None or empty, use original word
                if corrected_word is None or corrected_word == "":
                    corrected_words.append(word)
                else:
                    corrected_words.append(corrected_word)
                    
            except Exception as e:
                # If any error in correcting a word, use the original word
                corrected_words.append(word)
        
        # Join only if we have valid words
        if corrected_words:
            return " ".join(corrected_words)
        else:
            return text
            
    except Exception as e:
        print(f"Spelling correction error: {e}")
        # Return original text if any error occurs
        return text