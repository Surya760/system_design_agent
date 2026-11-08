"""
Prompts for Stage 5: Developer Action Plan & Scaffolding.
"""

STAGE5_PROMPT_TEMPLATE = """You are acting in Stage 5 of the Technical Specification pipeline.
Given the full technical design, generate Section 5: Developer Action Plan & Scaffolding.

Project Pitch:
\"\"\"{pitch}\"\"\"

Architecture Summary:
\"\"\"{hld_summary}\"\"\"

Required Output Structure:
### 5. Developer Action Plan & Scaffolding

#### Repository Directory Tree
Provide a complete, production-ready directory layout suited for the chosen technology stack (e.g., FastAPI, Node/Express, or Go). Include configuration, migrations, domain models, services, API routers, workers, tests, and CI/CD workflows.

#### Sequential Implementation Checklist
Provide a comprehensive 4-phase, checkbox-formatted (`- [ ]`) task list designed for junior and mid-level developers:
- Phase 1: Database Setup, Migrations & Core Models
- Phase 2: Core Domain Logic & Service Layer
- Phase 3: API Endpoints, Validation & Auth Middleware
- Phase 4: Async Workers, Caching, Edge Cases & Integration Tests

Each phase must contain 4–6 specific, granular tasks.

Output format: Return ONLY the GitHub-flavored markdown for Section 5.
"""
