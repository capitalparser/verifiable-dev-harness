# Skill: Implement the pinned plan

- **Responsibility:** Deliver the user outcome through the actual public/consumer path.
- **Input:** Original request/ACs, pinned plan, permitted scope, existing source and owner context.
- **Output:** Code, wiring, relevant tests/docs, deviations and implementation handoff references.
- **Owner:** Implementer; existing coordinator retains write lease and authority decisions.
- **Failure:** Do not rewrite expected results, hide missing work or silently change the plan.

Read [ORCHESTRATION](../../docs/ORCHESTRATION.md) and applicable instructions first.

1. Confirm the plan version, candidate source and current write scope with the existing owner.
   Reuse the canonical implementation. Preserve unrelated dirty files and leases.
2. Implement a coherent feature/fix including input, transformation, persistence/return and
   real consumers. A helper function with no caller is not a finished user capability.
3. Run relevant tests during iteration. At stable handoff use the selected native check set
   once; do not attach repeated full/focused suites on identical inputs.
4. Internal reversible choices may be recorded as `within_contract`. Material changes to
   outcome/contracts/calculations/ownership/authority require `plan_gap` or `authority_blocked`,
   not a silent reinterpretation. Tool/fixture/credential problems are `environment_blocked`.
5. Link `changes wiring tests deviations` to actual source/test/work-record references and
   list missing work in `gaps`. Do not claim a test ran just because its source exists.
6. Have the owner pin the new candidate snapshot, preserving the agreed plan identity. Ready
   routes to the native verifier, never directly to review/merge/deploy.

Do not edit the trusted owner context, acceptance oracle or native receipt to make this step
pass. The stage contract does not grant write permission or automatically dispatch a model.
