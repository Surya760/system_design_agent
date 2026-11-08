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

#### Cloud CI/CD & Deployment Pipeline Blueprint
Specify the automated deployment pipeline for shipping code to the cloud:
- Continuous Integration (CI): Linting & formatting check, unit and integration test pass, container image build, vulnerability & secret scanning (e.g., Trivy, GitGuardian).
- Continuous Delivery (CD): Push versioned image to Container Registry (e.g., AWS ECR / GCP Artifact Registry), automated pre-deployment DB migration job (Alembic/Prisma/Flyway), and zero-downtime deployment rollout (e.g., Rolling Update with minimum healthy percent = 100%, Blue/Green with ALB traffic shifting, or Canary).
- Infrastructure as Code (IaC): Concrete Terraform or CloudFormation module layout for provisioning VPC, compute, and databases.
- Observability & Monitoring: Container health check probes (`/health/live`, `/health/ready`), Prometheus/CloudWatch metric alarms, structured JSON log streaming, and distributed tracing (OpenTelemetry).

#### Sequential Implementation Checklist
Provide a comprehensive 4-phase, checkbox-formatted (`- [ ]`) task list designed for junior and mid-level developers:
- Phase 1: Database Setup, Migrations & Core Models
- Phase 2: Core Domain Logic & Service Layer
- Phase 3: API Endpoints, Validation & Auth Middleware
- Phase 4: Async Workers, Caching, Edge Cases & Integration Tests

Each phase must contain 4–6 specific, granular tasks.

Output format: Return ONLY the GitHub-flavored markdown for Section 5.
"""
