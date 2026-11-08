"""
Gemini API client implementation using standard library urllib.
Zero external dependencies required.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from system_design_agent.llm.base import LLMClient, LLMResponse
from system_design_agent.llm.ssl_context import get_ssl_context


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", timeout: float = 90.0):
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.ssl_context = get_ssl_context()

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                candidates = resp_json.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No candidate responses returned by Gemini API")

                content_parts = candidates[0].get("content", {}).get("parts", [])
                text_content = "".join(part.get("text", "") for part in content_parts)

                usage = resp_json.get("usageMetadata", {})
                tokens = usage.get("totalTokenCount", 0)

                return LLMResponse(
                    content=text_content,
                    tokens_used=tokens,
                    model=self.model,
                    provider="gemini",
                )
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini API HTTP {e.code}: {err_body}") from e
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {e}") from e
