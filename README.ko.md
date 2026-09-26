# Verifiable Dev Harness

**한국어** · [English](README.md)

> **AI 보조 개발을 위한 Verification-first 개발 하네스**  
> 추적 가능성, 재현 가능성, 사람의 통제권을 잃지 않으면서 개발 루프를 더 많이 자동화하는 것을 목표로 합니다.

AI 코딩 에이전트는 이미 코드를 빠르게 만들 수 있습니다. 더 어려운 문제는 그 다음입니다.

- 실제로 무엇이 바뀌었는가?
- 어떤 검증이 필요한가?
- 그 검증은 정말 실행됐는가?
- 결과를 뒷받침하는 증거는 무엇인가?
- 검증 통과가 어디까지의 권한을 의미하는가?

**Verifiable Dev Harness**는 이 문제를 다루기 위한 가벼운 repository-level harness입니다.

제품 의도, Feature Map, 위험 비례 검증, 실제 실행 가능한 검사, 실행 증거와 인계 구조를 연결해 사람과 코딩 에이전트가 같은 정본을 기준으로 작업하도록 합니다.

---

## 왜 만드는가

목표는 에이전트의 자율성을 최대화하는 것이 아닙니다.

목표는 다음과 같습니다.

> **결과를 설명하고, 재현하고, 반증할 수 있는 능력을 유지하면서 개발 자동화 범위를 최대한 넓히는 것.**

이를 위해 다섯 가지 원칙을 둡니다.

1. **올바른 경로가 가장 쉬운 경로가 되게 합니다.**  
   반복되는 제약을 프롬프트에 계속 적는 대신 아키텍처, 계약, lint, 실행 가능한 검사로 옮깁니다.

2. **보고가 아니라 동작을 검증합니다.**  
   “테스트했습니다”는 증거가 아닙니다. 실제 명령, 원천 상태, 환경, 결과, 로그를 남깁니다.

3. **위험에 비례해 검증합니다.**  
   변경에 필요한 최소한의 설득력 있는 검사를 실행하고, 공유 계약·권한·지속 데이터·계산·미매핑 영향이 있을 때 범위를 확대합니다.

4. **권한 경계를 분리합니다.**  
   검증 증거가 있다고 해서 merge, 배포, 업무 판단, 외부 행동 권한이 자동으로 생기지 않습니다.

5. **검증 자체를 다음 병목으로 만들지 않습니다.**  
   과도한 micro-slice, 중복 전체 회귀, 불필요한 reviewer chain, 신뢰를 높이지 않는 문서 작업을 피합니다.

---

## 개발 루프

```mermaid
flowchart LR
    A["의도<br/>PRODUCT / SPEC / AC"] --> B["Feature Map<br/>증상 → 진입점 → 검사"]
    B --> C["변경<br/>사람 또는 코딩 에이전트"]
    C --> D["영향 범위 선택<br/>docs / focused / full"]
    D --> E["검사 실행<br/>실제 명령"]
    E --> F["Evidence Receipt<br/>SHA · 환경 · 로그 · 상태"]
    F --> G["무결성 검증<br/>재계산 · 대조"]
    G --> H["기존 통제 경계<br/>검토 · merge · 배포"]
```

검증 통과는 **증거**이지 **승인**이 아닙니다.

---

## 포함된 구성

| 영역 | 역할 | 주요 진입점 |
|---|---|---|
| 개발 계약 | 권한, 정본, 작업 단위, 검증 원칙 | `AGENTS.md` |
| 제품 의도 | 문제, Actor, Business Requirement | `docs/PRODUCT.md` |
| 아키텍처 | 컴포넌트 책임과 경계 | `docs/ARCHITECTURE.md` |
| 데이터 흐름 | Source → 변환 → 저장 → Consumer lineage | `docs/DATA_FLOW.md` |
| 기능 계약 | 기능 동작과 Acceptance Criteria | `specs/` |
| 검증 정책 | 위험 비례 검증과 증거 의미 | `docs/HARNESS.md` |
| 기능 탐색 | 증상 → 기능 → 명세 → 소스 → 테스트 | `tools/feature_map.py` |
| 검증 실행기 | 필요한 검사 범위를 선택하고 실행 | `tools/verify.py` |
| 증거 무결성 | plan을 재계산하고 receipt/log 일관성 확인 | `tools/verify_receipt.py` |
| 실행형 journey | disposable 환경에서 실제 CLI 경로 재현 | `tools/harness_journey.py` |
| 로컬 도입 | 기존 registry/lease/runner를 보존하며 통합 | `docs/LOCAL_ADOPTION.md` |

이 저장소 자체도 파일럿 시스템으로 사용합니다. 현재 실행 가능한 Feature Map은 `harness/verification.json`에 있습니다.

---

## 1. 위험 비례 검증

실제 변경 범위에 따라 검증 profile을 선택합니다.

- **docs** — 문서 변경과 가벼운 구조 검사
- **focused** — 영향받는 기능의 검사와 실제 journey
- **full** — 공유/고위험·미매핑 변경, 통합/릴리스 필요, 또는 기존 필수 정책이 있는 경우

