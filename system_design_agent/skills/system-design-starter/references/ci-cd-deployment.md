# CI/CD deployment planning

Use this guide when the user asks how to build, test, release, or operate their project through an automated delivery pipeline. Read it alongside `cloud-deployment.md` when both the runtime architecture and its release process are in scope.

## Keep the two pipelines distinct

Describe separately:

- **Product or data pipeline:** runtime processing performed by the deployed system, such as importing learning content each day.
- **CI/CD pipeline:** automated validation, packaging, and release of application, pipeline, and infrastructure code.

Show how a CI/CD release affects the running product pipeline, but do not conflate a daily data job with a code deployment.

## Design the release path

Choose tools based on the repository, cloud, team, security needs, and existing conventions. Show the release path as a diagram or ordered stages, with explicit triggers, outputs, and gates. A typical path includes:

1. **Pull request validation:** formatting and lint, unit tests, type or schema checks, dependency and secret scanning, and infrastructure validation as relevant.
2. **Build once:** create a versioned package or container image from the reviewed commit; record its commit and build provenance.
3. **Publish:** push the immutable artifact to a controlled registry, with access limited by environment and role.
4. **Deploy to development or staging:** apply environment configuration and infrastructure changes, then run smoke, integration, contract, and representative data checks.
5. **Approve production changes:** show the infrastructure plan, migration effects, and release notes to the responsible reviewer when risk warrants a human gate.
6. **Promote the same artifact:** deploy the already-tested digest to production; do not rebuild it with production settings.
7. **Verify and recover:** check health, key business metrics, logs, and alerts; define the rollback or forward-fix path.

Adapt the stages to the project. A small personal project may use fewer gates; regulated or high-impact systems may need stronger separation of duties, audit evidence, and approval controls.

## Environments, configuration, and security

- Name the environments and their purpose, such as development, staging, and production. Identify whether they use separate cloud projects/accounts, networks, data, and identities.
- Keep environment configuration outside the built artifact. Promote the same immutable image or package through environments.
- Give CI and each runtime environment least-privilege identities. For external CI providers on GCP, evaluate Workload Identity Federation rather than long-lived service-account keys.
- Store secrets in a managed secret store and reference them at runtime or through a controlled deployment step. Keep secret values out of repositories, logs, diagrams, and generated documents.
- Protect the production branch and release credentials. State who can approve or trigger production deployment.
- Include dependency, container, and infrastructure-as-code scanning when those artifact types are used; identify findings that block a release.

## Infrastructure and data changes

Explain how infrastructure-as-code is validated, planned, reviewed, and applied. Keep state, permissions, and environment boundaries explicit. Identify any manual console steps as prerequisites rather than hiding them in the pipeline.

For database changes, use backward-compatible expand-and-contract migrations where practical: add compatible schema, deploy code that can work with both versions, migrate data, then remove obsolete schema in a later release. State who owns migration execution and how it is observed.

For data-processing systems, distinguish deployment recovery from data recovery. A code rollback does not automatically reverse records already written. Include pause/resume, idempotency, checkpoints or watermarks, replay boundaries, duplicate handling, and reconciliation where relevant.

## Release and rollback plan

Specify the artifact and configuration version to restore, health signals that trigger rollback, who can initiate it, and how to verify recovery. Consider canary or gradual rollout when the platform and traffic shape support it. For irreversible schema or data changes, prefer a forward fix or an explicit compensating/replay plan; do not imply that redeploying older code reverses data changes.

## GCP examples and prerequisites

Potential GCP building blocks include Cloud Build for builds, Artifact Registry for packages and images, Cloud Deploy for delivery orchestration, Cloud Logging and Monitoring for verification, Secret Manager for secrets, and Workload Identity Federation for external identity. These are options, not mandatory choices. Check current official GCP documentation for supported features, availability, limitations, and pricing when recommending a concrete design; state the date checked and cite those sources.

List prerequisites that apply to the selected path, such as:

- source repository, protected branch, and CI trigger permissions;
- GCP project or project per environment, billing, and required APIs;
- build and deploy identities, IAM roles, and federation trust if CI runs outside GCP;
- artifact registry, retention policy, and image/package naming;
- selected build and deployment service, runners, network access, and approval owners;
- secret references, environment configuration, and workload identity;
- infrastructure state location and change review process;
- migration owner, rollback target, and data replay/reconciliation policy.

Verify current product names, feature status, and prerequisites against primary vendor documentation at design time. Do not provision resources or run a deployment while producing a plan. Actual live changes require an explicit request that identifies the target account and environment.
