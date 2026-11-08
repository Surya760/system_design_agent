"""
Prompts for Stage 3: Low-Level Design (LLD).
"""

STAGE3_PROMPT_TEMPLATE = """You are acting in Stage 3 of the Technical Specification pipeline.
Given the Requirements and High-Level Design, generate Section 3: Low-Level Design (LLD).

Project Pitch:
\"\"\"{pitch}\"\"\"

Architecture Context:
\"\"\"{stage2_context}\"\"\"

Required Output Structure:
### 3. Low-Level Design (LLD)

#### Data Layer / Database Schema
Provide COMPLETE, copy-pasteable PostgreSQL 16 SQL DDL statements (`CREATE TABLE ...`):
- Explicit data types (UUID, TIMESTAMPTZ, VARCHAR(n), JSONB, etc.).
- Explicit NULL / NOT NULL markers.
- Primary Keys, Foreign Keys with `ON DELETE` rules, and CHECK constraints.
- Explicit B-tree / GIN indexes for query performance.
- STRICT RULE: NEVER write placeholders like '...', '// other columns', or 'TODO'. Every table must be complete and executable.

#### API Contracts
Provide a clear markdown table covering the essential REST endpoints:
- Columns: `Method`, `Endpoint Path`, `Auth Requirement`, `Request Body (JSON schema/sample)`, `Response Body (JSON schema/sample)`, and `Key Status Codes (200/201/400/401/404/409/500)`.

#### Core Domain Models / Entity Layer
Provide strongly typed class definitions (Python Pydantic v2 models or TypeScript interfaces) representing the business entities, enums, and request/response DTOs.

#### Execution Flow Sequence Diagram
A valid, renderable Mermaid `sequenceDiagram` mapping out the critical, end-to-end user transaction path (e.g., job submission, checkout, or auth+state change):
- Show participants: Client, Gateway, Service, Cache/Lock, Database, and Worker.
- Use `autonumber` and conditional blocks (`alt ... else ... end`).
- Quote participant names if they have spaces or special characters.

Output format: Return ONLY the GitHub-flavored markdown for Section 3.
"""
