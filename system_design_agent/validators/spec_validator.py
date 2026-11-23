"""
Comprehensive specification validator across all 5 sections.
"""
from __future__ import annotations

import re
from typing import List

from system_design_agent.models.domain import ValidationReport
from system_design_agent.models.spec import SystemDesignSpec
from system_design_agent.validators.mermaid_validator import MermaidValidator
from system_design_agent.validators.sql_validator import SQLValidator


class SpecValidator:
    """Validates the complete SystemDesignSpec against architectural standards."""

    @classmethod
    def validate_spec(cls, spec: SystemDesignSpec) -> ValidationReport:
        report = ValidationReport()

        # Section 1 Validation
        sec1 = spec.requirements.raw_markdown
        if not sec1 or len(sec1.strip()) < 100:
            report.add_error("Requirements", "Section 1 content is missing or too brief.")
        else:
            if not re.search(r"FR-\d+|1\.\s+\*\*|Functional Requirements", sec1, re.IGNORECASE):
                report.add_warning("Requirements", "Section 1 should list explicitly numbered functional requirements (e.g., FR-1, FR-2).")
            if not re.search(r"scale|availability|latency|privacy|security|cost|reliability|performance", sec1, re.IGNORECASE):
                report.add_warning("Requirements", "Section 1 should identify quality needs or state which ones remain open.")

        # Section 2 Validation (HLD)
        sec2 = spec.hld.raw_markdown
        if not sec2 or len(sec2.strip()) < 100:
            report.add_error("HLD", "Section 2 (HLD) content is missing or too brief.")
        else:
            valid_m, m_errs = MermaidValidator.validate_markdown(sec2)
            if not valid_m:
                for err in m_errs:
                    report.add_error("HLD.Mermaid", err)

            has_table = bool(re.search(r"\|(?:\s*[:-]+[-:]\s*\|)+", sec2))
            if not has_table:
                report.add_warning("HLD.TechStack", "Section 2 should include a markdown Technology Stack Matrix table.")

            if re.search(r"cloud|deploy|hosting|gcp|aws|azure", spec.pitch, re.IGNORECASE) and not re.search(r"vpc|subnet|ecs|eks|fargate|kubernetes|cloud|hosting|deployment", sec2, re.IGNORECASE):
                report.add_warning("HLD.CloudInfra", "Section 2 should detail Cloud Infrastructure & Network Topology (e.g. VPC, subnets, managed compute).")

        # Section 3 Validation (LLD)
        sec3 = spec.lld.raw_markdown
        if not sec3 or len(sec3.strip()) < 100:
            report.add_error("LLD", "Section 3 (LLD) content is missing or too brief.")
        else:
            if re.search(r"```sql\b", sec3, re.IGNORECASE):
                valid_sql, sql_errs = SQLValidator.validate_markdown(sec3)
                if not valid_sql:
                    for err in sql_errs:
                        report.add_error("LLD.SQL", err)

            valid_m, m_errs = MermaidValidator.validate_markdown(sec3)
            if not valid_m:
                for err in m_errs:
                    report.add_error("LLD.SequenceDiagram", err)

            if "```python" not in sec3 and "```typescript" not in sec3 and "```ts" not in sec3:
                report.add_warning("LLD.DomainModels", "Section 3 should include strongly typed domain models in Python or TypeScript.")

        # Section 4 Validation (Resilience)
        sec4 = spec.resilience.raw_markdown
        if not sec4 or len(sec4.strip()) < 80:
            report.add_error("Resilience", "Section 4 (Resilience & Security) content is missing or too brief.")
        else:
            if not re.search(r"concurrency|idempot|transaction|consistency|retry", sec4, re.IGNORECASE):
                report.add_warning("Resilience", "Section 4 should address consistency, retries, or concurrency where relevant.")

        # Section 5 Validation (Scaffolding & Plan)
        sec5 = spec.scaffolding.raw_markdown
        if not sec5 or len(sec5.strip()) < 80:
            report.add_error("Scaffolding", "Section 5 (Developer Action Plan) content is missing or too brief.")
        else:
            if not re.search(r"milestone|implementation|acceptance criteria|checklist|phase", sec5, re.IGNORECASE):
                report.add_warning("Scaffolding", "Section 5 should include dependency-aware implementation steps and acceptance criteria.")
            if not re.search(r"ci|cd|pipeline|deployment|rollout|docker|terraform", sec5, re.IGNORECASE):
                report.add_warning("Scaffolding.CloudPipeline", "Section 5 should describe the Cloud CI/CD & Deployment Pipeline.")

        if re.search(r"\b(api|rest|graphql|endpoint|webhook)\b", spec.pitch, re.IGNORECASE):
            if "openapi:" not in sec3.lower() and "```json" not in sec3.lower():
                report.add_warning("LLD.APIContract", "An API is in scope; include a machine-readable contract as well as readable API documentation.")
        if re.search(r"create table|database|persistent|stored", sec3, re.IGNORECASE) and "erdiagram" not in sec3.lower():
            report.add_warning("LLD.DataModel", "Include a Mermaid ER diagram when the selected data model has meaningful relationships.")

        return report
