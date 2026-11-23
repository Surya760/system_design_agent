"""
Prompts for Stage 2: High-Level Design (HLD).
"""

STAGE2_PROMPT_TEMPLATE = """You are acting in Stage 2 of the Technical Specification pipeline.
Given the Project Pitch and Section 1 Requirements, generate Section 2: High-Level Design (HLD).

Project Pitch:
\"\"\"{pitch}\"\"\"

Section 1 Context:
\"\"\"{stage1_context}\"\"\"

Use the skill guidance in this prompt. Do not require a specific architecture pattern or provider when needs do not justify it. For current vendor support, use cited official documentation if available; otherwise flag status as unverified.

Required Output Structure:
### 2. High-Level Design (HLD)

#### Architectural Paradigm
- Chosen pattern (for example, a modular monolith or a distributed design when justified).
- Concrete rationale tied to stated needs and known scale. Label any modest first-release assumptions.

#### Component Topology Diagram
A valid, renderable Mermaid `graph TD` diagram illustrating the real actors, system boundary, necessary components, data stores, and external dependencies. Include a cache, broker, gateway, or replica only when the requirements justify it.

Important Mermaid Rules:
- Only use `graph TD` or `flowchart TD`.
- Enclose node labels in double quotes if they contain parentheses, slashes, or special symbols (e.g., `App["Core API (FastAPI)"]`).
- No trailing semicolons or malformed arrows.

#### Technology Stack Matrix
A concise markdown table covering:
- Runtime / Language
- Web / API Framework
- Primary Database
- Cache / Message Broker
- Infrastructure / Hosting (e.g., AWS ECS/EKS, RDS Multi-AZ, S3, CloudFront)
Include why each choice fits, one meaningful tradeoff, an alternative, and the evidence/source needed to verify volatile support claims.

#### Cloud Infrastructure & Network Topology (when deployment is requested)
- Cloud Provider Mapping (use the user's provider choice, or compare reasonable options if unspecified):
  - Environment boundaries, ingress/egress, managed compute, state, secret references, identity, telemetry, and prerequisites relevant to the selected architecture.
  - Include CIDRs, instance sizes, or autoscaling thresholds only when supplied or clearly marked as values to size during implementation.
- Include a separate Mermaid deployment diagram when the user requests a deployable/cloud design; show environment boundaries, ingress/egress, runtime, state, secrets/identity, telemetry, and CI/CD at an appropriate level.

Output format: Return ONLY the GitHub-flavored markdown for Section 2.
"""
