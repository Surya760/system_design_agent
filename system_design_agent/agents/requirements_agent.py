"""
Requirements & Scope Extraction Agent (Stage 1).
"""
from __future__ import annotations

from system_design_agent.agents.base_agent import BaseAgent
from system_design_agent.models.domain import RequirementsSection
from system_design_agent.prompts.stage1_requirements import STAGE1_PROMPT_TEMPLATE


class RequirementsAgent(BaseAgent):
    def run(self, pitch: str, target_dau: int = 50_000) -> tuple[RequirementsSection, int]:
        prompt = STAGE1_PROMPT_TEMPLATE.format(
            pitch=pitch.strip(),
            target_dau=target_dau,
        )
        resp = self.execute_with_retry(prompt)
        section = RequirementsSection(raw_markdown=resp.content.strip())
        return section, resp.tokens_used
