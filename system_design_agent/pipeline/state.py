"""
Pipeline state representation and stage tracking.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Dict, Optional


class PipelineStage(str, Enum):
    INIT = "INIT"
    REQUIREMENTS = "REQUIREMENTS"
    HLD = "HLD"
    LLD = "LLD"
    RESILIENCE = "RESILIENCE"
    SCAFFOLDING = "SCAFFOLDING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class PipelineState:
    current_stage: PipelineStage = PipelineStage.INIT
    stage_durations: Dict[str, float] = field(default_factory=dict)
    stage_tokens: Dict[str, int] = field(default_factory=dict)
    total_tokens: int = 0
    start_time: float = field(default_factory=time.time)
    error_message: Optional[str] = None

    def record_stage(self, stage_name: str, duration: float, tokens: int) -> None:
        self.stage_durations[stage_name] = duration
        self.stage_tokens[stage_name] = tokens
        self.total_tokens += tokens
