"""
Orchestrates the multi-stage system design pipeline.
"""
from __future__ import annotations

import logging
from pathlib import Path
import re
import time
from typing import Callable, Optional

from system_design_agent.agents.hld_agent import HLDAgent
from system_design_agent.agents.lld_agent import LLDAgent
from system_design_agent.agents.requirements_agent import RequirementsAgent
from system_design_agent.agents.resilience_agent import ResilienceAgent
from system_design_agent.agents.scaffolding_agent import ScaffoldingAgent
from system_design_agent.config import AgentConfig
from system_design_agent.llm import get_llm_client
from system_design_agent.llm.base import LLMClient
from system_design_agent.models.spec import SystemDesignSpec
from system_design_agent.pipeline.state import PipelineStage, PipelineState
from system_design_agent.storage.db import SpecRepository
from system_design_agent.validators.spec_validator import SpecValidator

logger = logging.getLogger(__name__)

StageCallback = Callable[[PipelineStage, str], None]


class PipelineOrchestrator:
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        client: Optional[LLMClient] = None,
        repository: Optional[SpecRepository] = None,
    ):
        self.config = config or AgentConfig()
        self.client = client or get_llm_client(self.config)
        self.repo = repository or SpecRepository(self.config.database_path)

        # Initialize agents
        self.req_agent = RequirementsAgent(self.client, self.config)
        self.hld_agent = HLDAgent(self.client, self.config)
        self.lld_agent = LLDAgent(self.client, self.config)
        self.resilience_agent = ResilienceAgent(self.client, self.config)
        self.scaffolding_agent = ScaffoldingAgent(self.client, self.config)

    def _infer_title(self, pitch: str) -> str:
        first_line = pitch.strip().splitlines()[0]
        # Remove common prefixes
        clean = re.sub(r"^(build|create|design|a|an)\s+", "", first_line, flags=re.IGNORECASE).strip()
        words = clean.split()
        if len(words) <= 7:
            return clean.title()
        return " ".join(words[:6]).title() + " System"

    def run(
        self,
        pitch: str,
        title: Optional[str] = None,
        target_dau: Optional[int] = None,
        output_file: Optional[Path] = None,
        on_stage_update: Optional[StageCallback] = None,
    ) -> SystemDesignSpec:
        """Executes the complete multi-stage technical specification pipeline."""
        dau = target_dau or self.config.default_dau
        spec_title = title or self._infer_title(pitch)
        spec = SystemDesignSpec(title=spec_title, pitch=pitch, target_dau=dau)
        state = PipelineState()

        def notify(stage: PipelineStage, msg: str) -> None:
            state.current_stage = stage
            if on_stage_update:
                on_stage_update(stage, msg)

        overall_start = time.time()

        try:
            # -------------------------------------------------------------
            # Stage 1: Requirements & Core Assumptions
            # -------------------------------------------------------------
            notify(PipelineStage.REQUIREMENTS, "Synthesizing Functional & Non-Functional Requirements (50k DAU baseline)...")
            s_start = time.time()
            sec1, t1 = self.req_agent.run(pitch, target_dau=dau)
            state.record_stage("requirements", time.time() - s_start, t1)
            spec.requirements = sec1

            # -------------------------------------------------------------
            # Stage 2: High-Level Design (HLD) & Topology
            # -------------------------------------------------------------
            notify(PipelineStage.HLD, "Designing Architecture Paradigm, Component Topology & Tech Matrix...")
            s_start = time.time()
            sec2, t2 = self.hld_agent.run(pitch, sec1.raw_markdown, target_dau=dau)
            state.record_stage("hld", time.time() - s_start, t2)
            spec.hld = sec2

            # -------------------------------------------------------------
            # Stage 3: Low-Level Design (LLD), Schemas & Sequence Flow
            # -------------------------------------------------------------
            notify(PipelineStage.LLD, "Drafting PostgreSQL 16 DDL, REST Contracts, Domain Models & Sequence Flow...")
            s_start = time.time()
            sec3, t3 = self.lld_agent.run(pitch, sec2.raw_markdown)
            state.record_stage("lld", time.time() - s_start, t3)
            spec.lld = sec3

            # -------------------------------------------------------------
            # Stage 4: Resilience, Concurrency & Security
            # -------------------------------------------------------------
            notify(PipelineStage.RESILIENCE, "Hardening Concurrency Locks, Caching TTLs & Rate Limiting Policies...")
            s_start = time.time()
            sec4, t4 = self.resilience_agent.run(pitch, sec3.raw_markdown)
            state.record_stage("resilience", time.time() - s_start, t4)
            spec.resilience = sec4

            # -------------------------------------------------------------
            # Stage 5: Developer Action Plan & Scaffolding
            # -------------------------------------------------------------
            notify(PipelineStage.SCAFFOLDING, "Scaffolding Repository Layout & 4-Phase Developer Task Checklist...")
            s_start = time.time()
            sec5, t5 = self.scaffolding_agent.run(pitch, sec2.raw_markdown)
            state.record_stage("scaffolding", time.time() - s_start, t5)
            spec.scaffolding = sec5

            # -------------------------------------------------------------
            # Stage 6: Validation & Assembly
            # -------------------------------------------------------------
            notify(PipelineStage.VALIDATING, "Validating Mermaid Syntax, SQL Completeness & Architectural Consistency...")
            spec.tokens_used = state.total_tokens
            spec.duration_seconds = round(time.time() - overall_start, 2)
            spec.validation_report = SpecValidator.validate_spec(spec)

            # -------------------------------------------------------------
            # Export & Persistence
            # -------------------------------------------------------------
            out_path = output_file
            if not out_path:
                self.config.output_dir.mkdir(parents=True, exist_ok=True)
                out_path = self.config.output_dir / f"{spec.generate_slug()}.md"
            else:
                out_path.parent.mkdir(parents=True, exist_ok=True)

            markdown_content = spec.to_markdown()
            out_path.write_text(markdown_content, encoding="utf-8")

            self.repo.save(spec, markdown_path=str(out_path))
            notify(PipelineStage.COMPLETED, f"Specification successfully generated and saved to {out_path}")

            return spec

        except Exception as e:
            notify(PipelineStage.FAILED, f"Pipeline execution failed: {e}")
            state.error_message = str(e)
            raise
