"""
Low-Level Design Agent (Stage 3).
Validates SQL DDL completeness and Mermaid sequenceDiagram syntax with self-healing.
"""
from __future__ import annotations

import logging
from system_design_agent.agents.base_agent import BaseAgent
from system_design_agent.models.domain import LLDSection
from system_design_agent.prompts.stage3_lld import STAGE3_PROMPT_TEMPLATE
from system_design_agent.validators.mermaid_validator import MermaidValidator
from system_design_agent.validators.sql_validator import SQLValidator

logger = logging.getLogger(__name__)


class LLDAgent(BaseAgent):
    def run(self, pitch: str, stage2_context: str) -> tuple[LLDSection, int]:
        prompt = STAGE3_PROMPT_TEMPLATE.format(
            pitch=pitch.strip(),
            stage2_context=stage2_context.strip(),
        )
        resp = self.execute_with_retry(prompt)
        content = resp.content.strip()
        tokens = resp.tokens_used

        # Check SQL and Mermaid
        sql_valid, sql_errs = SQLValidator.validate_markdown(content)
        m_valid, m_errs = MermaidValidator.validate_markdown(content)

        issues = []
        if not sql_valid:
            issues.extend(sql_errs)
        if not m_valid:
            issues.extend(m_errs)

        if issues:
            logger.info("Stage 3 validation detected issues: %s. Attempting self-healing...", issues)
            heal_prompt = (
                f"The following LLD markdown has validation issues:\n"
                f"- {chr(10).join(issues)}\n\n"
                f"REMINDER: SQL DDL must be 100% complete PostgreSQL 16 (no '...', no TODOs). "
                f"Mermaid sequence diagrams must be valid syntax.\n\n"
                f"Original Section 3:\n{content}\n\n"
                f"Please fix all issues and return the corrected, complete Section 3 markdown."
            )
            try:
                heal_resp = self.execute_with_retry(heal_prompt)
                content = heal_resp.content.strip()
                tokens += heal_resp.tokens_used
            except Exception as e:
                logger.warning("LLD self-healing failed: %s. Keeping original content.", e)

        section = LLDSection(raw_markdown=content)
        return section, tokens
