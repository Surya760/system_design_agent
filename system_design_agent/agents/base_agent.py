"""
Base Agent class with retry and error handling.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from system_design_agent.config import AgentConfig
from system_design_agent.llm.base import LLMClient, LLMResponse
from system_design_agent.prompts.system_persona import PRINCIPAL_ARCHITECT_PERSONA

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, client: LLMClient, config: AgentConfig):
        self.client = client
        self.config = config

    def execute_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> LLMResponse:
        retries = max_retries or self.config.max_retries
        sys_prompt = system_prompt or PRINCIPAL_ARCHITECT_PERSONA

        for attempt in range(1, retries + 1):
            try:
                response = self.client.generate(
                    prompt=prompt,
                    system_prompt=sys_prompt,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                return response
            except Exception as e:
                logger.warning(
                    "Attempt %d/%d failed with error: %s",
                    attempt,
                    retries,
                    e,
                )
                if attempt == retries:
                    raise
                time.sleep(self.config.retry_delay_seconds * attempt)

        raise RuntimeError("Exceeded maximum execution retries.")
