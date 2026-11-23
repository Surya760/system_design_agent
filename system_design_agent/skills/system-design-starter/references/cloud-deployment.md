# Cloud architecture and deployment plan

Use this guide when the user asks for a real-world architecture, cloud hosting, deployment stages, or production readiness.

## Required planning artifacts

Include:

- A provider-neutral or provider-specific deployment diagram showing environments, network boundaries, ingress/egress, compute, data services, secrets, telemetry, CI/CD, and external services.
- A technology/service matrix: workload, recommended service, why it fits, alternatives, support status/version checked, operational burden, and the condition that would justify changing it.
- A prerequisite checklist with owner/status, not just a list of products.
- A staged deployment plan with acceptance gates, rollback criteria, and who or what must approve each production stage.
- A practical operations section covering identity and access, secrets, network policy, data protection, backups/restores, monitoring, incident response, and cost controls.

Use a default structure such as these stages, tailoring or removing stages that do not fit:

1. **Discovery and account readiness:** select provider/region, verify data-residency/legal needs, account ownership, billing/budgets, quotas, DNS/domain, and IAM/security contacts.
2. **Local development:** define runtime/dependency versions, local configuration, test data, container/build approach, and secret-free developer onboarding.
3. **Development environment:** provision isolated network and services through version-controlled infrastructure-as-code; establish least-privilege roles, logs, and disposable data.
4. **CI/CD foundation:** build reproducibly, run lint/type/security/dependency checks as appropriate, publish immutable artifacts, manage deployment credentials through short-lived identity where supported, and record provenance.
5. **Staging and validation:** deploy production-like topology, seed synthetic data, exercise migrations, auth, integrations, load expectations, backups/restores, alerts, and rollback.
6. **Production readiness:** review threat model, access, privacy/retention, SLOs, runbooks, support ownership, backup objectives, cost budget, DNS/TLS, and change approvals.
7. **Canary and rollout:** release to a bounded audience or traffic slice, compare health and business signals, expand in steps, and stop/rollback at stated thresholds.
8. **Operations and evolution:** patch and rotate credentials, review spend and quotas, test recovery, manage schema/API deprecation, and revisit architecture when evidence crosses stated thresholds.

## Prerequisites to surface

Select the relevant items and state who supplies them and when:

- Cloud organization/project/subscription/account, region, billing owner, budget alert, and quota increases.
- Domain/DNS ownership, TLS/certificate plan, ingress/e-mail/payment/shipping accounts, and webhook endpoints.
- IAM groups/roles, break-glass path, workload identity, secret manager, key rotation, and audit logging.
- Network layout/CIDR ranges, private connectivity, firewall/egress policy, WAF/CDN needs, and environment separation.
- Runtime/toolchain versions, CLI/IaC versions, CI runner access, artifact registry, repository permissions, and deployment approval rules.
- Database ownership, engine/version, connection limits, encryption, backup retention, restore target, migration ownership, and data deletion policy.
- Expected traffic/data growth, latency/availability targets, recovery time/point objectives, support coverage, and launch window.
- Legal/security review, data classification/residency, privacy notice, retention, and vendor assessment where applicable.

Do not request or embed secret values. Explain where the user should provision them securely. Do not assume production accounts, permissions, budget, region, or approval authority.

## Stage gates

For each stage, define a small observable exit gate. Examples include successful infrastructure plan review; reproducible CI artifact; passing integration and migration checks; a restored backup within the recovery objective; alerts reaching the named owner; canary business/error signals staying within approved bounds; and a tested rollback. Use measurable thresholds only when supplied or label them as proposed values for review.

A deployment plan does not authorize actual provisioning. Before live mutations, confirm account/environment, resources, expected cost or quota effects, and rollback. Prefer plan/preview output and reviewable infrastructure changes before apply.
