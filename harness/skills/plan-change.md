# Skill: Plan a bounded change

- **Responsibility:** Remove material guessing from implementation, not prescribe every line.
- **Input:** Original request, existing feature map, approved scope, actual source/consumers, ACs.
- **Output:** Version-bound plan in the existing SPEC/work record and role packet.
- **Owner:** Planner; the existing coordinator owns permissions and stage transitions.
- **Failure:** Unresolved business/security/authority decisions stay explicit; do not guess them.

Read [ORCHESTRATION](../../docs/ORCHESTRATION.md) and applicable instructions first.

1. Locate the canonical implementation through the feature map. Read real entrypoints,
   consumers and nearby tests before naming a cause. Separate observed facts from assumptions.
2. State user outcome and exclusions, reuse/extend decision, contracts, invariants, failure
   behavior, proposed implementation, real wiring, and independently defined normal/negative ACs.
3. Choose risk-proportional checks using the existing policy. Do not invent a parallel runner,
   owner, oracle or approval process. Do not require full regression on every edit.
4. Leave reversible internal choices autonomous. Keep material unknowns in `gaps`; use
   `authority_blocked` for decisions outside the current mandate or `environment_blocked`
   for unavailable sources/tools. Continue incomplete planning within the existing task;
   do not emit ready or invent a transition to bypass unresolved questions.
5. Link plan outputs `scope owner contracts steps consumers verification decisions` to actual
   record headings. A nonempty heading is not proof of a good plan; inspect its content.
6. Ask the existing owner to pin the full plan-file digest and candidate snapshot. Do not
   derive the trusted context by copying a worker's claimed hashes. Ready routes to implementer.

For a small fix one existing work-note section is enough. Do not create a new PLAN/TASK file,
PR or approval for each field above. No provider/model name is hardcoded into this skill.
