import aiohttp
import random
import asyncio
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import aiofiles

# Ensure the uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# List of common User-Agents (rotated to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36",
]

async def scrape_web_page(url: str) -> str:
    """
    Fetches a web page, extracts headings (h1-h6), paragraphs (p), and divs,
    then saves the text content in a file inside the 'uploads' directory.
    Returns the saved file's path.
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    await asyncio.sleep(random.uniform(1, 3))  # Random delay (1-3 sec) to avoid detection

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise ValueError(f"Failed to fetch the web page: {response.status}")

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # Extract text from headings, paragraphs, and divs
            extracted_text = "\n".join([
                element.get_text(strip=True) for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div"])
            ])
            
            if not extracted_text.strip():
                raise ValueError("No readable content found on the page.")

            # Generate timestamped filename with sanitized URL
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            sanitized_url = re.sub(r'\W+', '_', url).strip("_")[:50]  # Clean & shorten URL
            filename = f"{timestamp}_{sanitized_url}.txt"
            file_path = os.path.join(UPLOAD_DIR, filename)

            # Save extracted text asynchronously
            async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
                await file.write(extracted_text)

            return file_path  # Return the saved file path
