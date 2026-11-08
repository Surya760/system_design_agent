"""
Anthropic Claude API client implementation using standard library urllib.
Zero external dependencies required. Includes macOS SSL CA verification.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from system_design_agent.llm.base import LLMClient, LLMResponse
from system_design_agent.llm.ssl_context import get_ssl_context


class AnthropicClient(LLMClient):
    """Client for Anthropic Claude models (including Claude 3 Opus, 3.5 Sonnet, 3.5 Haiku)."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        base_url: str = "https://api.anthropic.com/v1",
        timeout: float = 120.0,
    ):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided for Claude provider.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.ssl_context = get_ssl_context()

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        url = f"{self.base_url}/messages"

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }

        if system_prompt:
            payload["system"] = system_prompt

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                content_blocks = resp_json.get("content", [])
                text_parts = [
                    block.get("text", "")
                    for block in content_blocks
                    if block.get("type") == "text"
                ]
                text_content = "".join(text_parts)

                usage = resp_json.get("usage", {})
                tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)

                return LLMResponse(
                    content=text_content,
                    tokens_used=tokens,
                    model=self.model,
                    provider="anthropic",
                )
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            try:
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = err_body
            raise RuntimeError(f"Anthropic Claude API HTTP {e.code}: {err_msg}") from e
        except Exception as e:
            raise RuntimeError(f"Anthropic Claude API request failed: {e}") from e
