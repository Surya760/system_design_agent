"""
Developer Action Plan & Scaffolding Agent (Stage 5).
"""
from __future__ import annotations

from system_design_agent.agents.base_agent import BaseAgent
from system_design_agent.models.domain import ScaffoldingSection
from system_design_agent.prompts.stage5_scaffolding import STAGE5_PROMPT_TEMPLATE


class ScaffoldingAgent(BaseAgent):
    def run(self, pitch: str, hld_summary: str) -> tuple[ScaffoldingSection, int]:
        prompt = STAGE5_PROMPT_TEMPLATE.format(
            pitch=pitch.strip(),
            hld_summary=hld_summary.strip(),
        )
        resp = self.execute_with_retry(prompt)
        section = ScaffoldingSection(raw_markdown=resp.content.strip())
        return section, resp.tokens_used
