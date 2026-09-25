# Native receipt integrity — 기존 하네스의 증거 확인

- **Responsibility:** 실행기가 남긴 증거가 현재 원천·선택 범위·로그와 맞는지 검사한다.
- **Input:** 기존 manifest/receipt, 호출자가 지정한 base/head/run/context, checkout 밖의 증거.
- **Output:** 범위가 명시된 증거 일관성 결과. 제품 정확성이나 실행자 인증, 승인이 아니다.
- **Owner:** 기존 하네스 owner. 선택/실행은 CMP-H001, 읽기 전용 검사는 CMP-H002가 맡는다.
- **Failure:** 미실행·실패·누락·오래된 원천·변조 증거는 BLOCKED. 정상화해 통과시키지 않는다.

## 1. 최신 main과 결합한 범위

작업 중 PR #1이 main `e4ba1922e2953afa797cdae72fed3a2b4319687c`에 병합되어, 그 위험 비례 하네스를 기준으로 통합했다. 기존 `AGENTS.md`, `docs/HARNESS.md`, `docs/LOCAL_ADOPTION.md`, `harness/verification.json`의 선택/권한/작업 단위 정책은 유지한다. 별도 feature-map, receipt 포맷, 선택 실행기, 완료 상태 registry는 만들지 않는다.

`tools/verify.py`가 기존 검사를 실행하고 기존 receipt에 무결성 필드를 추가한다. `tools/verify_receipt.py`는 같은 manifest와 선택기를 이용해 필요한 검사 목록을 다시 계산한 다음 증거를 읽기만 한다. **제품 검사를 다시 실행하지 않는다.** docs/focused/full 선택이나 full에 이미 포함된 검사를 중복 실행하는 정책을 추가하지 않는다.

## 2. 기존 receipt의 호환 확장

`schema_version: 1`과 기존 상태·plan·checks는 보존한다. 다음 필드만 추가한다.

| 필드 | 의미 |
|---|---|
| `evidence_contract_version: 1` | 이 무결성 확장의 버전. bool을 정수로 허용하지 않는다. |
| `run_id` | coordinator가 `--run-id`로 전달하거나 실행기가 새 UUID를 생성한다. |
| `finished_at` | 시간대가 있는 종료 시각. 시작 이후이며 검증 시각보다 미래일 수 없다. |
| `checks[].log_sha256` | 실제 실행 후 닫힌 로그를 스트리밍으로 읽어 산정한 SHA-256. |
| `checks[].log_bytes` | 같은 로그의 바이트 수. 실제로 실행하지 않은 NOT_RUN 항목에는 만들지 않는다. |

기존 `manifest_sha256`은 원문 파일 바이트가 아니라 `json.dumps(data, sort_keys=True)`의 SHA-256이다. 기존 계산법을 바꾸지 않았다. 원천 파일의 변경은 기존 snapshot도 함께 확인한다.

무결성 필드가 없는 과거 receipt는 열람할 수 있지만 새 checker의 통과 증거로 사용할 수 없다. 실제 검사를 다시 실행해야 하며 과거 로그에 임의 해시를 붙여 새 실행으로 취급하지 않는다.

**빈 로그는 그 자체로 실패가 아니다.** `git diff --check`처럼 성공 시 출력이 없는 검사가 있으므로, 기록된 크기·해시·정수 종료코드·선택된 검사 목록을 함께 검사한다. 화면·성능 주장은 기존 정책대로 별도 실제 journey/캡처/측정 결과가 필요하다.

## 3. 실행 및 확인

기존 실행기에서 한 번 실행한다. 아래 ref·경로·run ID는 실제 승인된 값으로 바꾼다.

```sh
python -B tools/verify.py --base origin/main --feature harness-verification --output ../rdc-evidence/run-001 --run-id run-001 --context synthetic-v1
python -B tools/verify_receipt.py --base origin/main --feature harness-verification --receipt ../rdc-evidence/run-001/receipt.json --expect-head FULL_HEAD_SHA --expect-run-id run-001 --context synthetic-v1
```

`FULL_HEAD_SHA`는 receipt 내용에서 복사하지 말고 신뢰하는 coordinator가 검사할 checkout에서 확인한다. 실행과 확인에 같은 base/profile/feature/context를 사용한다. 비교 ref를 고정 SHA로 지정하면 실행 사이 ref 이동을 피할 수 있다. 작업 중 dirty 상태는 허용하되 `binding=workspace`로 표시한다. 릴리스 등 깨끗한 커밋 증거가 필요한 소비자는 checker에 `--require-clean`을 붙인다. 모든 반복 개발 단계에 clean 상태를 강제하지 않는다.

