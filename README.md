# Verifiable Dev Harness

[한국어](README.ko.md) · **English**

> **Verification-first infrastructure for AI-assisted software development.**  
> Automate more of the development loop without giving up traceability, reproducibility, or human control.

AI coding agents can generate code quickly. The harder engineering problem is deciding:

- what actually changed,
- which checks are required,
- whether those checks really ran,
- what evidence supports the result,
- and what a passing result is allowed to authorize.

**Verifiable Dev Harness** is a lightweight repository harness for that problem.

It connects product intent, feature navigation, risk-proportional verification, executable checks, and evidence handoff so that humans and coding agents can work against the same source of truth.

---

## Why this exists

The goal is not maximum agent autonomy.

The goal is:

> **maximize useful development automation while keeping the result explainable, reproducible, and challengeable.**

That leads to five design principles.

1. **Make the correct path the easy path.**  
   Move recurring constraints into architecture, contracts, lint, and executable checks instead of repeating them in prompts.

2. **Verify behavior, not narratives.**  
   “I tested it” is not evidence. Record the command, source state, environment, result, and logs.

3. **Scale verification with risk.**  
   Run the smallest convincing set of checks for the change, then escalate when shared contracts, authority, durable data, calculations, or unmapped impact are involved.

4. **Keep authority boundaries explicit.**  
   Verification evidence does not automatically grant merge, deployment, business-decision, or external-action authority.

5. **Do not make verification the next bottleneck.**  
   Avoid micro-sliced PRs, duplicate full regression, unnecessary reviewer chains, and documentation that does not improve confidence.

---

## The development loop

```mermaid
flowchart LR
    A["Intent<br/>PRODUCT / SPEC / AC"] --> B["Feature Map<br/>symptom → entrypoint → checks"]
    B --> C["Change<br/>human or coding agent"]
    C --> D["Impact Selection<br/>docs / focused / full"]
    D --> E["Execute Checks<br/>real commands"]
    E --> F["Evidence Receipt<br/>SHA · environment · logs · status"]
    F --> G["Integrity Validation<br/>recompute & compare"]
    G --> H["Existing Control Boundary<br/>review · merge · deploy"]
```

A passing verification result is **evidence**, not approval.

---

## What is included

| Area | Purpose | Main entry point |
|---|---|---|
| Development contract | Authority, source-of-truth, work-unit, and verification rules | `AGENTS.md` |
| Product intent | Problem, actors, business requirements | `docs/PRODUCT.md` |
| Architecture | Component responsibilities and boundaries | `docs/ARCHITECTURE.md` |
| Data flow | Source → transformation → persistence → consumer lineage | `docs/DATA_FLOW.md` |
| Feature contract | Feature behavior and acceptance criteria | `specs/` |
| Verification policy | Risk-proportional verification and evidence semantics | `docs/HARNESS.md` |
| Feature navigation | Symptom → feature → spec → source → test lookup | `tools/feature_map.py` |
| Verification runner | Select and execute the relevant check set | `tools/verify.py` |
| Evidence integrity | Recompute the plan and validate receipt/log consistency | `tools/verify_receipt.py` |
| Runnable journey pilot | Disposable environment for an actual CLI journey | `tools/harness_journey.py` |
| Local adoption | Integrate without replacing existing registry/lease/runner owners | `docs/LOCAL_ADOPTION.md` |

The repository itself is also the pilot system. Its runnable feature map is in `harness/verification.json`.

---

## 1. Risk-proportional verification

Verification is selected from the actual change surface.

- **docs** — documentation-only changes and lightweight structural checks
- **focused** — affected feature checks and its real journey
- **full** — shared/high-risk or unmapped changes, integration/release needs, or existing mandatory policy

The runner will not silently downgrade a change below its computed minimum profile. Duplicate check IDs are executed once.

```sh
# Plan only — no verification has run yet
python -B tools/verify.py --base origin/main --plan

# Execute the selected verification once
python -B tools/verify.py \
  --base origin/main \
  --output ../vdh-evidence/run-001 \
  --context local
```

`origin/main` is only an example. Use an approved comparison ref or immutable commit in your environment.

---

## 2. Feature Map as navigation infrastructure

The Feature Map is not a second requirements database.

It connects existing intent and implementation so that an agent can move from a vague report to the relevant source and verification path.

```text
user symptom
  ↓
feature
  ↓
SPEC / Acceptance Criteria
  ↓
actual source entrypoints
  ↓
tests / journey / failure probe
```

Example:

```sh
python -B tools/feature_map.py lookup --query "verification missing"
python -B tools/feature_map.py lint
```

The current implementation resolves Python symbols and Markdown acceptance headings without importing or executing the target code.

Broken references fail lint instead of silently becoming stale navigation.

The map is deliberately **navigation, not diagnosis**. Matching a feature does not prove the root cause.

---

## 3. Evidence-producing verification

The runner records source state and actual execution instead of only returning green/red.

A receipt can contain:

- head / base / merge-base SHA
- dirty workspace state and workspace digest
- selected profile and checks
- actual argv
- environment and non-secret context
- `PASS / FAIL / TIMEOUT / ERROR / NOT_RUN / STALE`
- elapsed time
- log path, size, and SHA-256
- run ID and timestamps

A failed check leaves remaining checks as `NOT_RUN`. There is no automatic retry-to-green.

