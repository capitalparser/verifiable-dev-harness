# Acceptance: Runnable harness navigation

## AC-H010: Current navigation without changing intent

Given a registered feature, lookup returns its candidate ID, SPEC/AC references, actual
source/test lines and content hashes. Missing files/symbols/headings or invalid AC/check
bindings block. Line movement is reflected on the next read; intended behavior is never
rewritten. Empty/no-match queries remain unresolved and multiple matches remain candidates.

## AC-H011: Real native CLI journey

Given an isolated repository with fixed synthetic alpha/beta inputs, public --plan reports
PLANNED_NOT_RUN, focused execution selects exactly smoke and alpha once (not beta), and
its receipt/log contains the observed result ALPHA_OK. The adapter does not use select()
or execute() to manufacture expected results. Commands, times and actual stdout/stderr,
receipts and logs are retained in the structured report captured by the existing runner.

## AC-H012: Discriminating failure cases

Given alpha input reject, the native run returns exit 1 / FAIL with an actual failed check.
Given a changed risk path and requested focused profile, it returns exit 2 / BLOCKED before
creating output. Failed or unavailable steps cannot yield JOURNEY_PASS. Cleanup runs on
ordinary exceptions and timeouts, removes only adapter-owned temporary state and reports
failure rather than an invented successful teardown.

## AC-H013: Guardrails and proportional scope

Navigation parses references without importing mapped code, writing files or executing
commands. Traversal and symlink references are rejected. The pilot copies only its fixed
fixture inputs and the current native CLI, forwards no arbitrary environment keys and
never accepts an external cleanup target. Documentation changes run the small reference
lint; full uses the original unit suite and the pilot once, with check ID deduplication.
The native CLI/receipt contract and PR #2 integrity-consumer compatibility are preserved.

## Evidence and limits

This is the real developer-tool CLI exercised with synthetic input repositories, not an
accounting application, browser journey or user-PC deployment. No live model eval, Windows
execution or performance improvement is claimed unless separately executed. Timings are
observations, not a benchmark. Evidence consistency and acceptance never authorize merge.
