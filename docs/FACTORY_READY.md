# Factory-ready navigation and native CLI pilot

- **Responsibility:** 증상에서 실제 기능을 찾아 실행·관찰·정리할 수 있게 한다.
- **Input:** 기존 기능 지도, SPEC/AC, 현재 소스, 고정 합성 fixture.
- **Output:** 현재 위치·해시를 가진 탐색 결과와 실제 CLI 경로의 실행 보고서.
- **Owner:** 기존 harness owner. 기능 ID·선택기·receipt·권한·lease 정본은 바꾸지 않는다.
- **Failure:** 참조 파손·재현 실패·도구 부족·정리 실패는 미해결/실패로 남긴다.

## CMP-H003: Read-only feature navigation

`tools/feature_map.py`는 기존 `harness/verification.json`의 `features`를 읽는다.
`entrypoints`는 계속 정본이며 `navigation`에는 `spec`, `acceptance`, `tests`, `environment`
참조만 추가한다. acceptance 항목은 `{ref, checks}`로 정의한다. 해당 기능의 check 또는
선택 profile의 공통 check만 연결할 수 있다. 기능의 모든 check가 하나 이상의 AC에
연결돼 있어야 한다. 테스트/심볼 참조가 존재한다는 사실은 테스트 통과가 아니다.

Python `path.py:Class.method`는 AST로 위치를 찾고 실행/import하지 않는다.
다른 언어는 현재 파일 참조만 지원하며 심볼 분석을 지원한다고 주장하지 않는다.
Markdown `path.md#AC-H010`은 실제 ID heading을 찾으며 코드 블록 속 예시는 제외한다.
경로는 리포 상대 POSIX 표기이고, 외부/상위 경로·symlink는 거부한다.
`navigation`이 없는 과거 기능은 `unmapped_features`로 표시한다. 그 기능을 명시해서
검증하려 하면 차단하지만 모든 과거 기능의 이관을 파일럿의 선행조건으로 만들지 않는다.

매번 읽을 때 실제 줄 번호·소스 SHA-256을 계산하므로 별도 생성 파일/수기 상태표를
동기화하지 않는다. 삭제·이름 변경·깨진 AC 링크는 lint에서 실패한다. 같은 심볼 안의
의미가 바뀌었는지는 기계적 참조 검사만으로 알 수 없다. 그 차이는 기존 AC와 실제
journey가 확인하며, 자동화가 코드를 보고 기대 동작을 덮어쓰지 않는다.

`lookup`은 ID/증상/기존 journey의 단순 어휘 일치로 후보를 반환한다. 확률이나 원인
판정이 아니며 복수 후보·일치 없음은 그대로 표시한다. 해당 check 명령을 보여줄 뿐
실행하지 않는다. adapter가 현재 권한/lease를 확인한 후 기존 runner로 실행해야 한다.

## CMP-H004: Native journey adapter, not a second runner

`tools/harness_journey.py`는 기존 runner에 등록된 **하나의 check**다.
고정 `harness/fixtures/native-journey.json`을 새 임시 Git 저장소에 준비하고 현재
`tools/verify.py`를 복사하여 **공개 CLI**로 실행한다. alpha/beta는 하네스에 넣는
합성 입력일 뿐, 새 업무 앱이나 실제 결산 데이터가 아니다.

준비 -> --plan으로 readiness 확인 -> focused 정상 실행 -> 입력 reject에 대한 FAIL
확인 -> 위험 변경 하향 요청 BLOCKED 확인 -> 로그/receipt 관찰 -> owned temp 정리.
기대 상태·check ID·ALPHA_OK는 명세와 고정 probe에 명시하며 selector의 관측 출력으로
기대값을 만들지 않는다. 준비 자체가 실패하면 통과 보고하지 않는다.

작업공간·HOME·Git 설정·임시 경로를 분리하고 자식 환경은 실행에 필요한 OS 키만
허용한다. 고객 DB URL·토큰·임의 GIT/PYTHON 설정을 전달하지 않는다. 임의 manifest나
cleanup 디렉터리를 CLI 인자로 받지 않으며 복사/삭제는 생성한 temp 아래만 수행한다.
자식 명령은 제한 시간·shell=False로 실행한다. 파일 단위 격리/환경 allowlist는
OS sandbox가 아니므로 악성 후보 실행에는 기존 컨테이너/VDI 등 권한 격리가 필요하다.
정상 예외/timeout의 정리는 보장 범위지만 강제 종료·OS 장애·악성 자손 프로세스까지
복구하는 전역 janitor나 process supervisor는 도입하지 않는다.

## DF-H004 / DF-H005

DF-H004: 기존 feature/의도 참조 + 실제 소스 -> AST/heading 해석 -> 현재 탐색 JSON.
읽기 전용 stdout이며 영구 생성 지도·완료 상태를 저장하지 않는다.
DF-H005: 고정 fixture + native CLI 바이트 -> disposable 실행 -> 관측 report ->
기존 `harness-journey.log` 및 receipt. 보고서는 임시 경로를 정리하기 전에 로그와
receipt 내용을 포함한다. 해시/시간은 관측값이지 독립 실행 인증이나 성능 개선 주장 아님.

## 실행

```sh
python -B tools/feature_map.py lookup --query "검증 누락"
python -B tools/feature_map.py lint
python -B tools/harness_journey.py
python -B tools/verify.py --base origin/main --feature harness-verification --output ../rdc-evidence/factory-001 --context native-cli-pilot-v1
```

앞의 개별 명령은 탐색/개발용이다. 마지막 runner가 같은 check를 이미 포함했다면
안정된 상태에서 개별 검사와 full을 다시 연달아 돌리지 않는다. 비교 ref는 승인된
고정 SHA로 바꿀 수 있다. docs에는 빠른 참조 lint, full에는 단위 시험과 journey를
check ID당 한 번 연결했다. 사용자 제품의 모든 PR에 파일럿/모델 QA를 강제하지 않는다.

PR #2는 별도이며 이 PR은 main만으로 동작한다. 그 무결성 확장이 채택된 환경에서는
기존 `tools/verify_receipt.py`가 이 실행의 로그/receipt를 그대로 확인할 수 있다.
새 receipt 포맷, 자동 merge, CI 활성화, 모델 API 키, 권한/lease 설정은 추가하지 않는다.

## 실제 제품에 이식할 때

기존 `docs/LOCAL_ADOPTION.md`가 이관 정본이다. 기존 feature ID에 실제 SPEC/AC·라우터·
서비스·테스트 참조를 붙이고, 위 **native CLI pilot check**를 제품의 공식 입력→출력
journey wrapper로 교체한다. 이 파일럿 통과를 해당 제품의 E2E로 취급하지 않는다.
웹앱은 기존 도구로 ephemeral DB/포트/사용자 역할을 준비하고 health check 후 실제
브라우저/API로 확인한다. 필요할 때만 화면 캡처/trace를 수집하고, wrapper가 만든
리소스만 정리한다. 환경 관리가 이미 있으면 재사용하며 두 번째 runner를 만들지 않는다.

참조: Python 공식 subprocess, tempfile, ast 문서(2026-09-25 확인).
https://docs.python.org/3/library/subprocess.html
https://docs.python.org/3/library/tempfile.html
https://docs.python.org/3/library/ast.html
