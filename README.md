# Repository Development Contract

사람과 AI 코딩 에이전트가 같은 제품 의도·아키텍처·데이터 흐름을 참조하고,
**의미 있는 기능 단위로 구현 → 필요한 검증 → 증거 인계**까지 끝내기 위한 템플릿입니다.
문서 수, PR 수, 테스트 실행 횟수를 늘리는 것이 목적이 아닙니다.

## 운영 원칙

작은 PR은 “몇 줄짜리 PR”이 아니라 **독립적으로 확인하고 되돌릴 수 있는 변경**입니다.
기능에 필요한 화면·로직·배선·시험·문서는 한 작업으로 묶습니다.
단순 수정마다 SPEC/PLAN/TASK 파일이나 여러 리뷰어를 만들지 않습니다.

| 변경 | 작업 기록 | 기본 검증 |
|---|---|---|
| 문구·설명 문서 | 짧은 PR 설명 | 적용되는 문서/형식 검사 |
| 한 기능·버그 수정 | 기존 SPEC/AC 보완 또는 짧은 작업 노트 | 영향 테스트 + 해당 사용자 경로 |
| 공유 계약·권한·계산·마이그레이션 등 | 필요한 ADR와 영향 범위 | 관련 통합/회귀, 필요 시 full |

프로젝트의 기존 필수 통제는 유지합니다. 비용 때문에 필요한 검증을 생략하는 것이 아니라,
같은 검사를 반복하거나 관계없는 전체 회귀를 상시 실행하는 일을 줄입니다.

## 문서와 실행 도구

| 경로 | 역할 |
|---|---|
| `AGENTS.md` | 권한 경계, 작업 크기, 구현·검증 원칙의 짧은 진입점 |
| `docs/PRODUCT.md` | 문제, Actor, 성공지표, BR |
| `docs/ARCHITECTURE.md` | 컴포넌트 책임과 경계 |
| `docs/DATA_FLOW.md` | 입력부터 소비자까지 DF lineage |
| `specs/_template/` | 실질적인 기능의 SPEC/AC, 자잘한 수정에는 복제하지 않음 |
| `docs/HARNESS.md` | 검증 정책, 증거 계약, 경량 도구의 범위와 한계 |
| `docs/LOCAL_ADOPTION.md` | 기존 로컬 하네스 보존·연결 절차와 실행 프롬프트 |
| `harness/verification.json` | 이 리포 자체의 기능 지도와 검사 명령 |
| `tools/verify.py`, `tests/test_verify.py` | 선택 실행기와 작은 결정론적 계약 시험 |

PRODUCT/ARCHITECTURE/DATA_FLOW의 제품 영역은 채워 쓸 골격입니다.
빈 템플릿을 실제 제품 요구사항이나 현재 구현의 증거로 취급하지 않습니다.
기존 프로젝트에는 전체 문서를 덮어쓰지 말고 필요한 계약만 반영하세요.

## 로컬에서 실행

Python 3.10+와 Git이 필요하며 외부 Python 패키지는 없습니다. 리포 루트에서:

```sh
# 읽기 전용 계획: 아직 실행한 검증이 아님
python -B tools/verify.py --base origin/main --plan

# 실제 실행: 출력은 checkout 밖의 새 디렉터리
python -B tools/verify.py --base origin/main --output ../rdc-evidence/run-001 --context synthetic-v1

# 명시적인 특정 기능 검증(다른 변경의 검사 범위를 좁히지는 않음)
python -B tools/verify.py --base origin/main --feature harness-verification --output ../rdc-evidence/run-002
```

`origin/main`은 예시입니다. 실제 비교 ref를 지정하고 필요하면 먼저 fetch하세요.
실행기는 네트워크 fetch, branch 생성, push, merge를 하지 않습니다.
`--profile full`은 범위를 넓히며, 위험 판정을 `focused`로 낮출 수는 없습니다.
변경 없는 실행은 `NO_CHANGES`, `--plan`은 `PLANNED_NOT_RUN`으로 구분합니다.

선택 규칙: 문서만 변경 → docs / 기능 매핑 → focused / 위험 경로·미매핑 → full.
full은 공통 검사와 모든 등록 기능 검사를 합치며, 같은 check ID는 한 번만 실행합니다.
현재 manifest는 **이 템플릿 자체를 검증**합니다. 다른 제품에 그대로 복사해 통과시켜도
그 제품의 UI·결산·공시 정확도를 검증한 것이 아닙니다. 실제 검사 명령으로 연결해야 합니다.

## 기존 하네스에 가져오기

`feature_list`, agent registry/authority, lease, `verify.sh`, eval fixture가 있다면 그대로
정본을 유지합니다. 기능 지도는 기존 registry의 필드/생성 뷰로 연결하고 별도 정본을 만들지 않습니다.
이미 선택 실행기가 있다면 이 정책만 이식하고 두 번째 runner를 설치하지 않아도 됩니다.
새 프로젝트는 이 리포의 템플릿을 사용하거나 필요한 파일을 가져와 제품 문서를 채웁니다.

자동 병합, 무제한 병렬 에이전트, 모든 PR의 다중 모델 QA, GitHub Actions 의무화는 추가하지 않습니다.
