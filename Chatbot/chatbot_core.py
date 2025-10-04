import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean_text, rule_based_response, correct_spelling

def get_faq_response(user_query, model, df, question_embeddings, threshold=0.55):
    """
    Finds the most semantically similar FAQ answer.
    """
    user_query = clean_text(user_query)
    user_embedding = model.encode([user_query])
    similarities = cosine_similarity(user_embedding, question_embeddings)

    best_match_idx = np.argmax(similarities)
    best_score = similarities[0][best_match_idx]

    if best_score < threshold:
        return None
    return df.iloc[best_match_idx]['answer']


def chatbot_response(user_input, model, df, question_embeddings, threshold=0.55):
    """
    Combines spell-corrected, rule-based + ML semantic search logic.
    """
    # --- Spell Correction ---
    corrected_input = correct_spelling(user_input)

    # Rule-based response
    rule_reply = rule_based_response(corrected_input)
    if rule_reply:
        return rule_reply

    # FAQ semantic search response
    faq_reply = get_faq_response(corrected_input, model, df, question_embeddings, threshold)
    if faq_reply:
        return faq_reply

    # Default fallback
    return "Hmm 🤔 I’m not sure about that yet. Could you rephrase or ask something else?"


# Optional helper function if you want a single point to process messages
def process_user_message(msg, model, df, question_embeddings, threshold=0.55):
    """
    Corrects spelling and returns chatbot reply.
    """
    reply = chatbot_response(msg, model, df, question_embeddings, threshold)
    return reply
