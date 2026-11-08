"""
Resilience, Concurrency & Security Agent (Stage 4).
"""
from __future__ import annotations

from system_design_agent.agents.base_agent import BaseAgent
from system_design_agent.models.domain import ResilienceSection
from system_design_agent.prompts.stage4_resilience import STAGE4_PROMPT_TEMPLATE


class ResilienceAgent(BaseAgent):
    def run(self, pitch: str, stage3_context: str) -> tuple[ResilienceSection, int]:
        prompt = STAGE4_PROMPT_TEMPLATE.format(
            pitch=pitch.strip(),
            stage3_context=stage3_context.strip(),
        )
        resp = self.execute_with_retry(prompt)
        section = ResilienceSection(raw_markdown=resp.content.strip())
        return section, resp.tokens_used
