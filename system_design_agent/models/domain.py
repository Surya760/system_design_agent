"""
Domain entities and structures representing the 5 core sections of a Technical Specification.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RequirementsSection:
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: Dict[str, Any] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    raw_markdown: str = ""


@dataclass
class HLDSection:
    architectural_paradigm: str = ""
    paradigm_rationale: str = ""
    topology_mermaid: str = ""
    tech_stack_matrix: List[Dict[str, str]] = field(default_factory=list)
    raw_markdown: str = ""


@dataclass
class LLDSection:
    sql_ddl: str = ""
    api_contracts: List[Dict[str, Any]] = field(default_factory=list)
    domain_models_code: str = ""
    sequence_diagram_mermaid: str = ""
    raw_markdown: str = ""


@dataclass
class ResilienceSection:
    concurrency_control: str = ""
    caching_strategy: Dict[str, Any] = field(default_factory=dict)
    security_and_rate_limiting: Dict[str, Any] = field(default_factory=dict)
    raw_markdown: str = ""


@dataclass
class ScaffoldingSection:
    directory_tree: str = ""
    implementation_checklist: List[Dict[str, Any]] = field(default_factory=list)
    raw_markdown: str = ""


@dataclass
class ValidationIssue:
    severity: str  # 'ERROR' | 'WARNING'
    stage: str
    message: str
    details: Optional[str] = None


@dataclass
class ValidationReport:
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)

    def add_error(self, stage: str, message: str, details: Optional[str] = None) -> None:
        self.is_valid = False
        self.issues.append(ValidationIssue(severity="ERROR", stage=stage, message=message, details=details))

    def add_warning(self, stage: str, message: str, details: Optional[str] = None) -> None:
        self.issues.append(ValidationIssue(severity="WARNING", stage=stage, message=message, details=details))
