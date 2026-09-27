# Skill: Review requirements and plan, not the implementer's confidence

- **Responsibility:** Compare the original outcome, plan, actual diff/wiring and execution evidence.
- **Input:** Original request/ACs, pinned plan, candidate source, native receipt and actual changes.
- **Output:** AC-level findings, plan fidelity, integration and structure findings; clear next owner.
- **Owner:** Reviewer; independent review depth follows the existing risk policy.
- **Failure:** A faithful implementation of a wrong plan is not a pass.

Read [ORCHESTRATION](../../docs/ORCHESTRATION.md) and
[verify-feature](verify-feature.md). Use a fresh session when the owner requires it. Another
session/model name is not proof of independence; keep the oracle independent of implementation.

1. Read the original request/ACs before the implementer's summary. Inspect the real source/diff.
2. Check each scoped AC, then plan fidelity, real entrypoint/consumer integration and structure.
   Look for duplicate pipelines, wrong owners, dead wiring and unintended side effects.
3. Inspect the native receipt/logs through the existing validator. A plan document, a test
   name, a saved green summary or a unit suite alone does not prove the product's real journey.
4. Return `implementation_gap` for code/wiring defects, `plan_gap` for incorrect/missing design,
   `environment_blocked` for unavailable evidence, and `authority_blocked` for required decisions.
   Give each finding a location, expected/observed behavior and smallest corrective scope.
5. Mark `ready` only when every original scoped AC and all three review dimensions have an
   evidence reference and `pass`, no unresolved gaps, and the native evidence checks out.
   Ready routes to the coordinator for a human-readable handoff, not merge approval.

Do not repair and call that same work independently reviewed. Do not turn stylistic preference
into an unnecessary architecture rewrite or extra review chain. Report what now works, where
it can be inspected, unverified work, residual risk and the specific owner decision needed.
