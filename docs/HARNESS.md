# Verification-first harness contract

- **Responsibility:** Connect symptom → feature → real entry point → acceptance criterion → executed check → evidence → counterexample.
- **Input:** Versioned map; existing verifier's receipt; caller-selected feature, run and revision.
- **Output:** Reproducible verification records and scoped gate results, not autonomous approvals.
- **Owner:** Existing repository maintainer/coordinator; product semantics remain with product owners.
- **Failure:** Missing, unavailable, stale or inconsistent evidence blocks completion.

## 1. Keep the existing owners

`feature_list`, agent registry/authority, work leases, `verify.sh` and eval fixtures remain canonical wherever they already exist. This template supplies a verification contract, not replacements for those systems. Export/extend the existing feature catalog into the versioned map, reusing its IDs; do not maintain two editable completion statuses. The supplied map covers only this repository's gate feature. It does not claim to enumerate another product's features.

Codex, Claude and other adapters consume the same map/receipt contract. A routing/review adapter may remain advisory while the existing coordinator controls execution. Do not interpret an adapter name, agent ID, valid receipt or independent-looking model output as authority. No agent hierarchy or model access is installed here.

## 2. Feature-map version 1

JSON object: `version: 1`, nonempty `features`. Unknown fields and duplicate keys are rejected. All features in a map must be fully specified; keep draft/inapplicable items in the existing catalog, not as partially valid entries that can silently pass.

| Feature field | Contract |
|---|---|
| `id`, `owner` | Stable catalog ID and accountable owner. |
| `symptoms` | Nonempty list of user-visible symptoms, including Korean aliases where useful. |
| `entrypoints` | Nonempty `{path, navigate}` list. Path must be an existing repository file; navigation describes screen/URL/selector or CLI steps. |
| `refs` | Nonempty `path#ID` list, with BR/WF/CMP/DF and AC IDs. Each ID must be defined as a Markdown heading in that file. |
| `checks` | Nonempty checks; at least one `positive` and one `negative`. |
| `catalog_ref` | Optional existing catalog file path; no duplicate status ownership. |

Every check has `id`, `kind`, `argv`, `expected`, `covers`, `evidence_types`. `argv` is a nonempty string array, **never executed by this gate**. `expected` states the discriminating oracle, not merely “exit 0”. `covers` contains registered AC IDs; all registered ACs must be covered. Kinds: `positive`, `negative`, `regression`, `architecture`, `eval`, `e2e`. Evidence types: `log`, `report`, `trace`, `screenshot`, `snapshot`. Require only relevant evidence; a backend parser does not need a screenshot or heap snapshot for every change.

For UI features, `navigate` should contain the actual route, accessible name/test selector, login role and fixture setup. For data/CLI/MCP features, give the real command/tool and official input route. Do not invent selectors or bypass official ingestion by directly seeding a test-only result table. The gate checks structural references, not UI selector correctness or command existence; product tests must do that.

## 3. Receipt version 1

The existing trusted runner creates the receipt after executing approved checks. It records, rather than invents, these exact fields:

| Field | Contract |
|---|---|
| `version` | Integer 1, not boolean. |
| `feature_id`, `run_id`, `commit_sha` | Exact caller-bound feature, unique coordinator-issued run ID and full 40/64-character lowercase revision. |
| `map_sha256` | SHA-256 of the complete map file bytes used for this run. |
| `producer` | `{agent_id, adapter}` for attribution; not authenticated identity. |
| `environment` | `{os, runtime}`; runner should include lockfile/tool/browser/build versions in its report artifact. |
| `started_at`, `finished_at` | ISO-8601 timezone-aware times, ordered and not in the future. |
| `results` | Exactly one result for every check in the selected feature, no extras. |

A result has `check_id`, exact `argv`, `status`, `exit_code`, `artifacts`. Each artifact has `path`, `sha256`, `type`. Paths must be under `artifacts/verification/<run_id>/`, repository-relative, regular files, not symlinks, and nonempty. Hashes must match file bytes. All declared evidence types must be present. Duplicate checks/artifact paths are rejected.

