# Local harness adoption — preserve, connect, verify

- **Responsibility:** Apply the extension to the actual local workspace without replacing its owners.
- **Input:** Reviewed template revision and inspected local configuration.
- **Output:** One bounded pilot, executable integration, evidence and rollback instructions.
- **Owner:** Local coordinator and existing harness maintainer.
- **Failure:** Unavailable configuration or permission remains blocked; do not guess paths or claim local deployment.

## Current evidence boundary

The template repository was inspected at main `09b9a841f4fd074d68d5a4430ddf0f4f7b46bafe`. It originally contained eight Markdown files and no executable harness. The user's actual PC workspace, feature-list schema, authority/lease implementation and `verify.sh` were not mounted for this change. Accordingly, this document is a handoff for real local integration, not an assertion that it has happened. No `.codex` global configuration, user registry, durable judgment state or local project is modified by this repository change.

## 1. Inspect before adapting

Record the real workspace root, Git revision and dirty files. Read applicable organization/runtime/repository instructions in their actual order. Locate the canonical feature catalog, agent registry, authority checks, lease owner, verification runner and eval fixtures by reading their definitions and consumers; record “not found” rather than making up a new component. Distinguish the development harness from a product's accounting/judgment runtime. The development harness must not reimplement calculation or approval logic.

| Existing owner | Add only |
|---|---|
| `feature_list` or equivalent | Stable feature-ID reference plus verification metadata, or a deterministic export into the map. No second editable done-status. |
| Agent registry/authority | References to existing identity/role decisions; do not grant new write/merge powers. |
| Work leases | Acquire/validate through the existing owner. Bind source revision; do not invent a second lock mechanism. |
| `verify.sh` or equivalent | Existing approved checks stay authoritative. Append a receipt emitter and invoke the read-only gate after checks. Preserve nonzero exits. |
| Eval fixtures | Add observed failure scenarios, fixed expected outcomes and held-out cases. Do not replace the existing oracle. |
| Product tests | Use official input/ingestion/navigation/output paths and actual user acceptance; synthetic contract tests are supplementary. |

Prefer a pinned vendor copy of the two gate modules or another existing approved distribution method. Review the update diff and record its origin SHA; do not curl-and-execute a moving main branch. Do not overwrite `AGENTS.md`, `CLAUDE.md`, global skills, `.codex/config.toml` or existing Git sync rules. No new model access or API key is required.

## 2. Select one real feature

Choose one active, safe-to-run feature with a visible result: for example package upload → validation → issue display, only if that route actually exists in the selected workspace. Record the exact route/CLI, actor role, accessible selectors, source owner, required input fixture, output assertion and discriminating negative case. For accounting workflows, use an independent expected-result oracle; never force a match to disclosed totals by injecting a test-only local adapter.

Export its existing catalog ID into the map. Decide which evidence is necessary. A wrong-header rejection should capture validation output; a UI-flow defect should additionally capture relevant browser trace/screenshots; a latency claim needs a measured timing method. Missing fixtures/credentials are `not_run`, not success.

## 3. Execute through the existing runner

Before execution, obtain the current lease and approved scope, issue a fresh run ID, pin the revision, verify a clean isolated worktree and record tool/lockfile/fixture versions. Run the existing commands with bounded timeouts and ordinary sandbox restrictions. Capture stdout/stderr and structured assertions without leaking customer data. Populate the receipt from actual process results, never from the model's narrative. The negative test must fail when the plausible wrong implementation is intentionally substituted.

Add the gate as the final **additional** check; do not replace product tests with it:

```sh
# Within the existing POSIX verifier, preserve each preceding command's status.
python tools/verify_contract.py receipt --root "$REPO_ROOT" --map "$MAP_PATH" \
  --feature "$FEATURE_ID" --run-id "$RUN_ID" --commit-sha "$EXPECTED_SHA" \
  --receipt "$RECEIPT_PATH"
status=$?
exit "$status"
```

```powershell
# Within the existing PowerShell verifier; values come from the coordinator.
python tools/verify_contract.py receipt --root $RepoRoot --map $MapPath --feature $FeatureId --run-id $RunId --commit-sha $ExpectedSha --receipt $ReceiptPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

These are integration fragments, not installers or claims of a configured emitter. Ensure the existing runner continues reporting all failed/not-run results and does not hide failures with `|| true`, unconditional exit 0 or a final successful echo. Any wrapper/model adapter receives the same evidence contract, not permission to reroute around a failure.

## 4. Independent verification and rollout

The separate verifier checks the exact candidate SHA, the approved map/oracle revision and actual case assertions. Inspect a full positive path plus malformed input, duplicate request, stale state, interrupted run or unauthorized action as appropriate. Evaluate the real UI/output, not only backend unit tests. Protect source/map/oracle changes from self-certification. Passing a gate may advance an existing verification state only through its current owner; it cannot approve a business judgment, close a review or merge a PR.

Run one pilot before parallel workers. Require the proposed quality thresholds in `HARNESS.md` to be met on actual local runs, then enlarge only the worker count already permitted by leases and authority. Do not change cloud access, sandbox permissions or external-action approval policy as part of this rollout.

## 5. Rollback

Make one focused integration commit/PR. Record the baseline runner command and its exit behavior before changes. Roll back only the added gate/emitter wiring and verification metadata by the normal review process; retain evidence for diagnosis. Do not delete leases, reset dirty worktrees or restore an entire global configuration directory. A gate failure is a reason to investigate, not to silently disable enforcement.

## Copy-ready task for the local coordinator

```text
Use the reviewed Repository-Development-Contract verification-first extension.
Do not assume the current directory, feature_list/registry/lease schema or verify.sh path.
Read the applicable safety/workspace/repository instructions and inspect actual owners first.
Preserve all dirty files, canonical ownership, current approvals, durable judgment state,
Codex/Claude adapter permissions and external-action boundaries. Do not merge.

Integrate only one actual product feature. Reuse the canonical feature ID and export its
symptom → screen/CLI → source → BR/WF/CMP/DF/AC → check → evidence → counterexample route.
Keep the original product verifier. Add a receipt emitter based on real process results,
then call the read-only receipt gate on the exact clean candidate revision and fresh run ID.
Keep failed/not_run/error distinct; never fabricate a receipt or weaken the product oracle.
Do not introduce a second feature-status, agent-authority or lease registry.

Add and run normal, malformed, stale/missing-evidence, duplicate and unauthorized-action
cases that fit this feature. Verify the public product entry point and observable output.
Make a separate verifier rerun the same revision. Submit one focused PR without merging.
Report exact changed files, head SHA, commands/environment, logs/trace/captures, expected
versus actual outcomes, NOT RUN work, approval effects (must be none), and rollback steps.
The template's synthetic harness test pass is not proof that this product feature works.
```
