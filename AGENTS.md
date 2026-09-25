# Development Contract

This file defines how any contributor — human or AI agent — works in this repository. It applies to Claude Code, Codex, or any other coding agent reading this file.

## Source of Truth Priority

When code and documentation disagree, resolve in this order:

1. `docs/PRODUCT.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DATA_FLOW.md`
4. `specs/<feature>/SPEC.md`
5. Source code

Code must conform to the documents above, not the other way around. If code needs to diverge from a document, update the document first (see Change Rule).

## ID & Traceability Convention

Every traceable artifact gets a stable ID so diagrams, code, and tests can reference each other directly.

| Prefix | Meaning | Defined in |
|---|---|---|
| `BR-xxx` | Business Requirement | `docs/PRODUCT.md` |
| `WF-xxx` | Workflow step | `docs/PRODUCT.md` or `docs/WORKFLOWS.md` |
| `CMP-xxx` | Architecture Component | `docs/ARCHITECTURE.md` |
| `DF-xxx` | Data Flow node | `docs/DATA_FLOW.md` |
| `AC-xxx` | Acceptance Criterion | `specs/<feature>/ACCEPTANCE.md` |
| `ADR-xxx` | Architecture Decision Record | `docs/decisions/` |

Reference IDs directly in code and tests:

```python
# Implements: DF-003
class PackageSchemaValidator:
    ...
```

```python
def test_DF003_missing_required_column():
    ...
```

## Before Implementation

Before writing or changing production code, confirm:

1. Which `BR`/`WF` this serves.
2. Which `CMP`(s) it touches, and whether the responsibilities in `ARCHITECTURE.md` still hold.
3. Which `DF` node(s) it reads or writes, and whether the input/output contract changes.
4. What the failure/exception behavior is.
5. What the acceptance criteria are.

If any of these is materially unclear, stop and ask rather than guessing.

## Architecture Rule

Every component in `ARCHITECTURE.md` must state: responsibility, input, output, owner, dependencies, and failure behavior. Do not introduce a new architectural component without updating `ARCHITECTURE.md` first.

## Data Rule

Every non-trivial data transformation must be traceable as a `DF` node: source → input schema → transformation → output schema → persistence → downstream consumer. Do not silently change a `DF` node's input/output contract without updating `DATA_FLOW.md` first.

## Implementation Rule

```
SPEC → PLAN → TASK → CODE → TEST → CONVERGENCE
```

A feature is not "done" when the code merely runs — it is done when the criteria in its `ACCEPTANCE.md` pass.

## Change Rule

If implementation requires changing the architecture or a data contract:

1. Do not change it silently.
2. Create `docs/decisions/ADR-<next-number>-<slug>.md` (copy `docs/decisions/ADR-template.md`) describing the decision.
3. Update the relevant document (`ARCHITECTURE.md` / `DATA_FLOW.md`) to match.
4. Only then change the code.

## Extending This Template

This template ships with the minimal core (`PRODUCT` / `ARCHITECTURE` / `DATA_FLOW` / `specs`). Add more documents only when the project's complexity genuinely needs it:

- `docs/DOMAIN_MODEL.md` — when actors/entities/relationships get too complex for `PRODUCT.md`.
- `docs/WORKFLOWS.md` — when a business process has multiple actors/steps worth diagramming on its own (swimlane/sequence diagram).
- `docs/STATE_MODEL.md` — when a task or entity has non-trivial states and transitions (e.g. an approval workflow).

Reuse the same header pattern as `ARCHITECTURE.md` (Responsibility / Input / Output / Owner / Failure) for any new document. Do not invent a new format per document.

## Verification-first extension

The existing document priority describes approved product intent. It does not override organizational security rules, workspace boundaries or explicit human approvals. Descriptive AS-IS documents are observations, not permission to rewrite product semantics.

For an adopted verification map, follow `docs/HARNESS.md` and `verification/skills/verify-feature.md`:

1. Resolve symptoms through the existing feature catalog; read the actual entry point before proposing a cause. A new verification map is a projection, not a second mutable feature/authority registry.
2. Bind checks and evidence to the exact feature, run, map digest and commit. Preserve `failed`, `not_run`, `error` and unresolved work; never convert absence into success.
3. Exercise a positive path and a discriminating negative case. A synthetic fixture is not proof of real product E2E. Report both separately.
4. Reuse the official product path and independent expected-result oracle. Do not patch product logic or expected results merely to match the observed output.
5. Turn repeated failures into tested gates when deterministic enforcement is possible. Evaluate skill changes on held-out failures; an LLM judge is advisory, not the oracle.
6. Keep agents, adapters, leases, write scope and approvals in their existing owners. No automatic merge, deployment, durable judgment promotion or permission expansion follows from passing verification.
7. Protect verifier/map/oracle changes with independent review. An agent editing both implementation and its own gate cannot certify itself.

The shipped CLI validates contracts and evidence consistency only. It neither executes product checks nor authenticates who produced a receipt. State exactly what ran and in which environment.