Only `status: passed` with an **integer** `exit_code: 0` qualifies. Report `failed`, `not_run` or `error` honestly; all block acceptance. A negative test normally exits zero when it correctly asserts that the product rejects invalid input. Product rejection is not the same as a failed test.

A combined suite log may cover multiple checks only when the runner genuinely ran their asserted cases; listing the same arbitrary log multiple times proves nothing. Record case-level report assertions where the product framework supports them. A screenshot hash does not verify its semantic content. The gate deliberately reports `execution_attested: false`.

## 4. CLI and meanings

Requires Python 3.10+; receipt mode also requires Git. No external Python packages.

```sh
python tools/verify_contract.py lint --root . --map verification/feature-map.json
python tools/verify_contract.py receipt --root . --map verification/feature-map.json \
  --feature verification-gate --run-id RUN_ID --commit-sha FULL_HEAD_SHA \
  --receipt artifacts/verification/RUN_ID/receipt.json
```

Substitute the actual run and full SHA; the placeholders above are not passing evidence. In PowerShell put the receipt command on one line or use PowerShell continuation, not `\`. Obtain the SHA from the trusted coordinator's checked-out revision, not by copying the receipt's claim.

| Result | Meaning |
|---|---|
| `map_valid`, exit 0 | Registered map structure/references are valid. No checks have been executed. |
| `evidence_valid`, exit 0 | One selected feature's evidence is internally consistent with the supplied bindings. |
| `blocked`, exit 1 | A validation, file, Git or decoding check failed. |
| exit 2 | CLI invocation error; never treat it as pass. |

`merge_authorized` and `execution_attested` are always false. Receipt CLI checks the actual repository root, matching HEAD, tracked map and clean worktree (including untracked files, except ignored artifacts). Use an isolated clean checkout for a release-bound receipt. Never commit customer logs just to make the tree clean. Lint can run in a development worktree; it is not release evidence. The library validator assumes its caller provides a validated map, actual map hash and trusted expected identities; use the CLI for workspace checks.

## 5. Trust and authorization are separate

Hashes establish byte consistency, **not who executed a test or whether its assertions are correct**. Anyone able to replace both a receipt and its log can fabricate mutually matching hashes. This first version has no signed attestation, trusted producer identity, replay ledger, automatic changed-feature discovery or adversarial-filesystem isolation. The coordinator must issue fresh run IDs, retain append-only evidence and verify the expected revision/environment. Reusing a caller-approved run ID is not detected by a global ledger here.

An isolated verifier must run a protected version of the gate and independent oracle. Merely giving two agents different names is not independent review. Do not let a candidate patch weaken the gate, remove a feature/AC/negative check or change expected results and then certify itself. Protect gate/map/oracle/CI changes through existing review policy. Branch protection, required checks and approval registries are not configured by this extension.

CI should run deterministic checks with least privileges and no customer secrets. The included workflow tests this harness and its map, not another product's E2E. GitHub recommends least-privilege tokens, immutable action SHA pins and avoiding privileged untrusted checkouts: <https://docs.github.com/en/actions/reference/security/secure-use> (consulted 2026-09-25). No automatic artifact upload is enabled; sanitize logs/traces before sharing because they may contain data, tokens, file paths or memory contents.

## 6. Failure-driven skills and measured scale

Use `verification/skills/verify-feature.md` for the observation → failure fixture → skill/gate change → held-out evaluation loop. The bundled Python tests are deterministic contract regressions, not live agent-quality evals. A model judge may supplement human or deterministic grading but cannot redefine the correct product outcome.

Scale only after the local pilot has reproducible evidence. Suggested **initial policy targets, not measured results**: required-check coverage 100%, zero critical false passes, zero unauthorized state transitions, successful independent rerun on at least five distinct changes. Track time-to-reproduce, defect escapes, false passes, flaky results and cost per accepted change; PR count alone is not a quality metric. Expansion sequence: one feature/one worker → independent verifier → bounded workers with existing nonoverlapping leases → cloud execution only after explicit permission and data review.
