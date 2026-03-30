import os
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Type, Any

class LLMClient:
    """Wrapper for LLM interactions."""
    
    def __init__(self, model_name: str = "gpt-4-turbo"):
        self.model_name = model_name
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def generate_text(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """Generate raw text response from the LLM."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    def generate_structured(self, prompt: str, response_model: Type[BaseModel], system_prompt: str = "You are a helpful assistant.") -> Any:
        """Generate structured response from the LLM using Pydantic."""
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format=response_model,
            temperature=0.2
        )
        return response.choices[0].message.parsed