실행기는 계산된 최소 profile보다 낮게 임의로 축소하지 않습니다. 동일한 check ID도 중복 실행하지 않습니다.

```sh
# 계획만 확인 — 아직 검증을 실행한 것이 아님
python -B tools/verify.py --base origin/main --plan

# 선택된 검증을 한 번 실행
python -B tools/verify.py \
  --base origin/main \
  --output ../vdh-evidence/run-001 \
  --context local
```

`origin/main`은 예시입니다. 실제 환경에서는 승인된 비교 ref 또는 고정 commit을 사용합니다.

---

## 2. Feature Map: AI를 위한 제품 내비게이션

Feature Map은 두 번째 요구사항 DB가 아닙니다.

기존 제품 의도와 실제 구현을 연결해, 모호한 사용자 제보에서도 에이전트가 관련 소스와 검증 경로를 찾도록 돕습니다.

```text
사용자 증상
  ↓
기능
  ↓
SPEC / Acceptance Criteria
  ↓
실제 소스 진입점
  ↓
테스트 / journey / failure probe
```

예시:

```sh
python -B tools/feature_map.py lookup --query "검증 누락"
python -B tools/feature_map.py lint
```

현재 구현은 Python symbol과 Markdown Acceptance heading을 실제 파일에서 확인하되, 대상 코드를 import하거나 실행하지 않습니다.

파일·심볼·AC 참조가 깨지면 오래된 문서를 그대로 신뢰하는 대신 lint가 실패합니다.

Feature Map은 의도적으로 **탐색용이지 진단기가 아닙니다.** 관련 기능을 찾았다고 원인까지 증명되는 것은 아닙니다.

---

## 3. 실행 증거를 남기는 검증

실행기는 단순한 green/red 결과보다 실제 원천 상태와 실행 사실을 기록합니다.

Receipt에는 다음과 같은 정보가 포함될 수 있습니다.

- head / base / merge-base SHA
- dirty workspace 상태와 workspace digest
- 선택된 profile과 check
- 실제 argv
- 환경과 비밀이 아닌 context
- `PASS / FAIL / TIMEOUT / ERROR / NOT_RUN / STALE`
- 실행 시간
- 로그 경로, 크기, SHA-256
- run ID와 timestamps

하나의 검사가 실패하면 이후 검사는 `NOT_RUN`으로 남습니다. 자동 retry-to-green은 하지 않습니다.

증거는 source와 evidence가 뒤섞이지 않도록 checkout 밖에 저장합니다.

---

## 4. Receipt 무결성은 실행 인증이 아닙니다

`tools/verify_receipt.py`는 기대되는 원천 상태와 검사 plan을 다시 계산한 뒤 제출된 receipt·로그와 비교합니다.

다음과 같은 불일치를 차단할 수 있습니다.

- 오래됐거나 다른 원천 상태
- 누락·중복·예상 밖 검사
- 실행 명령 drift
- 변경·분실된 로그
- run/context/manifest 불일치
- FAIL/TIMEOUT/NOT_RUN을 성공으로 표현한 경우

하지만 **해시는 신원 인증이 아닙니다.**

로그와 receipt를 모두 통제할 수 있는 생산자는 서로 일치하는 데이터를 조작할 수 있습니다. 따라서 이 하네스는 cryptographic execution attestation을 제공한다고 주장하지 않습니다.

검증된 증거가 있다고 해서 다음이 자동으로 참이 되지는 않습니다.

```text
execution_attested = true
merge_authorized   = true
```

Trusted execution environment, 독립 검토, branch protection, 승인 정책은 별도의 통제입니다.

자세한 내용은 `docs/EVIDENCE_INTEGRITY.md`를 참고하세요.

---

## 5. 에이전트 수보다 먼저 Factory-ready 환경

여러 에이전트를 병렬로 늘리기 전에, 하나의 기능을 통제된 환경에서 재현하기 쉬워야 합니다.

```text
알려진 상태 준비
→ 실제 제품 경로 호출
→ 정상 사례 실행
→ 구별력 있는 실패 사례 실행
→ 관찰 가능한 결과 확인
→ 증거 수집
→ 자신이 만든 리소스만 정리
```

이 저장소는 `tools/harness_journey.py`를 통해 native CLI 파일럿을 제공합니다.

이는 하네스 자체를 검증하는 예시이며, 다른 제품의 UI나 업무 workflow가 맞다는 증거는 아닙니다.

웹앱이나 서비스 제품에서는 해당 제품이 이미 사용하는 browser, database, container, test environment를 재사용해 실제 입력 → 처리 → 출력 journey로 교체해야 합니다.

자세한 내용은 `docs/FACTORY_READY.md`를 참고하세요.

---

## 정본 구조

```text
PRODUCT
  ↓
ARCHITECTURE
  ↓
DATA_FLOW
  ↓
Feature SPEC / ACCEPTANCE
  ↓
source code + tests
  ↓
execution evidence
```

