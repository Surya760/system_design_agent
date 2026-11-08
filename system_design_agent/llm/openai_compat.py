"""
OpenAI-compatible client (works with OpenAI, Groq, Ollama, DeepSeek, LocalAI) using standard library urllib.
Zero external dependencies required. Includes macOS SSL CA verification.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from system_design_agent.llm.base import LLMClient, LLMResponse
from system_design_agent.llm.ssl_context import get_ssl_context


class OpenAICompatClient(LLMClient):
    """Client for OpenAI (GPT-4o, GPT-4o-mini, o1, o3-mini) and OpenAI-compatible providers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
        timeout: float = 120.0,
        provider_name: str = "openai",
    ):
        self.base_url = base_url.rstrip("/")
        # For non-local endpoints, ensure api_key is present
        is_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url
        if not api_key and not is_local:
            raise ValueError(f"OPENAI_API_KEY must be provided for {provider_name} provider.")

        self.api_key = api_key or "dummy-key-for-local"
        self.model = model
        self.timeout = timeout
        self.provider_name = provider_name
        self.ssl_context = get_ssl_context()

    def _is_reasoning_model(self) -> bool:
        """Detects OpenAI o-series reasoning models (o1, o1-mini, o3-mini)."""
        m = self.model.lower()
        return m.startswith("o1") or m.startswith("o3")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        is_reasoning = self._is_reasoning_model()

        messages = []
        if system_prompt:
            # o-series models accept 'developer' role or standard 'system'
            role = "developer" if is_reasoning else "system"
            messages.append({"role": role, "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        # Parameter adaptations for reasoning models (o1, o3-mini) vs standard chat models (gpt-4o)
        if is_reasoning:
            # Reasoning models use max_completion_tokens and do not allow custom temperature
            payload["max_completion_tokens"] = max_tokens
        else:
            payload["max_tokens"] = max_tokens
            payload["temperature"] = temperature

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as resp:
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
            try:
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = err_body
            raise RuntimeError(f"OpenAI API HTTP {e.code}: {err_msg}") from e
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}") from e
