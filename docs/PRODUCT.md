# Product

## Business Hypothesis

> 시장 검증형 제품이면 가설/검증을 채우세요. 내부 도구나 사내 프로젝트라면 이 섹션을 "왜 필요한가 / 누가 요청했는가"로 대체해도 됩니다.

**H-001**
(가설을 한 문장으로 — 누가 어떤 문제를 반복적으로 겪는가)

**Validation**
(무엇을 근거로 검증했는가 — 인터뷰, 데이터, 기존 요청 이력 등. 근거가 없다면 "미검증"이라고 명시)

## Problem

(해결하려는 문제를 구체적으로 서술)

## Actors

| Actor | Goal | Pain today |
|---|---|---|
| | | |

## Success Metrics

| Metric | Target | How measured |
|---|---|---|
| | | |

## Business Requirements

### BR-001

- **Statement:** (무엇을 만족해야 하는가)
- **Rationale:** (왜 필요한가 — H-001 또는 실제 사례와 연결)
- **Affects:** (관련 `WF-xxx`, `CMP-xxx`)

<!-- 요구사항이 늘어나면 BR-002, BR-003 ... 순서로 추가하세요. -->

## Shipped development-tooling requirement (optional for adopters)

The 900-series IDs below describe this template's verification extension, not an adopter's business domain. Preserve existing product IDs when adopting it.

### BR-900

- **Statement:** A feature verification claim must connect a user symptom, real entry point, acceptance criteria, positive/negative checks and inspectable evidence for one immutable revision.
- **Rationale:** Requested local-first harness improvement; no claim of measured productivity gains or externally verified talk statistics.
- **Affects:** `WF-900`, `CMP-900`.

### WF-900

Observe symptom → locate canonical feature and source → execute approved checks in an isolated workspace → collect evidence → validate receipt → independent review → separately authorized decision. A valid receipt never grants merge, deployment or durable-decision authority.
