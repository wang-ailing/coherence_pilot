import json
import os
from typing import Any, Dict, Optional, Type

from openai import OpenAI
from pydantic import BaseModel

from core.runtime_config import load_runtime_config

class LLMClient:
    """Wrapper for LLM interactions."""

    def __init__(self, model_name: Optional[str] = None):
        llm_config = load_runtime_config()["llm"]

        api_key = self._read_first_env(llm_config["api_key_envs"])
        base_url = self._read_first_env(llm_config["base_url_envs"]) or llm_config["default_base_url"]

        if base_url:
            base_url = self._normalize_base_url(base_url)

        if model_name is None:
            model_name = self._read_first_env(llm_config["model_envs"]) or llm_config["default_model"]

        if not api_key and base_url.startswith("http://127.0.0.1"):
            api_key = llm_config.get("local_api_key", "local-vllm")

        self.model_name = model_name
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def _read_first_env(names: list[str]) -> Optional[str]:
        for name in names:
            value = os.environ.get(name)
            if value:
                return value
        return None

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        """Accept either an API root or a full chat/completions endpoint."""
        normalized = base_url.rstrip("/")
        for suffix in ("/chat/completions", "/v1/chat/completions"):
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)]
                break
        if not normalized.endswith("/v1"):
            normalized = normalized + "/v1"
        return normalized
        
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

    def generate_json(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> Dict[str, Any]:
        """Generate JSON via plain chat completion for OpenAI-compatible APIs."""
        raw = self.generate_text(
            prompt=(
                prompt
                + "\n\nReturn valid JSON only. Do not wrap it in markdown fences or add explanations."
            ),
            system_prompt=system_prompt,
        )
        return json.loads(self._extract_json_payload(raw))

    @staticmethod
    def _extract_json_payload(raw: str) -> str:
        stripped = raw.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            stripped = stripped.replace("json\n", "", 1).strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            return stripped

        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            return stripped[start : end + 1]
        return stripped

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
