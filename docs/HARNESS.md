# Risk-proportional local harness

## Responsibility / Input / Output / Owner / Failure

- **Responsibility:** 한 기능을 완성하는 속도를 유지하면서 주장에 필요한 검증을 재현한다.
- **Input:** 명시한 Git base, 현재 checkout, 승인된 기능 지도·검사 명령, 비밀이 아닌 실행 context.
- **Output:** 선택 이유, 실행 명령·상태·소요시간·로그, `receipt.json`. 검증 증거이며 승인 아님.
- **Owner:** 기존 프로젝트/하네스 owner. agent authority와 lease는 기존 정본이 관리한다.
- **Failure:** 누락 설정은 BLOCKED, 실패/시간 초과는 FAIL, 실행 중 원천 변화는 STALE. 녹색으로 우회하지 않는다.

## BR-H001 / WF-H001: 하나의 의미 있는 작업

사용자 요청 → 관련 원본 탐색 → 한 기능/원인 단위 변경 → 영향 검증 → 한 번의 인계.
파일 수·시간·라인 수로 강제 분할하지 않는다. 분리는 독립 배포/rollback, 충돌하는 소유권,
선행 의존성 또는 사람이 검토할 수 없는 범위 때문에 필요할 때만 한다.
단순 수정은 짧은 작업 노트로, 보통 기능은 기존 SPEC/AC로 충분하다.
상태·증거·변경 이유는 기존 작업/PR 레코드에 링크한다. 두 번째 작업 관리 DB는 만들지 않는다.

## 검증 범위와 예산

| 단계 | 기본 | 확대 사유 |
|---|---|---|
| 구현 중 | 변경 함수/기능의 빠른 테스트 | 해당 실패가 상류·하류로 전파됨 |
| 안정된 인계 시점 | 공통 빠른 검사 + 영향 기능/실제 journey | 공유 계약·권한·금액·지속 데이터·의존성 영향 |
| full/통합 | 영향이 넓거나 미매핑, release/통합, 기존 의무 정책 | 명시한 사유가 있을 때만 |

한 번의 full에 포함된 focused 검사를 별도 의식처럼 다시 돌리지 않는다.
일반 작업은 안정된 시점의 통합 리뷰 한 번으로 묶고 추가 리뷰는 구체적인 위험에 배정한다.
코드/필수 입력이 바뀌면 영향 검사를 다시 실행한다. 승인된 기대값을 바꿔 통과시키지 않는다.

각 검사에 timeout을 둔다. 예산 부족은 NOT_RUN/불완전 증거이지 PASS가 아니다.
자동 재시도는 없다. 같은 실패가 반복되면 원인·환경·범위를 먼저 확인한다.
동일 check ID는 중복 제거한다. 다른 ID가 같은 무거운 명령을 감싸지 않게 manifest owner가 정리한다.
기존 verify.sh가 늘 full만 돌린다면 그 자체를 focused로 표시하지 않는다. 실제 선택 인자를 연결한다.

## Feature Map: 정본은 하나

기존 `feature_list`가 있다면 그 기능 ID를 재사용하고 아래 필드를 보완하거나 생성 뷰로 내보낸다.
별도의 수기 기능 목록, 상태표, 완료율을 병행 관리하지 않는다.

`id / symptoms / entrypoints / paths / journey / checks / failure_probe`

UI 기능의 entrypoint에는 실제 route·탭·안정 selector, 데이터 기능에는 공식 API/CLI와
입력 fixture/읽기 모델을 연결한다. journey는 사용자 증상을 재현할 경로이다.
check의 `argv`에는 그 경로를 실제 검증하는 기존 테스트/브라우저 wrapper를 연결한다.
지도에 문장만 써 두는 것은 실행 증거가 아니다. 등록하지 못한 검증은 명시적으로 미실행이다.

현재 `harness/verification.json`은 템플릿의 CLI 기능 한 개만 등록한다.
다른 제품의 route나 명령을 추측해 넣지 않는다. 실제 원본을 확인한 활성 기능부터 연결한다.
모든 과거 기능의 지도 완성을 도입 선행조건으로 삼지 않는다.

## CMP-H001: 선택기와 실행기

- **Responsibility:** `tools/verify.py`가 Git 변경을 수집하고 manifest의 check ID를 선택·실행한다.
- **Input:** schema_version 1 manifest; `--base`; 선택적 `--feature`, `--profile`, `--context`.
- **Output:** plan 또는 외부 디렉터리의 receipt/log.
- **Owner:** 하네스 owner; feature의 의미·명령은 제품 owner.
- **Depends on:** Python 표준 라이브러리, Git, manifest에 등록된 기존 실행 도구.
- **Must NOT:** 코드를 고치거나 commit/push/merge, 승인 대행, 외부 의존성 설치, LLM 호출.
- **Failure behavior:** 설정/명령 누락을 통과 처리하지 않고 재시도 없이 결과를 남긴다.