Evidence is written outside the checkout to reduce source/evidence collisions.

---

## 4. Receipt integrity is not execution attestation

`tools/verify_receipt.py` recomputes the expected source state and check plan and compares them with the submitted receipt and logs.

It can reject inconsistencies such as:

- stale or different source state
- missing, duplicated, or unexpected checks
- command drift
- altered or missing logs
- mismatched run/context/manifest
- failed, timed-out, or not-run checks represented as success

But hashes are not identity.

A producer who controls both the receipt and logs can fabricate mutually matching bytes. This harness therefore does **not** claim cryptographic execution attestation.

Verified evidence does not imply:

```text
execution_attested = true
merge_authorized   = true
```

Trusted execution environments, independent review, branch protection, and approval policy remain separate concerns.

See `docs/EVIDENCE_INTEGRITY.md`.

---

## 5. Factory-ready execution before agent scale

Before scaling to many agents, a feature should be reproducible in a controlled environment.

```text
prepare known state
→ invoke the real product path
→ exercise a success case
→ exercise a discriminating failure case
→ inspect observable output
→ collect evidence
→ clean up only owned resources
```

This repository includes a native CLI pilot through `tools/harness_journey.py`.

It is a harness self-test, not proof that another product's UI or business workflow is correct.

For a web or service product, replace that pilot with the product's real input → processing → output journey while reusing the existing browser, database, container, or test-environment tooling.

See `docs/FACTORY_READY.md`.

---

## Source-of-truth model

```text
PRODUCT
  ↓
ARCHITECTURE
  ↓
DATA_FLOW
  ↓
Feature SPEC / ACCEPTANCE
  ↓
source code + tests
  ↓
execution evidence
```

Code establishes **AS-IS behavior**.

Approved product/spec documents establish **intended behavior**.

When they disagree, the disagreement should be surfaced — not silently normalized by rewriting one from the other.

Structural references can be automated. Semantic intent still requires explicit ownership.

---

## Human, deterministic, and AI responsibilities

This project does not prescribe one universal operating model. It encourages explicit task-level boundaries.

| Responsibility | Typical owner |
|---|---|
| Deterministic validation, invariants, selection, reconciliation | Code / rules |
| Navigation, implementation, test execution, candidate generation | Coding agent or developer |
| Ambiguous judgment, policy changes, exceptions | Human / domain owner |
| Merge, deployment, durable decisions, external actions | Existing authorized control |

A task performed by an LLM does not automatically gain decision authority.

A human-owned outcome does not mean every step must be performed manually.

---

## Quick start

Requirements:

- Python 3.10+
- Git
- no external Python packages for the core harness

```sh
# 1. Validate feature navigation
python -B tools/feature_map.py lint

# 2. Inspect what would run
python -B tools/verify.py --base origin/main --plan

# 3. Run verification
python -B tools/verify.py \
  --base origin/main \
  --feature harness-verification \
  --output ../vdh-evidence/run-001 \
  --context local

# 4. Run the disposable native journey directly
python -B tools/harness_journey.py
```

For receipt-integrity usage, see `docs/EVIDENCE_INTEGRITY.md`.

---

## Adopting this in an existing repository

Do **not** blindly copy the whole harness over an established development system.

First identify the existing owners of:

- feature registry or product map
- agent registry / authority model
- work leases or concurrency control
- verification entry point
- test fixtures and expected-result oracle
- CI / branch protection / review policy

Then integrate only the missing contracts and evidence path.

If you already have a good runner, keep it. If you already have a feature registry, extend or export it instead of creating another manually maintained source of truth.

See `docs/LOCAL_ADOPTION.md`.

---

## What this project intentionally does not do

This is not:

- an autonomous merge or deployment bot
- an OS-level sandbox
- a universal agent orchestrator
- a proof that a test suite is semantically correct
- an execution-attestation or cryptographic identity system
- a replacement for product-specific E2E testing
- a reason to run every regression suite on every change
- a requirement to use multiple LLM judges for ordinary PRs

The harness is meant to make development **more observable, reproducible, and falsifiable** without turning verification itself into the next bottleneck.

---

## Repository structure

```text
.
├── AGENTS.md
├── docs/
│   ├── PRODUCT.md
│   ├── ARCHITECTURE.md
│   ├── DATA_FLOW.md
│   ├── HARNESS.md
│   ├── FACTORY_READY.md
│   ├── EVIDENCE_INTEGRITY.md
│   ├── LOCAL_ADOPTION.md
│   └── decisions/
├── harness/
│   ├── verification.json
│   ├── fixtures/
│   ├── skills/
│   └── examples/
├── specs/
│   ├── _template/
│   └── harness-verification/
├── tools/
│   ├── verify.py
│   ├── verify_receipt.py
│   ├── feature_map.py
│   └── harness_journey.py
└── tests/
```

---

## Direction

The long-term direction is simple:

> **A development system where agents can understand the product, make bounded changes, execute the real path, produce evidence, and leave the final authority boundary explicit.**

A planned next layer is a **human-readable system/process/decision map** generated from the same source contracts — showing modules, workflows, rule-based tasks, AI-assisted tasks, human decisions, and their verification status without creating another manually maintained source of truth.

The metric is not how many agents or PRs the system can produce.

The metric is how much of the development loop can be automated **without losing the ability to explain, reproduce, and challenge the result**.
