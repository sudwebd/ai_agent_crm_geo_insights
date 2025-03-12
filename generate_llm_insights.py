from openai import OpenAI
from keys.keys import OPEN_ROUTER_KEY
import json
import re

class generate_llm_insights:
    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Initializing generate_llm_insights class.")
        self.client = self._setup_openai()

    def _setup_openai(self):
        self.logger.debug("Setting up OpenAI client with base_url: %s", "https://openrouter.ai/api/v1")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPEN_ROUTER_KEY,
        )   
    
    def call_llm(self, model: str, prompt: json, content: json):
        self.logger.info("Calling LLM with model: %s", model)
        self.logger.debug("LLM request prompt: %s\nLLM request content: %s", prompt, content)
        self.logger.debug("Length of LLM input:", len(content) + len(prompt) + 2) 
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
        self.logger.debug("Parsed LLM response: %s", result)
        return result

    def extract_html(self, response_text):
        """Extracts the first valid HTML block from the response, ignoring Markdown-style code fences."""
        # First try to find HTML inside code blocks
        code_block_match = re.search(r'```(?:html)?\s*((?:<html>|<!DOCTYPE html|<[a-z][^>]*>)[\s\S]*?</html>)\s*```', response_text, re.IGNORECASE)
        if code_block_match:
            return code_block_match.group(1)
        
        # If not found in code blocks, look for HTML directly in the text
        direct_match = re.search(r'((?:<html>|<!DOCTYPE html|<[a-z][^>]*>)[\s\S]*?</html>)', response_text, re.IGNORECASE)
        return direct_match.group(1) if direct_match else None
