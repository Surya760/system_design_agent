"""
OpenAI-compatible client (works with OpenAI, Groq, Ollama, DeepSeek, LocalAI) using standard library urllib.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from system_design_agent.llm.base import LLMClient, LLMResponse


class OpenAICompatClient(LLMClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
        timeout: float = 90.0,
        provider_name: str = "openai",
    ):
        self.api_key = api_key or "dummy-key-for-local"
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.provider_name = provider_name

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                choices = resp_json.get("choices", [])
                if not choices:
                    raise RuntimeError("No choices returned by OpenAI-compatible endpoint")

                content = choices[0].get("message", {}).get("content", "")
                usage = resp_json.get("usage", {})
                tokens = usage.get("total_tokens", 0)

                return LLMResponse(
                    content=content,
                    tokens_used=tokens,
                    model=self.model,
                    provider=self.provider_name,
                )
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {e.code}: {err_body}") from e
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}") from e
