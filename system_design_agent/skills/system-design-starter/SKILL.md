---
name: system-design-starter
description: Turn a product idea or existing codebase into a buildable system design, API contract, technology plan, data model, and staged cloud and CI/CD deployment plan. Use for architecture, stack choices, database diagrams, prerequisites, or a project foundation.
---

# System Design Starter

Help the user understand how their product can work and give them artifacts they can adapt and build from. Recommend the simplest architecture that meets stated needs. Separate confirmed facts, assumptions, recommendations, and open decisions.

## Choose the starting point

- **New idea:** Identify users, the problem, core journeys, and first useful release. Ask only for decisions that would materially change the design; otherwise state assumptions and continue.
- **Existing project:** Read its instructions, README, manifests, source structure, and relevant implementation. Treat the codebase as the source of truth and preserve its choices unless the user requests a change.
- **Idea plus existing code:** Explain what the current project already supports and what must change to reach the intended product.

## Choose deliverables

Match the output to the request. A design-only answer can be concise and inline. When the user wants a buildable project plan, create a reviewable architecture document and diagrams. When an API is part of the system, include both a machine-readable API definition and a human-readable API contract document unless the user asks for only one. When cloud deployment is in scope, include deployment stages and prerequisites; distinguish a plan from actually provisioning or deploying resources.

For complex contract, technology, database, or cloud work, read the relevant focused guide:

- For OpenAPI or another API contract, read [references/api-contracts.md](references/api-contracts.md).
- For cloud architecture, prerequisites, and staged deployment, read [references/cloud-deployment.md](references/cloud-deployment.md).
- For CI/CD architecture, release stages, promotion gates, and rollback, read [references/ci-cd-deployment.md](references/ci-cd-deployment.md).
- For supported technology choices, database design, and diagrams, read [references/technology-and-data.md](references/technology-and-data.md).

## Work from needs to design

Identify user journeys and quality needs that affect the design: scale, latency, availability, privacy, security, cost, platform, integrations, team skills, and delivery constraints. If scale or constraints are unknown, label a modest first-release assumption and show what decisions could change it.

Map the smallest useful architecture: interfaces, modules/services, data stores and ownership, external dependencies, important flows, identity/security boundaries, and operations. Prefer a modular monolith and managed services for an early product unless stated needs justify more. Explain tradeoffs and the point at which a simpler choice should change.

## Buildable design outputs

When producing a full design, include the relevant items below and save generated files together in a clear output folder:

1. Product scope, target users, journeys, assumptions, and open decisions.
2. Architecture diagram with trust boundaries and external dependencies.
3. Component responsibilities, data ownership, important request/event flows, and failure behavior.
4. Data model with entity relationships, constraints, indexes, migration approach, and a database diagram.
5. Technology choices tied to requirements, with alternatives and operational tradeoffs.
6. Security, privacy, reliability, observability, backup, restore, and recovery considerations.
7. API contract artifacts when an API is in scope: machine-readable definition plus human-readable contract document.
8. Cloud environment/deployment diagram, prerequisites, staged rollout, and rollback/recovery plan when deployment is in scope.
9. CI/CD workflow diagram or stage sequence, quality and security gates, artifact promotion, environment strategy, and release rollback when delivery automation is in scope.
10. Dependency-aware implementation milestones and acceptance criteria.

Use Mermaid for editable architecture, deployment, sequence, and ER diagrams when the target platform supports it. Provide a rendered image only when useful or requested. Keep diagrams consistent with the prose and contracts.

## Current technology and cloud support

When recommending cloud services, frameworks, database engines, runtimes, or versions whose support status may change, verify current claims against official vendor documentation. State the date checked and cite the vendor source in the delivered design. Distinguish generally available, preview, deprecated, and end-of-support features. Do not call a technology “supported” without a current authoritative source. Avoid fake precision in cost and capacity estimates; document the assumptions and use current pricing sources when the user needs a cost estimate.

Do not provision, deploy, purchase, publish, or change live infrastructure as part of producing a plan. Do those actions only when the user explicitly asks for them and the target account, environment, and expected effects are clear. Keep credentials and secret values out of generated artifacts.

## Existing projects and implementation

Separate observations from recommendations and cite repository files as evidence. If implementation is requested, turn the agreed design into reviewable files using existing conventions. Do not modify files merely because the user asked for a design. Ask before irreversible or externally visible actions.

## Boundaries

This skill provides a design and implementation starting point; it does not certify security, compliance, capacity, or production readiness. For regulated or high-impact systems, identify review needs and keep claims within evidence. Do not invent product requirements, repository details, performance figures, vendor capabilities, or launch decisions.
