# Feature: Runnable navigation for harness-verification

## BR-H002

A contributor receiving a vague verification bug report can find the existing feature,
read its intended behavior, resolve real source/test locations and reproduce the native
CLI journey in a disposable workspace without a new runner or authority registry.

## WF-H002

Symptom -> candidate feature IDs -> SPEC/AC and actual source -> approved check ID ->
prepare isolated fixture -> public CLI plan/execute -> observe normal and failure results
-> remove only owned temporary state -> existing receipt/log handoff.

## Affected components and flows

CMP-H001 remains the selection/execution owner. CMP-H003 (navigation) and CMP-H004
(journey adapter), DF-H004/DF-H005 are defined in docs/FACTORY_READY.md. No product
runtime, agent registry, lease, global configuration, approval or merge policy changes.

## Input / output

Input: the existing harness/verification.json plus optional features[].navigation;
repository-relative Python/file and Markdown heading references; sanitized symptom query.
Output: read-only current line/hash navigation and a structured native-CLI journey report.
The existing runner captures the report in its normal check log and receipt.

## Invariants / exceptions

Intended behavior remains in this SPEC and ACCEPTANCE, not generated from implementation.
No second feature map, automatic rewrite of expectations, arbitrary command execution from
lookup, or duplicate full/focused runs. Missing adopted refs block. Unadopted features are
explicitly listed as unmapped. Ambiguous or unmatched queries are not diagnosed bugs.
The pilot operates only in its newly created temporary directory, forwards an allowlisted
environment and calls the real tools/verify.py entrypoint. This is scoped test isolation,
NOT a security sandbox against malicious Python/native commands. Existing OS controls apply.

## Plan

Extend the existing feature metadata and add AST/heading reference resolution. Add one
native-CLI lifecycle adapter with independently specified outcomes and fixed synthetic
inputs. Wire these checks into the existing selector, test the changed contracts once at
handoff, and expose adoption instructions without installing user-PC or cloud settings.
