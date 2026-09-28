# Model-neutral orchestration contracts

모델 이름보다 역할·입출력·권한·인계 근거를 먼저 고정합니다. 계획자는 중요한 추측을 없애고,
구현자는 공식 소비 경로까지 연결하며, 리뷰어는 **계획 준수와 원래 요구사항 충족을 모두** 확인합니다.
기존 coordinator가 역할을 배정합니다. 이 확장은 모델을 호출하거나 새로운 실행기를 설치하지 않습니다.

## BR-H003

Make plan → implementation → native verification → review handoffs inspectable across
models and sessions, without duplicating the feature registry, runner, receipt, lease or
approval owner. A correct-looking review of an incorrect plan is not sufficient.

## WF-H003

The existing coordinator grounds the request in the feature map, selects an allowed role
and supplies the context bundle. Planner → implementer → native verifier → reviewer →
coordinator is the normal path. The last step is an evidence handoff, **not automatic merge**.
Failures return to the responsible role, not blindly to another model.

## Roles and routing

| Role | Required work / handoff | Boundary |
|---|---|---|
| Planner | Read actual sources and consumers; define outcome, scope, existing owner, contracts, implementation steps, wiring, failure paths, checks and remaining decisions | Do not invent paths, replace the business oracle, or approve a policy change |
| Implementer | Implement the pinned plan, including actual entrypoints, consumers, tests and necessary docs; record deviations and missing work | Do not silently change semantics/authority or make a parallel implementation |
| Verifier | Execute the selected native checks; retain FAIL/TIMEOUT/ERROR/NOT_RUN and native receipt/logs | A model narrative is not a native execution result |
| Reviewer | Compare original ACs, plan, implementation, integration, structure and evidence; report actionable findings | Do not fix and independently certify the same work or rewrite expected results to match it |
| Coordinator | Own stage, bindings, scope, budgets, handoffs and failure routing | Do not fabricate completion or expand existing authority/lease permissions |

Use [plan-change](../harness/skills/plan-change.md),
[implement-plan](../harness/skills/implement-plan.md),
[review-change](../harness/skills/review-change.md) and the existing
[verify-feature](../harness/skills/verify-feature.md) skill. Roles are not a requirement for
four models, permanent agents, four PRs, or repeated review chains.

### Plan granularity and changes

For a localized fix, use a short section in the existing work note/SPEC. For a substantial
feature, specify the user outcome and exclusions, canonical owner and evidence read,
input/output schemas, invariants, exceptions, implementation approach, real consumer wiring,
independently defined normal/negative expectations, verification scope and open decisions.
The target is **no material guessing by the implementer**, not maximum document length.
Reversible internal choices can remain autonomous. A material change to user outcomes,
contracts, calculations, ownership or authority goes back to the planner; the human decision
boundary applies only where existing policy requires it. Record assumptions separately from facts.

Reuse the existing SPEC and ACCEPTANCE. The plan identity is a SHA-256 of the complete
referenced Markdown file, optionally with a heading for navigation. Changing any bytes in
that file invalidates the binding; the owner must issue a new context and reassess affected
verification. Do not edit the old context or receipt to manufacture continuity.

### Failure transitions (implemented)

| Event | Allowed sender | Next role |
|---|---|---|
| `ready` | planner / implementer / verifier / reviewer | implementer / verifier / reviewer / coordinator, respectively |
| `implementation_gap` | verifier, reviewer | implementer |
| `plan_gap` | implementer, verifier, reviewer | planner |
| `environment_blocked` | any of the four roles | environment_owner |
| `authority_blocked` | any of the four roles | human |
| `invalid_output` | any of the four roles | same role, correcting the packet only |

A non-ready event needs a concrete gap and finding reference. It is a **valid failure
handoff**, not a successful task. A ready event cannot contain unresolved gaps or a material
plan deviation. Unknown events, skipped roles and merge/deploy destinations are rejected.
An exhausted owner-issued attempt budget returns BLOCKED to the coordinator. Keep the
same failure from consuming an unbounded series of model swaps. Only retry with new root-cause
information or an actual correction. The owner, not this checker, increments counters and
tracks elapsed time, cost and repeated-failure history.

## Role-to-model bindings (guidance, not an implemented dispatcher)

