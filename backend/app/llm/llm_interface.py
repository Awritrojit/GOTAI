# This file will use the ollama library to talk to the local LLM

import ollama
from .. import config
import logging

logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self):
        self.model = config.LOCAL_LLM_MODEL
        
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text using the local LLM via Ollama"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )
            return response['response'].strip()
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return "Error: Could not generate response."
    
    def generate_short(self, prompt: str) -> str:
        """Generate a short response (for scoring, etc.)"""
        return self.generate(prompt, max_tokens=10)

# Global instance
llm_client = LLMInterface()
