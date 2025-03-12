import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from app.database.connection import chats_collection

# Load pre-trained LSTM model
lstm_model = tf.keras.models.load_model("app/models/lstm_model.h5")

# Tokenizer for converting text to sequences
tokenizer = Tokenizer(num_words=5000, oov_token="<OOV>")

async def get_lstm_response(username: str, user_message: str):
    """
    Uses an LSTM model to generate a response based on the last 10 user messages.
    """
    # Retrieve last 10 messages
    past_messages = await chats_collection.find({"username": username}).sort("timestamp", -1).limit(10).to_list(length=10)

    # Combine past messages into a list
    past_texts = [msg["user_message"] for msg in past_messages] + [user_message]

    # Convert text to sequences
    tokenizer.fit_on_texts(past_texts)
    sequences = tokenizer.texts_to_sequences(past_texts)

    # Pad sequences to match LSTM input size
    input_data = pad_sequences(sequences, maxlen=20, padding="post", truncating="post")

    # Get LSTM prediction
    prediction = lstm_model.predict(np.array([input_data]))  # Predict next response
    predicted_index = np.argmax(prediction, axis=-1)  # Get predicted word index

    # Convert prediction back to text
    index_word = {v: k for k, v in tokenizer.word_index.items()}  # Reverse dict
    lstm_response = index_word.get(predicted_index[0], "I don't understand.")

    return lstm_response