Start with the operator's existing default adapter for planner/implementer/reviewer. Reuse
the same model when appropriate; use a fresh review context when required by the risk policy.
Use the native runner for verifier. Choose a different model only when its permitted data
scope, tools and demonstrated capability fit the role. Data policy and required capabilities
come before cost/latency. Missing read/write/browser permissions mean STOP, not silent escalation.

[role-bindings.example.json](../harness/examples/role-bindings.example.json) contains **external
registry references only**; null means unconfigured. It is an integration example, not a live
configuration consumed by the checker. No model ranking, credential, SDK, API endpoint or
provider-specific default is installed. Record the actual selected adapter/model reference,
session, selection reason and capability evidence in the existing task log. The checker
validates attribution fields but does not authenticate them or assess model quality.

A separate session is a checkable requirement, not proof of independent reasoning. Multiple
models can share errors. Keep the expected-result oracle independent of the implementation,
and require independent review for the existing security/authority/financial/durable-data risks.
Do not mandate multiple model judges for routine changes. Parallelize only tasks with distinct
existing leases/write ownership; shared contracts require coordination, not more agents.

## CMP-H005: Read-only handoff checker

- **Responsibility:** Validate one claimed role transition against an owner-issued context.
- **Input:** Context snapshot, role packet, pinned plan/source and native evidence when required.
- **Output:** `HANDOFF_VALID` or `BLOCKED`, proposed next role and explicit evidence scope.
- **Owner:** Existing coordinator; `tools/orchestration_contract.py` does not own stage history.
- **Depends on:** Existing `feature_map.resolve/source_file`, `verify.snapshot/select` and
  `verify_receipt.validate_receipt`; Python standard library and Git.
- **Must NOT:** Dispatch models/check commands, mutate worktrees/registries/leases, install
  dependencies, advance task state, authorize external actions, merge or deploy.
- **Failure:** Missing fields, bad refs, stale plan/source, illegal transitions, exhausted
  budgets, incomplete review or native evidence mismatches block with exit 1. CLI errors exit 2.

### Context contract v1

The context is an export of the **existing task owner**, not a new manually maintained registry.
It must not be synthesized from the untrusted worker packet merely to make it pass.

| Field | Required content |
|---|---|
| `version`, `task_id`, `active_role` | Integer 1; existing task ID; one of planner/implementer/verifier/reviewer |
| `plan` | `{ref, sha256}`: existing Markdown file/heading and owner-pinned full-file SHA-256 |
| `source_state` | Unmodified `verify.snapshot(root, approved_base)` result for the candidate under review |
| `acceptance_refs` | Nonempty, unique existing Markdown `#AC-...` references, scoped by the owner |
| `verification` | `{manifest, profile, features, run_id, context}`: existing runner inputs and expected native run; no second check list |
| `review` | `{implementation_session, separate_session_required}` from existing risk policy |
| `budget` | `{used, limit}`: nonnegative attempts consumed, positive maximum; strict integers |

The owner pins the candidate at each stable handoff. Legitimate implementation changes require
refreshing the candidate snapshot; plan/AC changes additionally require explicit plan reconciliation.
Do not refresh a context automatically in response to a mismatch. Dirty snapshots are supported
and labeled `workspace`, not verified commits. Clean release requirements remain with the existing
release/receipt consumer. No history/replay ledger or OS authority enforcement is added here.

### Role packet contract v1

Every packet has exactly `version`, `task_id`, `role`, `event`, `next_role`, `plan_sha256`,
`source_sha`, `workspace_sha256`, `session_id`, `adapter_ref`, `model_ref`, `summary`, `gaps`,
`plan_deviation`, `outputs`. Fields are mandatory; unknown fields/versions are rejected.
`model_ref` is null only for the native verifier; manual planner/implementer/reviewer adapters
may explicitly record `human`. `plan_deviation` is `none`, `within_contract` or `material`.
Version/hash/identity types are strict. `gaps` is empty only for a ready handoff.

| Ready role | Exact `outputs` fields |
|---|---|
| planner | `scope owner contracts steps consumers verification decisions`, each an existing file/symbol/heading reference |
| implementer | `changes wiring tests deviations`, each an existing reference |
| verifier | `receipt` (absolute path outside checkout), `observations` (existing reference) |
| reviewer | `receipt`, `acceptance`, `plan_fidelity`, `integration`, `structure` |

