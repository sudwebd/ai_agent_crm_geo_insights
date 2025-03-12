from openai import OpenAI
from typing import Dict, Optional
from keys.keys import OPEN_ROUTER_KEY
import json
import re

class GenerateLLMInsights:
    def __init__(self, logger) -> None:
        self.logger = logger
        self.logger.info("Initializing GenerateLLMInsights class.")
        self.client = self._setup_openai()

    def _setup_openai(self) -> OpenAI:
        self.logger.debug("Setting up OpenAI client with base_url: %s", "https://openrouter.ai/api/v1")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPEN_ROUTER_KEY,
        )   
    
    def call_llm(self, model: str, prompt: Dict, content: Dict) -> str:
        self.logger.info("Calling LLM with model: %s", model)
        self.logger.debug("LLM request prompt: %s\nLLM request content: %s", prompt, content)
        self.logger.debug("Length of LLM input: %d", len(str(content)) + len(str(prompt)) + 2)        
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

    def extract_html(self, response_text: str) -> Optional[str]:
        code_block_pattern = r'```(?:html)?\s*((?:<html>|<!DOCTYPE html|<[a-z][^>]*>)[\s\S]*?</html>)\s*```'
        direct_pattern = r'((?:<html>|<!DOCTYPE html|<[a-z][^>]*>)[\s\S]*?</html>)'        
        if match := re.search(code_block_pattern, response_text, re.IGNORECASE):
            return match.group(1)        
        if match := re.search(direct_pattern, response_text, re.IGNORECASE):
            return match.group(1)        
        return None
