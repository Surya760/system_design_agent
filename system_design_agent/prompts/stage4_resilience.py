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

#### Concurrency & State Control
- Specific mechanism for race conditions (e.g., Optimistic locking via integer `version` column with code/SQL snippet, Redis distributed locks `Redlock` with TTL, or DB transactions with specific isolation levels like `REPEATABLE READ`).
- Explain the exact conflict resolution path when two concurrent requests hit the same resource.

#### Caching & Invalidation Rules
- Explicit caching pattern (e.g., Cache-Aside, Write-Through).
- Cache key naming conventions (e.g., `namespace:{{id}}:attribute`).
- Concrete TTLs (Time-To-Live in seconds/minutes).
- Synchronous or asynchronous invalidation triggers.
- Protection against cache stampede / thundering herd and negative caching.

#### Security & Rate Limiting
- Authentication & Authorization: Exact token standard (e.g., RS256 JWT in Authorization Bearer vs secure HTTP-only cookies, refresh token rotation).
- Rate Limiting: Algorithm (e.g., sliding window counter in Redis), explicit limits for authenticated vs unauthenticated traffic, burst thresholds.
- Input validation, SQL injection prevention, and encryption at rest / in transit.

Output format: Return ONLY the GitHub-flavored markdown for Section 4.
"""
