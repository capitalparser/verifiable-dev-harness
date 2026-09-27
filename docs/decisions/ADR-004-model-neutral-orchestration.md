# ADR-004: Model-neutral role contracts, not another orchestrator

**Status:** Proposed for maintainer review; no authority expansion.

## Context

The existing harness has source-grounded navigation, risk-proportional native execution and
receipt integrity, but no explicit planner/implementer/reviewer handoff contract. The user
requested detailed grounded planning, faithful implementation, and review against both plan
and original user requirements, without hardcoding model names or adding QA bottlenecks.

## Decision

Add role skills and one opt-in read-only handoff checker. Keep task/stage/budget/model/lease
ownership in the existing coordinator and reference its snapshot rather than creating a task
DB. Pin the existing plan's full file digest and source snapshot. Reuse the feature resolver
and native receipt consumer, never a second runner or a worker-authored green summary.
Route failures by cause. Review covers original scoped ACs, plan fidelity, real integration
and structure. A valid handoff proposes a next role but does not dispatch or approve it.

## Consequences

The checker catches missing inputs, stale bindings, illegal transitions, incomplete review,
false-green native evidence and exhausted declared budgets when explicitly invoked. It does
not authenticate the context issuer/model/session, maintain a replay ledger, judge semantic
correctness or enforce OS permissions. Full-file plan hashing is conservative: harmless edits
also require owner reconciliation. Model bindings are examples referencing existing adapters,
not an installed selector or provider SDK. Small work notes remain sufficient for small fixes.

## Affects / rollback

CMP-H005, DF-H006, BR-H003/WF-H003, AC-H020..H023 in docs/ORCHESTRATION.md. Existing
runner/receipt/feature IDs remain canonical. Revert this coherent extension to remove its
optional wiring; keep task records, receipts, source data, permissions and existing tests.