PowerShell에서도 위 명령을 한 줄로 사용할 수 있다. 각 명령 뒤 `$LASTEXITCODE`를 확인하며 실패를 숨기지 않는다. 기존 wrapper에 연결할 때 실행기 실패/미실행 상태를 먼저 보존하고, 성공한 실행의 후속 읽기 전용 검사로 checker를 호출한다. 기존 검사를 checker로 대체하지 않는다.

| 결과 | 의미 |
|---|---|
| `VERIFIED_EVIDENCE`, exit 0 | 호출자가 선택한 검사 범위의 증거가 일관됨. |
| `NO_CHANGES_EVIDENCE`, exit 0 | 변경 없는 실행의 기록이며 기능 검증 완료가 아님. |
| `BLOCKED`, exit 1 | 원천/범위/실행 결과/로그/형식이 맞지 않음. |
| exit 2 | 잘못된 CLI 호출. 통과가 아님. |

checker는 같은 manifest에서 계획을 재계산하여 전체 선택 목록과 실행 순서/argv를 비교한다. receipt에 적힌 작은 검사 목록을 그대로 분모로 믿지 않는다. `NOT_RUN`, `FAIL`, `TIMEOUT`, `ERROR`, 중복/누락 검사, 상태가 다른 SHA, 다른 context/run, 변조·분실 로그, symlink 로그, 중복 JSON 키, bool 종료코드를 통과시키지 않는다. JSON 명령은 실행하지 않는다. CLI의 Git 읽기 호출은 상속된 `GIT_*` 재지정 환경변수를 사용하지 않는다.

## 4. 신뢰와 승인 경계

모든 checker 결과는 `execution_attested=false`, `merge_authorized=false`이다. 로그와 receipt를 함께 조작할 수 있는 생산자는 서로 맞는 해시를 만들 수 있다. 해시는 실행자 인증, 독립 판정, 서명된 attestation이나 제품의 의미적 정확성 보증이 아니다. gate/기대값 변경의 검토는 기존 위험 기준과 승인선을 따른다. 모든 일반 PR에 다중 모델 judge나 반복 리뷰를 요구하지 않는다.

새 run ID 기본 생성은 재사용 방지 원장이 아니다. coordinator-issued ID의 전역 유일성, lease, 원본 증거 보존, 외부 DB/ignored 파일/도구/fixture의 신뢰는 기존 owner가 관리한다. 완전한 환경 fingerprint, 적대적 파일시스템 격리, 프로세스 트리 정리는 이 확장의 범위가 아니다.

로그 자동 업로드나 고객정보 마스킹은 추가하지 않는다. 민감 데이터는 기존 보안·보관 정책을 따른다. CI 예제는 `harness/examples/github-actions-evidence.yml`에만 두며 `.github/workflows` 설치, required check, branch protection, 자동 머지는 활성화하지 않는다.

## 5. 실제 로컬 적용 작업

사용자 PC의 현재 feature_list/registry/lease/verify.sh 파일은 이번 작업에 제공되지 않았다. **사용자 PC 설정은 수정하지 않았다.** 기본 이관은 `docs/LOCAL_ADOPTION.md`가 정본이며, 이 절은 receipt 연결에만 해당한다.

기존 runner가 이 템플릿과 같은 경우 변경된 `tools/verify.py`와 checker를 함께 검토한다. 다른 runner라면 실제 schema와 exit 동작부터 읽고 필요한 필드/검사만 이식한다. 새로운 runner를 병행 설치하거나 AGENTS/CLAUDE/.codex 전역 파일을 덮어쓰지 않는다. 한 실제 기능에서 정상·현실적인 반례·미실행·오래된 증거·로그 변조를 시험하고 원래 사용자 결과까지 확인한다.

```text
현재 로컬 하네스의 실제 지침과 feature/authority/lease/verify 소유자를 먼저 확인한다.
기존 registry, 역할, dirty 파일, 승인선과 외부 행동 권한을 보존한다.
Repository-Development-Contract PR #2의 최종 커밋을 검토해 receipt 무결성 부분만 연결한다.
기존 선택 실행기를 유지하고 실행 결과에서 run ID·종료시각·로그 해시/크기를 산정한다.
호출자 기준의 base/head/run/context 및 재계산된 필수 목록으로 receipt를 확인한다.
실제 기능 하나의 공식 입력→처리→출력과 반례를 검증한다. 합성 테스트를 제품 E2E로 보고하지 않는다.
full에 포함된 검사를 중복 실행하지 않고, 부족한 fixture/자격증명은 NOT_RUN으로 남긴다.
변경 파일, 실제 명령·환경·기대/관측 결과, 증거 위치, 미실행, 권한 변화 없음, rollback을 보고한다.
새 권한 부여·자동 merge·durable 판단 변경은 하지 않는다. 필요 변경은 한 focused PR로 제출한다.
```
