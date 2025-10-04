import pandas as pd
from sentence_transformers import SentenceTransformer

# ============================
# Load Dataset
# ============================
def load_data(path="data/faq_with_intent.csv"):
    df = pd.read_csv(path)
    return df

# ============================
# Load Model & Encode Questions
# ============================
def load_model_and_embeddings(df):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embeddings = model.encode(df['question'].tolist(), show_progress_bar=True)
    return model, question_embeddings


