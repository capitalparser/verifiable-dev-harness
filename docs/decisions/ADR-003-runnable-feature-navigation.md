# ADR-003: Runnable navigation using the existing map and runner

**Status:** Proposed. Main e4ba1922; independent of the open PR #2 (ADR-002 reserved).

## Context

The requested next step is not more receipt policy. It is source-grounded navigation,
an environment the agent can drive and mechanical boundaries, without micro-slices or
mandatory full regression for every change. This repository ships a developer CLI, not
a business web application; its native CLI is the only honest in-repository product pilot.

## Decision

Extend features[].navigation in the existing map, resolve current source/test references
with AST and intended-behavior heading references without executing or rewriting them.
Use a disposable native-CLI journey as one check in CMP-H001. Keep the existing runner
and receipt untouched. Enforce path/environment/owned-cleanup boundaries and verify real
CLI outcomes against fixed independent expectations. Treat lookup as candidate retrieval,
not a diagnosis. Return current locations/hashes on demand instead of a second generated map.

## Consequences

Python symbols/Markdown headings are machine-checked; other languages get file-level
navigation only. Semantic documentation drift still needs AC/journey checks. Temporary
workspaces and reduced environment exposure do not sandbox malicious code. The sample
is a native CLI E2E with synthetic inputs, not user-PC or accounting-app deployment.
No global agent settings, cloud automation, mandatory CI, model eval or authority expansion.

## Affects / rollback

CMP-H003/CMP-H004, DF-H004/DF-H005; BR-H002/WF-H002; AC-H010..H013.
Revert this one feature unit to remove navigation/journey wiring. Preserve existing
registry, leases, source data, logs and the PR #2 receipt extension if separately adopted.