Manifest의 `checks`는 안전한 ID, argv 문자열 배열, 양수 `timeout_seconds`로 정의한다.
`profiles.docs/focused/full`은 비어 있지 않은 check ID 목록이다.
`docs_paths/risk_paths/features[].paths`는 리포 상대 POSIX 경로를 `fnmatch`로 비교한다.
여기서 `*`는 하위 디렉터리 `/`도 포함한다. Gitignore 문법/부정 패턴이 아니다.
권한·공유 스키마·DB migration·금액 계산·lockfile·검증정책의 실제 경로를 제품별 risk_paths에 넣는다.
문서 경로와 위험 경로가 겹치면 위험이 우선한다. 명시적 feature는 추가 검사이지 범위 축소가 아니다.
미매핑 비문서 파일은 full로 올리고 계획에 파일명을 표시한다. 매핑을 좁게 보완해 상시 full을 방지한다.

## DF-H001: 변경에서 실행 계획으로

Source = 현재 Git checkout. Input = base/head + staged/unstaged/untracked 경로.
Transformation = merge-base와 현재 작업 트리 차이(삭제/이름 변경의 양쪽 포함)를 기능과 위험에 연결.
Output = profile, 영향 기능, 위험/미매핑 경로, 중복 제거된 checks.
Persistence = --plan stdout 또는 receipt.plan. Consumer = CMP-H001 실행 단계.
Exception = base 불명·잘못된 manifest·하향 profile 요청이면 BLOCKED(exit 2).

## DF-H002: 실행에서 인계 증거로

Source = 계획과 승인된 명령. Input = argv + timeout + 비밀이 아닌 context.
Transformation = shell=False 실행, 첫 실패 뒤 나머지는 NOT_RUN, 로그/시간 기록, 실행 전후 원천 비교.
Output = PASS / FAIL / STALE / NO_CHANGES 및 각 검사 PASS/FAIL/TIMEOUT/ERROR/NOT_RUN.
Persistence = checkout 밖의 새/빈 output 디렉터리. Consumer = 기존 작업 기록·reviewer.
Exception = 실패/시간 초과/원천 변경은 exit 1, 출력 위치/설정 오류는 exit 2.
PLANNED_NOT_RUN은 계획만 만들었다는 뜻이며 검증 성공이 아니다.

receipt는 head/base/merge-base SHA, dirty 여부, staged/unstaged diff 및 untracked 내용 digest,
manifest digest, Python/platform, context, 실제 argv, 상태/시간/로그를 담는다.
check에서 `{python}`, `{base}`, `{head}`, `{output}`을 쓸 수 있다. base는 비교 merge-base SHA다.
깨끗한 SHA의 결과와 dirty 작업 트리 결과를 섞지 않는다. base 이후 통합 상태의 검증은 별도 의미다.

## 증거의 비용과 한계

재현 명령+기대/실제 출력+로그가 기본이다. UI 시각 변경만 캡처, 성능/메모리 주장만 trace/profile을 요구한다.
스크린샷·trace·로그에 고객정보/토큰이 들어갈 수 있으므로 기존 마스킹·보관·권한 정책을 따른다.
이 도구는 마스킹기나 sandbox, 독립 판정자, 위조 방지 attestation 시스템이 아니다.
manifest의 명령은 권한을 가진 코드로 취급하고 실행 전 검토한다. 문서상 권한 경계를 OS 수준에서 강제하지 않는다.
테스트 DB/자격증명 격리는 기존 하네스가 담당한다. 웹앱 시작/종료와 자식 프로세스 정리는 기존 wrapper가 소유한다.
timeout은 직접 실행한 프로세스에 적용되며 플랫폼별 전체 프로세스 트리 종료를 보장하지 않는다.

자동 증거 캐시/재사용은 구현하지 않는다. 동시 중복 작업 억제는 기존 lease가 담당한다.
수동 재사용도 원천/검사/환경/fixture가 같다는 근거가 있을 때만 가능하며 이전 결과임을 표시한다.
ignored 파일, 외부 DB/도구, submodule 내부 상태와 모든 환경변수를 완전 fingerprint하지 않는다.
context에 fixture·설정·런타임 버전을 기록하고 변경 시 관련 검사를 다시 실행한다. 비밀은 기록하지 않는다.

## 반복 실패를 작은 가드레일로

추측 진단 → 원본 entrypoint 찾기 / 검증 누락 → 지도와 선택기 검사 /
거짓 녹색 → 실행/미실행·원천 상태 분리처럼 실제 실패에 대응한다.
새 규칙은 근거, 차단 조건, 최소 반례, 담당자를 기존 스킬/정책 기록에 남긴다.
스킬/라우팅을 바꿀 때 그 실패 fixture만 먼저 재실행하고, 관련 사건이 있을 때 범위를 넓힌다.
모든 제품 PR에 모델 eval·독립 judge·전체 스킬 회귀를 요구하지 않는다.

## 완료 기준과 관찰

`tests/test_verify.py`가 선택·중복 제거·하향 거부·실패·시간 초과·원천 변경 계약을 검증한다.
자체 CLI의 plan/execute를 한 번 확인한 뒤 제품별 실제 journey 연결은 해당 리포에서 검증한다.
Linux 검증을 Windows/사용자 PC 검증으로 주장하지 않는다.
PR 개수 대신 완료 기능 lead time, 검증 대기시간, 재작업/누락 결함, 같은 입력의 중복 실행을 관찰한다.
목표 수치는 아직 실측하지 않았다. 새 대시보드/보고 의무 없이 기존 receipt와 작업 기록을 재사용한다.
