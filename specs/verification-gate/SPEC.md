# Feature: Verification contract gate

## Business Requirement
`BR-900`

## Affected Workflow
`WF-900`

## Affected Data Flow
`DF-900`

## Affected Components
`CMP-900`

## Input
Version 1 feature map and optional version 1 receipt. Paths are repository-relative POSIX strings, including on Windows. Receipt mode additionally requires caller-supplied feature ID, unique run ID and full commit SHA; it verifies that HEAD matches and the workspace is clean. The map must be tracked. Detailed field definitions: `docs/HARNESS.md`.

## Output
JSON to stdout, exit 0 for `map_valid` or scoped `evidence_valid`, exit 1 for `blocked`, exit 2 for invalid CLI invocation. `merge_authorized` is always false. Evidence validation does not certify execution authenticity, semantic correctness, product completeness or readiness.

## Invariant
Read-only, no model/network calls, no execution of manifest commands, no approval/lease writes. Every registered feature has real source/navigation, BR/WF/CMP/DF/AC references, positive/negative checks and check-to-AC coverage. Every required check must have exactly one passing receipt result with matching argv, zero integer exit code and required nonempty hashed artifacts. Complete map digest, run ID, feature and revision must match.

## Exception
Reject duplicate JSON keys/IDs, unknown versions/fields, missing/invalid references, path traversal/symlinks, untracked maps, dirty or wrong revisions, incomplete check coverage, not-run/error/failed status, altered/empty/missing artifacts, reused run-path bindings and invalid timestamps. No exception is converted into a pass. Native OS execution failures are reported as blocked.

## Plan and tasks
1. Record BR/WF/CMP/DF and ADR before implementation.
2. Implement strict map/receipt validators and a read-only CLI.
3. Add independently assembled valid fixtures, invalid-input regressions and CLI subprocess tests.
4. Add the repository's own feature map and adapter-neutral verification skill.
5. Document staged local adoption and run the available checks; report unavailable product/Windows/LLM execution separately.
