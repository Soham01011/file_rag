# vector_store.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the transformer model (adjust model name as needed)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Determine the embedding dimension (384 for all-MiniLM-L6-v2)
embedding_dim = 384

# Dictionary to hold a separate FAISS index for each user.
user_indexes = {}

def get_faiss_index_for_user(user_id: str):
    """
    Retrieve the FAISS index for a given user.
    If it doesn't exist, create a new one.
    """
    if user_id not in user_indexes:
        user_indexes[user_id] = faiss.IndexFlatL2(embedding_dim)
    return user_indexes[user_id]

def embed_text(text: str) -> np.ndarray:
    """Generate an embedding for the given text."""
    embedding = model.encode(text)
    return np.array(embedding).astype('float32')

def add_text_to_user_index(user_id: str, text: str):
    """
    Compute embedding for the text and add it to the user's FAISS index.
    Returns the embedding.
    """
    index = get_faiss_index_for_user(user_id)
    embedding = embed_text(text)
    # FAISS expects a 2D array: [ [embedding values...] ]
    index.add(np.expand_dims(embedding, axis=0))
    return embedding