코드는 **현재 구현(AS-IS)** 을 보여줍니다.

승인된 PRODUCT/SPEC은 **의도된 동작**을 정의합니다.

둘이 다르면 차이를 드러내야 하며, 현재 코드를 근거로 기대 동작을 자동으로 덮어써서는 안 됩니다.

구조적 참조는 자동화할 수 있지만 의미와 정책의 소유권은 명시적으로 남아야 합니다.

---

## Rule / AI / Human의 역할 경계

이 프로젝트는 하나의 보편적인 운영 모델을 강제하지 않습니다. 대신 **task 단위의 역할과 권한 경계**를 명확히 하는 것을 지향합니다.

| 책임 | 일반적인 담당 |
|---|---|
| 결정론적 검증, invariant, 범위 선택, reconciliation | 코드 / 규칙 |
| 탐색, 구현, 테스트 실행, 후보 생성 | 코딩 에이전트 또는 개발자 |
| 모호한 판단, 정책 변경, 예외 | 사람 / 도메인 owner |
| merge, 배포, durable decision, 외부 행동 | 기존 승인 통제 |

LLM이 task를 수행한다고 해서 결정 권한까지 자동으로 갖는 것은 아닙니다.

반대로 결과 책임자가 사람이라고 해서 모든 단계를 수작업으로 수행해야 하는 것도 아닙니다.

---

## 빠른 시작

필요 환경:

- Python 3.10+
- Git
- core harness에는 외부 Python package가 필요하지 않음

```sh
# 1. Feature Map 참조 검사
python -B tools/feature_map.py lint

# 2. 어떤 검사가 선택될지 확인
python -B tools/verify.py --base origin/main --plan

# 3. 검증 실행
python -B tools/verify.py \
  --base origin/main \
  --feature harness-verification \
  --output ../vdh-evidence/run-001 \
  --context local

# 4. disposable native journey 직접 실행
python -B tools/harness_journey.py
```

Receipt 무결성 사용법은 `docs/EVIDENCE_INTEGRITY.md`를 참고하세요.

---

## 기존 저장소에 적용할 때

기존 개발 시스템 위에 이 하네스를 통째로 덮어쓰지 마세요.

먼저 다음의 기존 owner를 확인합니다.

- feature registry / product map
- agent registry / authority model
- work lease / concurrency control
- verification entry point
- test fixture / expected-result oracle
- CI / branch protection / review policy

그 다음 부족한 계약과 evidence path만 연결합니다.

이미 좋은 runner가 있다면 그대로 사용합니다. 기존 feature registry가 있다면 수기 정본을 하나 더 만들지 말고 확장하거나 생성 view로 내보냅니다.

자세한 내용은 `docs/LOCAL_ADOPTION.md`를 참고하세요.

---

## 의도적으로 하지 않는 것

이 프로젝트는 다음을 목표로 하지 않습니다.

- 자동 merge/deploy bot
- OS-level sandbox
- 범용 agent orchestrator
- 테스트 suite 자체가 의미적으로 옳다는 증명
- cryptographic execution attestation
- 제품별 E2E 검증의 대체
- 모든 변경의 전체 regression 강제
- 일반 PR마다 여러 LLM judge를 요구하는 운영

목표는 검증 자체를 다음 병목으로 만들지 않으면서 개발을 **더 관찰 가능하고, 재현 가능하고, 반증 가능하게** 만드는 것입니다.

---

## 저장소 구조

```text
.
├── AGENTS.md
├── docs/
│   ├── PRODUCT.md
│   ├── ARCHITECTURE.md
│   ├── DATA_FLOW.md
│   ├── HARNESS.md
│   ├── FACTORY_READY.md
│   ├── EVIDENCE_INTEGRITY.md
│   ├── LOCAL_ADOPTION.md
│   └── decisions/
├── harness/
│   ├── verification.json
│   ├── fixtures/
│   ├── skills/
│   └── examples/
├── specs/
│   ├── _template/
│   └── harness-verification/
├── tools/
│   ├── verify.py
│   ├── verify_receipt.py
│   ├── feature_map.py
│   └── harness_journey.py
└── tests/
```

---

## 앞으로의 방향

장기 방향은 단순합니다.

> **에이전트가 제품을 이해하고, 제한된 범위에서 변경하고, 실제 경로를 실행하고, 증거를 남기며, 최종 권한 경계는 명시적으로 사람과 기존 통제에 남기는 개발 시스템.**

다음 계층으로는 같은 정본에서 생성되는 **사람용 System / Process / Decision Map**을 고려하고 있습니다. 각 모듈과 workflow에서 rule-based task, AI-assisted task, human decision, 검증 상태를 시각화하되 새로운 수기 정본을 만들지 않는 방향입니다.

중요한 지표는 에이전트 수나 PR 개수가 아닙니다.

**설명하고, 재현하고, 반증할 수 있는 능력을 잃지 않으면서 개발 루프를 어디까지 자동화할 수 있는가**가 핵심입니다.
