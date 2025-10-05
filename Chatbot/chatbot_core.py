import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean_text, rule_based_response, correct_spelling, business_response

def get_faq_response(user_query, model, df, question_embeddings, threshold=0.3):
    """
    Finds the most semantically similar FAQ answer.
    """
    user_query = clean_text(user_query)
    user_embedding = model.encode([user_query])
    similarities = cosine_similarity(user_embedding, question_embeddings)

    best_match_idx = np.argmax(similarities)
    best_score = similarities[0][best_match_idx]

    # Check available columns in dataframe
    print(f"Debug - Available columns: {df.columns.tolist()}")
    print(f"Debug - Best similarity score: {best_score}, Threshold: {threshold}")
    
    # Use correct column names (lowercase)
    if 'question' in df.columns:
        print(f"Debug - Matched question: {df.iloc[best_match_idx]['question']}")
    elif 'Question' in df.columns:
        print(f"Debug - Matched question: {df.iloc[best_match_idx]['Question']}")
    else:
        print("Debug - No 'question' column found")

    if best_score < threshold:
        return None
    
    # Use correct column name for answer
    if 'answer' in df.columns:
        return df.iloc[best_match_idx]['answer']
    elif 'Answer' in df.columns:
        return df.iloc[best_match_idx]['Answer']
    else:
        return None

def chatbot_response(user_input, model, df, question_embeddings, threshold=0.3):
    """
    Combines spell-corrected, rule-based + ML semantic search logic.
    """
    # SPELLING CORRECTION CALL KARO - yeh line change karo
    corrected_input = correct_spelling(user_input)  # Ye use karo
    # corrected_input = user_input  # Ye comment karo ya hatao
    
    print(f"Debug - Original input: {user_input}")
    print(f"Debug - Corrected input: {corrected_input}")

    # Pehle rule-based response check karo
    rule_reply = rule_based_response(corrected_input)
    if rule_reply:
        print("Debug - Rule-based response used")
        return rule_reply

    # Fir business response check karo
    biz_reply = business_response(corrected_input)
    if biz_reply:
        print("Debug - Business response used")
        return biz_reply

    # FAQ semantic search response
    faq_reply = get_faq_response(corrected_input, model, df, question_embeddings, threshold)
    if faq_reply:
        print("Debug - FAQ response used")
        return faq_reply

    # Default fallback
    return "Hmm 🤔 I'm not sure about that yet. Could you rephrase or ask something else?"

def process_user_message(msg, model, df, question_embeddings, threshold=0.3):
    """
    Corrects spelling and returns chatbot reply.
    """
    reply = chatbot_response(msg, model, df, question_embeddings, threshold)
    return reply