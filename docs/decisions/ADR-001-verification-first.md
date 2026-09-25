# ADR-001: Verification-first development extension

**Status:** Proposed (pending maintainer review; no authority expansion)

## Context

The current repository is a document-first template. It has no executable verification gate. The user requested that local-first verification, feature navigation, failure-driven skills and mechanical checks be incorporated without replacing existing local orchestration.

## Decision

Add an optional, standard-library, read-only verification contract gate. Keep approved PRODUCT/ARCHITECTURE/DATA_FLOW/SPEC intent and the current ID convention. Separate map validity, evidence consistency, independent product verification and human authorization. Bind each receipt to caller-supplied feature/run/commit and the complete map digest. Require every registered check, including a discriminating negative case. Do not execute arbitrary commands from the map.

Existing feature lists, authority registries, work leases, verify scripts and eval owners remain canonical. Codex/Claude/other adapters may consume the same contract; this change grants none of them new powers. Dune-specific useEffect/comment bans and unverified PR-volume anecdotes are not universal policies.

## Consequences

The gate can reject missing checks, stale bindings and altered evidence deterministically. It does not prove a command actually ran, judge screenshot semantics, discover every product feature, authenticate agent identities or make an LLM judge independent. Trusted execution and protected review remain integration requirements. JSON metadata creates maintenance overhead, so extend an existing catalog through an adapter rather than duplicating it. Real local product integration is separate because the user's current workspace files are not available here.

## Affects

- Architecture: `CMP-900`
- Data Flow: `DF-900`
