import os
from google import genai
from google.genai import types

async def get_gemini_response(prompt: str) -> str:
    """
    Sends the user message with context to the Gemini API and returns the response.
    """
    client = genai.Client(api_key="AIzaSyBrmxy7fu6MU8I38NpgeAjUePNE1_v20jY")
    model = "gemini-2.0-flash"

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        response_text += chunk.text

    return response_text
