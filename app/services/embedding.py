import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

embedding_dim = 384

# Directory to store FAISS indexes
INDEX_DIR = "faiss_indexes"
os.makedirs(INDEX_DIR, exist_ok=True)  # Ensure the directory exists

# Dictionary to store user-specific FAISS indexes in memory
user_indexes = {}

def get_faiss_index_for_user(user_id: str):
    """
    Retrieve the FAISS index for a given user.
    If it doesn't exist, load it from disk or create a new one.
    """
    if user_id not in user_indexes:
        index_path = f"{INDEX_DIR}/{user_id}.index"

        if os.path.exists(index_path):
            user_indexes[user_id] = faiss.read_index(index_path)
            print(f"✅ Loaded FAISS index from disk for user: {user_id}")
        else:
            base_index = faiss.IndexFlatL2(embedding_dim)
            id_map = faiss.IndexIDMap(base_index)  # Wrap in an ID map
            user_indexes[user_id] = id_map
            print(f"🆕 Created new FAISS index for user: {user_id}")

    return user_indexes[user_id]

def save_faiss_index(user_id: str):
    """Save the FAISS index for a user to disk."""
    index = user_indexes.get(user_id)
    if index:
        index_path = f"{INDEX_DIR}/{user_id}.index"
        faiss.write_index(index, index_path)
        print(f"💾 Saved FAISS index for user: {user_id}")

def embed_text(text: str) -> np.ndarray:
    """Generate an embedding for the given text."""
    if not isinstance(text, str):
        raise ValueError("Expected a string input for embedding")
    
    embedding = model.encode([text])  # Ensure input is a list
    return np.array(embedding[0]).astype('float32')  # Extract the first result


def add_text_to_user_index(user_id: str, text: str, ext_id: int):
    """
    Compute embedding for the text and add it to the user's FAISS index.
    Uses ext_id as the external identifier. Then, saves the index.
    """
    index = get_faiss_index_for_user(user_id)
    embedding = embed_text(text)
    
    # FAISS expects a 2D array for vectors and an array of IDs (int64)
    index.add_with_ids(np.expand_dims(embedding, axis=0), np.array([ext_id], dtype='int64'))

    save_faiss_index(user_id)  # Save index after modification
    return embedding

def search_user_index(user_id: str, query_text: str, k: int = 3):
    """
    Search the user's FAISS index for the k most similar embeddings.
    Returns a list of matching ext_ids.
    """
    index = get_faiss_index_for_user(user_id)
    
    # Compute query embedding
    query_embedding = embed_text(query_text)
    query_embedding = np.expand_dims(query_embedding, axis=0).astype('float32')
    
    # Perform the FAISS search
    distances, indices = index.search(query_embedding, k)
    
    return indices[0].tolist()  # Return list of matching ext_ids

