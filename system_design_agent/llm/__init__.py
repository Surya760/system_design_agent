"""
LLM Provider Factory.
"""
from __future__ import annotations

import logging
from system_design_agent.config import AgentConfig
from system_design_agent.llm.anthropic import AnthropicClient
from system_design_agent.llm.base import LLMClient, LLMResponse
from system_design_agent.llm.gemini import GeminiClient
from system_design_agent.llm.mock import MockLLMClient
from system_design_agent.llm.openai_compat import OpenAICompatClient

logger = logging.getLogger(__name__)


def get_llm_client(config: AgentConfig) -> LLMClient:
    """Instantiates the appropriate LLM client based on configuration."""
    provider = config.resolve_provider()

    if provider == "gemini":
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required for Gemini provider.")
        return GeminiClient(
            api_key=config.gemini_api_key,
            model=config.gemini_model,
            timeout=config.timeout_seconds,
        )

    elif provider in ("anthropic", "claude"):
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Claude/Anthropic provider.")
        return AnthropicClient(
            api_key=config.anthropic_api_key,
            model=config.anthropic_model,
            base_url=config.anthropic_base_url,
            timeout=config.timeout_seconds,
        )

    elif provider in ("openai", "groq", "deepseek"):
        if not config.openai_api_key:
            raise ValueError(f"OPENAI_API_KEY is required for {provider} provider.")
        return OpenAICompatClient(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            model=config.openai_model,
            timeout=config.timeout_seconds,
            provider_name=provider,
        )

    elif provider == "ollama":
        return OpenAICompatClient(
            api_key="ollama",
            base_url=config.ollama_base_url,
            model=config.ollama_model,
            timeout=config.timeout_seconds,
            provider_name="ollama",
        )

    elif provider == "mock":
        return MockLLMClient()

    else:
        logger.warning("Unrecognized provider '%s'. Falling back to MockLLMClient.", provider)
        return MockLLMClient()


__all__ = [
    "LLMClient",
    "LLMResponse",
    "get_llm_client",
    "GeminiClient",
    "AnthropicClient",
    "OpenAICompatClient",
    "MockLLMClient",
]
