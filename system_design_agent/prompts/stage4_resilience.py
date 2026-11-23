"""
Prompts for Stage 4: Resilience, Concurrency & Security.
"""

STAGE4_PROMPT_TEMPLATE = """You are acting in Stage 4 of the Technical Specification pipeline.
Given the previous architecture and schema design, generate Section 4: Resilience, Concurrency & Security.

Project Pitch:
\"\"\"{pitch}\"\"\"

LLD & Schema Context:
\"\"\"{stage3_context}\"\"\"

Required Output Structure:
### 4. Resilience, Concurrency & Security

#### Reliability, Consistency & Recovery
- Select retry, idempotency, concurrency, and transaction mechanisms that fit the actual workflow. Explain failure modes and the conflict resolution path. Avoid adding Redis or distributed locks without a demonstrated need.

#### Caching (when useful)
- Explain whether a cache is justified. If included, state its access pattern, invalidation, and how TTLs will be selected; label unmeasured values as proposals.

#### Security & Rate Limiting
- Authentication and authorization boundaries and least-privilege identities.
- Rate limits based on vendor quotas and expected load; state unknown quotas as prerequisites instead of inventing thresholds.
- Input validation, encryption, secret handling, privacy/retention, and observability appropriate to the data.

#### CI/CD Deployment and Recovery
- Describe validation, artifact build and promotion, environment separation, secrets/identity, approvals, and rollback when release automation is in scope.
- For data-processing systems, distinguish code rollback from replay or compensation of data already written.

Output format: Return ONLY the GitHub-flavored markdown for Section 4.
"""
