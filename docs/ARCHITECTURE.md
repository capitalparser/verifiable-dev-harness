# Architecture

```mermaid
flowchart LR
    A[Source] --> B[Intake]
    B --> C[Process]
    C --> D[Store]
    D --> E[Consumer]
```

> 위 다이어그램은 골격입니다. 실제 컴포넌트 이름으로 교체하고, 아래 `## Components`에 각 노드를 `CMP-xxx`로 정의하세요.

## Components

### CMP-001: \<name\>

- **Responsibility:** (이 컴포넌트가 하는 일 — 한 가지로 명확하게)
- **Input:**
- **Output:**
- **Owner:**
- **Depends on:**
- **Must NOT:** (이 컴포넌트가 절대 하지 않아야 하는 일)
- **Failure behavior:** (실패 시 어떻게 동작하는가 — fail closed/open, 예외 전파 등)

<!-- 컴포넌트가 늘어나면 위 블록을 복사해 CMP-002, CMP-003 ... 순서로 추가하세요. -->

## Development tooling (not product runtime)

**CMP-H001: Verification planner/runner** — `tools/verify.py`.
Responsibility/input/output/owner/dependencies/failure boundaries are defined in
[HARNESS.md](HARNESS.md#cmp-h001-선택기와-실행기). It consumes the feature/check map,
executes existing commands and emits evidence only. It does not replace the local
agent registry, authority, lease, application runtime or merge control.

### CMP-H002: Receipt integrity validator

- **Responsibility:** Check the existing CMP-H001 receipt against a recomputed plan, source state and log bytes.
- **Input:** Existing manifest/receipt, caller-bound base/head/run/context and external evidence directory.
- **Output:** VERIFIED_EVIDENCE / NO_CHANGES_EVIDENCE / BLOCKED with commit-or-workspace scope; no approval.
- **Owner:** Existing harness owner; implementation in `tools/verify_receipt.py`.
- **Depends on:** CMP-H001 selection/snapshot/fingerprint functions, Python standard library and Git.
- **Must NOT:** Execute manifest checks, invent a second feature/lease/authority registry, merge, deploy or promote durable judgments.
- **Failure behavior:** Missing integrity metadata, inconsistent plan/source/checks/logs or invalid types block. Old receipts require a real rerun, not invented hashes.
- **Trust boundary:** Byte consistency is not execution attestation. Detailed contract and local integration: [EVIDENCE_INTEGRITY.md](EVIDENCE_INTEGRITY.md).
