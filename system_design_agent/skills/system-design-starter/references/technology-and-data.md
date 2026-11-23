# Technology choices, data models, and diagrams

Use this guide when the user asks which supported technologies to build with, a real-world stack, database design, or prerequisites tied to the stack.

## Technology selection

Start with product constraints, expected load, team experience, hosting preference, data sensitivity, and budget. Recommend only the smallest coherent set of technologies. For each consequential choice, state:

| Field | What to capture |
|---|---|
| Role | What part of the system it serves |
| Choice | Product/service and version or support tier when relevant |
| Fit | Requirement it satisfies |
| Evidence | Official documentation URL and date checked for current support claims |
| Tradeoff | Cost, operations, lock-in, limits, or complexity |
| Alternative | A credible alternative and why it was not chosen |
| Change trigger | Evidence that would justify revisiting the choice |

Check official vendor lifecycle, supported-region, service limit, and compatibility documentation for volatile claims. Distinguish LTS/GA from preview, deprecated, and unsupported releases. Avoid unsupported claims like “best,” “enterprise-grade,” or “infinitely scalable.” Keep estimated costs separate from confirmed prices and show usage assumptions.

## Data model

Identify entities, ownership, cardinality, lifecycle, and source of truth. For relational storage, specify primary/foreign keys, uniqueness, nullability, constraints, indexes, transaction boundaries, deletion/retention, and migration/backfill strategy. For non-relational stores, explain access patterns, partition keys, consistency needs, TTL/retention, and hot-key risks. Include only tables/collections justified by real workflows; mark unresolved domain policy as TBD.

Create a Mermaid ER diagram when supported, using stable entity and field names. Match it to the contract and prose. Add a short field dictionary for fields whose units, privacy, or lifecycle are not obvious. Do not infer exact SQL DDL from an incomplete idea without labeling design assumptions.

## Diagram set

Choose diagrams based on the user's requested depth:

- **Architecture/context:** actors, application boundaries, external services, trust boundaries, and primary data flows.
- **Deployment:** environments, cloud/network boundary, ingress, compute, storage/database, secrets, observability, CI/CD, and external providers.
- **Data model:** ERD or equivalent model diagram.
- **Sequence:** use for a flow with important async callbacks, retries, or consistency behavior.

Keep diagrams readable and consistent with the selected stack. Prefer Mermaid source files (`architecture.mmd`, `deployment.mmd`, `database-erd.mmd`) or fenced Mermaid blocks inside the design document. Render to SVG/PNG only if the target cannot display Mermaid or the user asks for image files.
