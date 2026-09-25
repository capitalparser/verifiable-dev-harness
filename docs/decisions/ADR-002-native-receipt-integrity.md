# ADR-002: Extend the native receipt, not the number of harnesses

**Status:** Proposed; supplements ADR-001-risk-proportional-harness, no authority expansion.

## Context

While this change was being developed, PR #1 was merged at main `e4ba1922e2953afa797cdae72fed3a2b4319687c`. That approved direction already provides risk-proportional selection, one feature map, execution and receipts. Keeping the earlier parallel feature-map/receipt prototype would duplicate ownership and conflict with the new policy.

## Decision

Use the existing `harness/verification.json`, planner/runner and schema_version 1 receipt. Add run identity, finish time and hashes/sizes of executed logs. Add a read-only consumer that recomputes the selected plan through the same owner and checks source/run/context/manifest/check/log consistency. Keep docs/focused/full selection, external evidence storage and existing authority/lease ownership. Treat dirty evidence as workspace-bound, not a verified commit. Accept genuine silent successful checks when their recorded empty-byte hash and size match.

No new feature registry, model routing, automatic merge, mandatory model evaluation, signed attestation or mandatory CI is introduced. Provide an opt-in CI example rather than installing a workflow against the merged policy. Retain the original main tests unchanged and test the native producer/consumer together. The prior standalone prototype is removed from the PR's final diff.

## Consequences

Consumers can reject stale, incomplete or altered evidence without rerunning the suite or inventing a second plan. Old receipts without integrity metadata require an actual rerun. Matching hashes remain forgeable by a producer who controls both log and receipt. Native schema/selection reuse reduces duplication but requires protected review of shared verifier/expected-result code. Actual user-PC integration and product E2E remain separate from synthetic harness tests.

## Affects

- Architecture: CMP-H001, CMP-H002.
- Data flow: DF-H002, DF-H003.
- Contract and migration: `docs/EVIDENCE_INTEGRITY.md`.
