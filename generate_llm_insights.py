import logging
import json
import re
from openai import OpenAI
from keys.keys import OPEN_ROUTER_KEY

# Set up logging: Debug logging provides detailed info, Info logging shows necessary info.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class generate_llm_insights:
    def __init__(self):
        logging.info("Initializing generate_llm_insights class.")
        self.client = self._setup_openai()

    def _setup_openai(self):
        logging.debug("Setting up OpenAI client with base_url: %s", "https://openrouter.ai/api/v1")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPEN_ROUTER_KEY,
        )   
    
    def call_llm(self, model: str, prompt: json, content: json):
        logging.info("Calling LLM with model: %s", model)
        logging.debug("LLM request prompt: %s\nLLM request content: %s", prompt, content)
        logging.debug("Length of LLM input:", len(content) + len(prompt) + 2) 
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{content}"
                }
            ],
            response_format="json"
        )
        result = completion.choices[0].message.content
        logging.debug("Parsed LLM response: %s", result)
        return result
    
    import re

    def extract_html(self, response_text):
        """Extracts the first valid HTML block from the response, ignoring Markdown-style code fences."""
        match = re.search(r"(?:```html\s*)?(<!DOCTYPE html[\s\S]*?</html>)(?:\s*```)?", response_text, re.IGNORECASE)
        return match.group(1) if match else None  # Return only valid HTML or None if no match
