"""
High-Level Design Agent (Stage 2).
Includes Mermaid topology validation and self-healing.
"""
from __future__ import annotations

import logging
from system_design_agent.agents.base_agent import BaseAgent
from system_design_agent.models.domain import HLDSection
from system_design_agent.prompts.stage2_hld import STAGE2_PROMPT_TEMPLATE
from system_design_agent.validators.mermaid_validator import MermaidValidator

logger = logging.getLogger(__name__)


class HLDAgent(BaseAgent):
    def run(self, pitch: str, stage1_context: str, target_dau: int = 50_000) -> tuple[HLDSection, int]:
        prompt = STAGE2_PROMPT_TEMPLATE.format(
            pitch=pitch.strip(),
            stage1_context=stage1_context.strip(),
            target_dau=target_dau,
        )
        resp = self.execute_with_retry(prompt)
        content = resp.content.strip()
        tokens = resp.tokens_used

        # Validate Mermaid diagram
        valid, errors = MermaidValidator.validate_markdown(content)
        if not valid:
            logger.info("Stage 2 Mermaid validation found issues: %s. Attempting self-healing...", errors)
            heal_prompt = (
                f"The following HLD markdown has syntax errors in its Mermaid topology diagram:\n"
                f"Errors: {', '.join(errors)}\n\n"
                f"Original Section 2:\n{content}\n\n"
                f"Please fix all Mermaid syntax errors and return the corrected complete Section 2 markdown."
            )
            try:
                heal_resp = self.execute_with_retry(heal_prompt)
                content = heal_resp.content.strip()
                tokens += heal_resp.tokens_used
            except Exception as e:
                logger.warning("HLD self-healing failed: %s. Keeping original content.", e)

        section = HLDSection(raw_markdown=content)
        return section, tokens
