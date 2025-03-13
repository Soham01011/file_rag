# vector_store.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the transformer model (adjust model name as needed)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Determine the embedding dimension (384 for all-MiniLM-L6-v2)
embedding_dim = 384

# Dictionary to hold a separate FAISS index for each user.
# Each user’s index will be an IndexIDMap that wraps a IndexFlatL2.
user_indexes = {}

def get_faiss_index_for_user(user_id: str):
    """
    Retrieve the FAISS index for a given user.
    If it doesn't exist, create a new one wrapped in an ID map.
    """
    if user_id not in user_indexes:
        # Create the base index and wrap it in an ID map for external IDs
        base_index = faiss.IndexFlatL2(embedding_dim)
        id_map = faiss.IndexIDMap(base_index)
        user_indexes[user_id] = id_map
    return user_indexes[user_id]

def embed_text(text: str) -> np.ndarray:
    """Generate an embedding for the given text."""
    embedding = model.encode(text)
    return np.array(embedding).astype('float32')

def add_text_to_user_index(user_id: str, text: str, ext_id: int):
    """
    Compute embedding for the text and add it to the user's FAISS index,
    using ext_id as the external identifier.
    Returns the embedding.
    """
    index = get_faiss_index_for_user(user_id)
    embedding = embed_text(text)
    # FAISS expects a 2D array for vectors and an array of IDs (int64)
    index.add_with_ids(np.expand_dims(embedding, axis=0), np.array([ext_id], dtype='int64'))
    return embedding

def search_user_index(user_id: str, query_embedding: np.ndarray, k: int=3):
    index = get_faiss_index_for_user(user_id)
    query_embedding = np.expand_dims(query_embedding, axis=0).astype('float32')
    distance, indices = index.search(query_embedding, k)
    return indices[0].tolist()
