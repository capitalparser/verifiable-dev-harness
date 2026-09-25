# Acceptance Criteria: Verification contract gate

## AC-900
Given a valid map with real source paths and defined BR/WF/CMP/DF/AC references, lint reports `map_valid` only. Missing navigation, broken references, duplicate IDs, missing positive/negative cases or unmapped acceptance criteria are blocked.

## AC-901
Given caller-bound feature/run/commit and matching map bytes, a complete receipt with passing checks, exact argv, integer zero exit codes, valid timestamps and nonempty matching SHA-256 artifacts reports scoped `evidence_valid`. Omitted, duplicate, failed, not-run or extra results are blocked.

## AC-902
Given stale bindings, altered/empty/missing evidence, invalid JSON/types, outside-root paths or symlinks, verification blocks. The gate never executes a command read from JSON. Receipt CLI also blocks dirty/wrong worktrees and untracked maps.

## AC-903
Given any result, no merge/approval/authority is granted or persisted. Regression tests and a real CLI invocation exercise the public entry point. Product E2E, Windows execution and model-based skill evals are reported separately unless actually run.
