# Development Contract

Applies to human contributors, Codex, Claude Code and other adapters. This is a
navigation and safety contract, not a requirement to create paperwork per edit.

## Authority and source of truth

User instructions and applicable organization/runtime safety rules take precedence.
This template does not expand an agent's authority, lease, merge or external-action permissions.
For approved intended behavior, use:

1. `docs/PRODUCT.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DATA_FLOW.md`
4. `specs/<feature>/SPEC.md` and its `ACCEPTANCE.md`

Read actual code and tests to establish **AS-IS** behavior. A placeholder, stale
narrative or generated map is not an approved requirement and cannot overrule
observed implementation. Mark disagreements; do not silently rewrite either side.

## Meaningful work units, not micro-slices

Default to one coherent, independently verifiable and reversible feature/fix per PR.
Keep its implementation, necessary tests, wiring and documentation together.
Split only for a genuine dependency, independent rollback, ownership boundary or
unreviewable scope. Never split by file, arbitrary line count or a 2–5 minute timer.
Avoid speculative refactors and unrelated improvements. Reuse the canonical owner
before extending it; introduce a new path only when the existing one cannot serve it.

## Before implementation

Identify the user outcome, code entrypoint/canonical owner, affected consumers,
input/output contract, failure behavior and the smallest convincing acceptance test.
Use existing BR/WF/CMP/DF/AC IDs when relevant; do not mint IDs for trivial edits.
Read nearby implementation and tests before diagnosing from a screenshot or guess.
For reversible details, record a reasonable assumption and proceed. Stop only at a
material unresolved requirement or authority, destructive-action or security boundary.

## Right-sized workflow

`SPEC -> PLAN -> IMPLEMENT -> VERIFY -> HANDOFF` describes reasoning, not five files or approvals.

- Localized fixes: a short PR/work-note with outcome, scope, test and risk is enough.
- Normal features: update the relevant SPEC/ACCEPTANCE; one short plan in the same unit.
- Architecture, durable data contracts or authority changes: record the material
  decision in an ADR and update the affected contract before implementing it.

Components retain responsibility/input/output/owner/dependencies/failure behavior.
Non-trivial transformations retain source/input/transform/output/storage/consumer lineage.
BR/WF/CMP/DF/AC/ADR IDs connect existing requirements, components, flows and tests.
They are not a requirement for repetitive comments or per-function documentation.

## Verification without a QA bottleneck

See `docs/HARNESS.md` for the executable policy and `docs/LOCAL_ADOPTION.md` for adoption.
Use the existing feature registry; connect symptom -> entrypoint -> journey -> check -> evidence.
For this template the runnable map is `harness/verification.json`.

During iteration, run the affected checks. At a stable handoff, run the selected
profile once. Full regression is conditional on shared/high-risk changes, unmapped
impact, a release/integration need or an existing mandatory policy; not every edit/PR.
A full run subsumes its focused checks: do not run both again on identical inputs.
Use one consolidated review at a stable feature boundary, not reviewer chains per patch.
Additional independent review is reserved for material security, authority, financial
calculation or durable-data risks. Do not require multiple models for ordinary changes.

A bug fix needs its reproduction and a relevant invariant/negative case; vary entity,
period or source when that dimension caused the failure. UI changes need the affected
real journey, not only a mocked unit test. Capture screenshots for visual claims;
traces/profiles only for timing, performance or memory claims. Never demand all artifacts.

Unknown impact is not a pass. Missing tools, skipped required checks, failed tests and
budgets exhausted are explicit incomplete evidence, not grounds to weaken an assertion.
No automatic retry-to-green. Investigate repeated failures before adding more QA layers.
Do not call a dirty-tree run a verified commit or a planned command an executed test.

## Guardrails and completion

Promote observed recurring mistakes into the smallest relevant lint/contract check.
Do not copy universal `useEffect`/comment bans or impose model evals on unrelated work.
Keep skill evals small and trigger them when that skill/routing/policy changes or a
related incident occurs; judge opinion never substitutes for a deterministic invariant.

Done means the scoped acceptance criteria have evidence, limitations are explicit,
and the next action is clear. Handoff: outcome, scope, SHA/dirty state, checks,
failures/omissions, receipt location and residual risk. Verification is not approval.
Do not merge, deploy, alter durable decisions or take external actions without the
existing authorization. Keep leases, registry/authority and worktree ownership intact.

Extend docs with DOMAIN_MODEL / WORKFLOWS / STATE_MODEL only when complexity needs it.
Prefer links to canonical records over duplicate documents or a second status registry.
