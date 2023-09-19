import requests
import json
from dotenv import load_dotenv
from typing import Generator
import os
import random

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_test_output():
    text = "Multithreading: In more complex applications or when dealing with long-running tasks (e.g., network requests or heavy computations), you might choose to use multiple threads. In this case, one thread can handle event listening and user input while another thread manages rendering and other tasks. This approach can help prevent blocking the main rendering loop, ensuring the user interface remains responsive."
    i = 0
    while i < len(text):
        n = random.randint(1, 8)
        yield text[i : i + n]
        i += n


def stream_chat_completion(prompt: str, test=True) -> Generator[str]:
    """Call OpenAI chat completion. Returns a generator of token strings."""
    if test:
        for i in generate_test_output():
            yield i
        return

    url = "https://api.openai.com/v1/completions"
    headers = {
        "Accept": "text/event-stream",
        "Authorization": "Bearer " + OPENAI_API_KEY,
    }
    body = {
        "model": "gpt-3.5-turbo-instruct",
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0,
        "stream": True,
    }
    response = requests.post(url, stream=True, headers=headers, json=body)
    buffer = ""
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            buffer += chunk.decode("utf-8")
            parts = buffer.split("\n")
            # Incomplete json string
            if len(parts) == 1:
                continue
            for part in parts[:-1]:
                if part == "" and part == "data: [DONE]":
                    continue
                try:
                    text = json.loads(part[6:].strip())["choices"][0]["text"]
                    print(f"'{text}'")
                    yield text
                except:
                    continue

            buffer = parts[-1]
