# API contract deliverables

Use this guide whenever the system exposes an HTTP API, webhook, event interface, or other integration contract.

## Files to produce

For a REST API, produce both:

- `openapi.yaml`: a valid OpenAPI document with the selected supported version, reusable schemas, operations, security schemes, examples, and error responses.
- `API_CONTRACT.md`: a human-readable guide for developers and product reviewers. Explain service purpose and base URL conventions, authentication/authorization, endpoints and methods, request/response examples, validation, status/error codes, pagination/filtering, idempotency, rate limits, versioning/compatibility, webhook verification/retries, and ownership.

For GraphQL, gRPC, async events, or another interface, create the matching machine-readable schema/IDL and readable contract guide. Do not force an OpenAPI file onto a non-REST interface.

## Contract rules

- Derive operations and fields from confirmed journeys and domain records. Mark unresolved behavior as open questions or use explicit `TBD` annotations; do not silently invent business policy.
- Specify required and optional fields, formats, bounds, nullability, enum evolution, identifiers, timestamps/time zones, currency/units, and ownership.
- Define stable error shape, validation behavior, authorization failures, retryability, and correlation identifiers.
- For writes with side effects, define idempotency scope, retention, duplicate response behavior, and concurrency guarantees.
- For webhooks/events, define authentication/signatures, event IDs, ordering expectations, retry schedule/terminal handling, replay, and deduplication.
- Use examples that validate against schemas. Keep secrets, real personal data, and production credentials out of examples.
- State contract versioning and compatibility rules. Provide a migration/deprecation path for breaking changes.
- If the user requests an actual document format such as DOCX/PDF, create that readable contract document as well as the machine-readable schema; keep it synchronized.

Before delivery, validate YAML/JSON syntax and schema structure with available tools when the user asks for validation or when the runtime provides a simple validator. Inspect consistency between the contract and architecture/data model. Do not claim conformance from merely reading the file.
