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
Provide a complete, production-ready directory layout suited for the chosen technology stack (e.g., FastAPI, Node/Express, or Go). Include configuration, migrations, domain models, services, API routers, workers, tests, IaC (Terraform/Helm), and CI/CD workflows.

#### Cloud Deployment and CI/CD Plan
Tailor deployment stages and CI/CD to the selected provider and project. Separate the product's runtime/data pipeline from the CI/CD release pipeline. Cover prerequisites, test/security gates, immutable artifact publication, environment promotion, approvals, configuration/secrets, infrastructure changes, observability, and rollback/recovery. Cite official current support sources when available; mark unverified claims.

#### Sequential Implementation Checklist
Provide a dependency-aware, checkbox-formatted (`- [ ]`) task list with acceptance criteria:
- Phase 1: Database Setup, Migrations & Core Models
- Phase 2: Core Domain Logic & Service Layer
- Phase 3: API Endpoints, Validation & Auth Middleware
- Phase 4: Async Workers, Caching, Edge Cases & Integration Tests

Tailor milestones to the requested project; do not force four phases or a fixed number of tasks.

Output format: Return ONLY the GitHub-flavored markdown for Section 5.
"""
