"""
Prompts for Stage 1: Requirements & Core Assumptions.
"""

STAGE1_PROMPT_TEMPLATE = """You are acting in Stage 1 of the Technical Specification pipeline.
Analyze the following project pitch and generate Section 1: Requirements & Core Assumptions.

Project Pitch:
\"\"\"{pitch}\"\"\"

Target Baseline Scale: ~{target_dau:,} Daily Active Users (DAU) if not specified by user.

Required Output Structure:
### 1. Requirements & Core Assumptions

#### Functional Requirements (FRs)
Provide a minimum of 4–6 numbered, unambiguous system capabilities (FR-1, FR-2, etc.).

#### Non-Functional Requirements (NFRs)
Provide explicit, quantified metrics:
- Throughput & RPS: Derive average and peak RPS explicitly from the {target_dau:,} DAU baseline (e.g., interactions/day -> average RPS -> peak RPS burst multiplier).
- Latency Ceilings: Specify explicit percentiles (e.g., p95 < 150ms, p99 < 300ms for writes; p95 < 50ms for reads).
- Read/Write Ratio: Specific ratio (e.g., 10:1 or 80:20).
- Availability & Durability: Uptime SLA target (e.g., 99.9%) and RPO/RTO.

#### Assumptions & Out-of-Scope (v1)
- Explicit technical and deployment assumptions.
- Explicit out-of-scope boundaries to prevent scope creep for this MVP.

Output format: Return ONLY the GitHub-flavored markdown for Section 1. Do not include markdown code block backticks around the entire response.
"""