For review, `acceptance` contains exactly one `{ref, status, evidence_ref}` for each scoped AC.
The other three findings are `{status, evidence_ref}`. All statuses must be `pass` to hand off
as ready; otherwise use the appropriate failure event with `outputs: {finding: existing_ref}`.
All non-ready packets use that same one-field finding object. References use the existing
Python/Markdown/file resolver; arbitrary URLs, outside-root and symlink refs are not followed.
Keep review narratives in the external packet/task record; reference stable source/test/AC
locations already in the checkout. Do not alter verified source just to save a review note.
The native receipt itself stays external. Do not commit sensitive execution logs.

For verifier/reviewer ready events, the checker directly invokes the **existing read-only
receipt validator**, recomputes the selected check plan, and checks actual log bytes. A saved
JSON string saying VERIFIED_EVIDENCE is not accepted in place of the native receipt. Missing,
failed, timed-out or not-run checks, altered logs and NO_CHANGES_EVIDENCE cannot advance this flow.
The validator checks the same execution evidence again for reviewer readiness; it does not run
the tests again. Share the already produced receipt, not a second full suite.

### Trust limits

`HANDOFF_VALID` means the explicit contract is consistent, **not** that the planner is correct
or the review conclusions are true. Nonempty references prove navigation only; they cannot
prove completeness, source quality or user satisfaction. An incorrect plan still needs to be
caught by the independent AC/oracle review. The context issuer, session identity, counters,
model capability and receipt producer are not authenticated. A hostile owner of all inputs can
forge a consistent bundle. All outputs retain `dispatch_authorized=false`,
`merge_authorized=false`, `execution_attested=false`, `state_updated=false`.
These checks enforce a boundary only when an existing coordinator actually calls them.

## DF-H006: Task handoff to next-role proposal

Existing task snapshot + role packet → binding/reference/transition checks → native evidence
consumer when needed → structured proposal → existing coordinator decision. The checker reads
files/Git and emits stdout; it does not persist state or replace the owner. Blocked results and
missing work remain explicit. The task owner retains the bundle and proposed route in its
normal task/PR record. The original request, plan, ACs, actual diff and evidence travel together,
not just the previous agent's optimistic narrative.

## Use and local adoption

```sh
python -B tools/orchestration_contract.py --root . --context /absolute/task-context.json --handoff /absolute/role-handoff.json
```

Context/handoff files come from the operator's existing coordinator. A fully assembled synthetic
native-runner example is exercised by `tests/test_orchestration_contract.py`; it is **not** live
agent validation. No installation or dependency download is necessary. The repository's existing
`harness-contract` test discovery covers these tests; do not wrap them again under a second check
ID. Existing feature-map navigation includes this tool and the ACs below.

For local rollout, inspect the actual coordinator/registry/lease and permissions first. Connect
one real feature through its existing runner, preserve exit codes, and record the role/model
binding chosen. Add the checker at stable handoff boundaries, not after every edit. Final owner
handoff answers: requested outcome, actual usable result, where to inspect it, unverified work,
residual risks, and decisions needed. User-PC configuration and actual model dispatch are not
changed by merging this repository extension.

## AC-H020

Normal planner→implementer→verifier→reviewer→coordinator transitions validate. Missing required
plan/implementation references, wrong active role, skipped stage, unknown event/version or stale
plan/source bindings block. None of the routes grants dispatch/merge authority.

## AC-H021

Review must cover all original scoped ACs plus plan fidelity, real consumer integration and
structure. Missing ACs, not-run findings, unresolved gaps, material deviations or required
review-session separation violations cannot be represented as ready.

## AC-H022

Missing/failed/not-run native evidence, altered log bytes, wrong run identity and a no-change
receipt cannot advance verifier/reviewer readiness. A genuine native receipt is reused without
re-executing checks; source/evidence remain unchanged.

## AC-H023

Implementation, plan, environment, authority and output-format failures route to their specified
owners; budget exhaustion stops at the coordinator. JSON/model instructions are never executed.
Preserve existing runner behavior and evidence meaning. Live model capability/semantic review,
Windows, user-PC integration and actual product E2E require separate evidence when performed.
