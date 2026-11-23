"""
Prompts for Stage 1: Requirements & Core Assumptions.
"""

STAGE1_PROMPT_TEMPLATE = """You are acting in Stage 1 of the Technical Specification pipeline.
Analyze the following project pitch and generate Section 1: Requirements & Core Assumptions.

Project Pitch:
\"\"\"{pitch}\"\"\"

Target scale: use only values provided by the user. If unknown, state a modest first-release assumption and explain which unknowns could change the design. Do not force the configured DAU value into requirements as a user fact.

Required Output Structure:
### 1. Requirements & Core Assumptions

#### Functional Requirements (FRs)
List the key first-release capabilities as concise, unambiguous requirements. Use numbered IDs when they improve traceability.

#### Non-Functional Requirements (NFRs)
Describe availability, latency, durability, security, privacy, and cost needs that follow from the pitch. Quantify only when the user supplies a target or label the value as a proposed decision for review. Do not invent traffic, latency, uptime, or recovery targets.

#### Assumptions & Out-of-Scope (v1)
- Explicit technical and deployment assumptions.
- Open decisions that materially affect the architecture.
- Explicit out-of-scope boundaries to prevent scope creep for this MVP.

Output format: Return ONLY the GitHub-flavored markdown for Section 1. Do not include markdown code block backticks around the entire response.
"""
