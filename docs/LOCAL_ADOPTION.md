# 기존 로컬 하네스에 적용

## Responsibility / Input / Output / Owner / Failure

- **Responsibility:** 기존 하네스의 정본·권한을 보존하면서 검증 경로와 비용 정책을 개선한다.
- **Input:** 실제 로컬 workspace와 적용할 이 리포의 정확한 commit.
- **Output:** 기존 파일의 최소 변경, 선택 실행 연결, 한 기능의 재현 가능한 receipt.
- **Owner:** 기존 로컬 coordinator/adapter의 승인된 역할. 역할을 재배정하지 않는다.
- **Failure:** 원본 경로·권한·실행 환경 미확인이면 그 부분을 미적용으로 남긴다. 추측 덮어쓰기 금지.

이 문서는 적용 절차이지 사용자 PC에 이미 설치했다는 기록이 아니다.
이 리포의 PR이 merge돼도 로컬 파일은 자동 갱신되지 않는다.

## 한 번의 도입 작업으로 묶기

실제 workspace에서 적용되는 AGENTS, feature_list, registry/authority, lease, verify.sh,
eval fixture 위치를 먼저 읽는다. 파일명이 다르면 실물을 따른다. 존재를 가정해 새 파일로 덮지 않는다.
현재 dirty 변경과 실행 중 lease를 보존하고 작업 브랜치/소유 범위 안에서 진행한다.

기존 스크립트가 선택 실행을 지원하면 정책·필드만 가져온다. 그렇지 않으면 `tools/verify.py`를
기존 진입점에서 호출하는 얇은 adapter로 연결하되 **기존 full 실행을 뒤에 또 붙이지 않는다**.
기존 verify.sh를 무조건 교체하거나 글로벌 Codex/Claude 설정, 승인 정책, MCP 키를 변경하지 않는다.
Windows에서 sh가 없으면 Python 진입점을 사용한다. 이번 템플릿의 Windows 실기 검증은 별도다.

기존 feature_list에 symptoms/entrypoints/journey/checks/failure_probe를 연결한다.
실행기 manifest가 필요하면 기존 정본에서 생성하거나 단일 소유 파일로 명시한다.
특정 제품의 paths/checks를 실제 코드·명령으로 바꾸며 이 템플릿의 self-test를 제품 테스트로 대체 사용하지 않는다.
중요 경로(승인·권한·계산·지속 데이터·의존성)는 기존 통제를 약화하지 않게 매핑한다.

활성 기능 하나에 재현 경로와 실패 반례를 연결하고 plan → 해당 실행 → 기존 작업 기록에 receipt 링크로 확인한다.
이 파일들을 따로따로 PR로 나누지 말고 하나의 도입 단위로 묶는다. 모든 제품·스킬의 재검증은 하지 않는다.

## 로컬 에이전트에 전달할 작업 지시

```text
이 리포의 docs/HARNESS.md 정책을 현재 로컬 하네스에 적용한다.
먼저 실제 workspace와 AGENTS/feature_list/registry/authority/lease/verify/eval 정본을 읽고
경로와 현재 adapter 권한을 확인하라. 기존 dirty 변경·lease·승인 경계를 보존한다.

한 개의 의미 있는 변경 단위로:
1. 기존 정책에서 불필요한 micro-slice와 상시 full/중복 리뷰 의무를 제거한다.
   단, 조직/프로젝트의 기존 필수 통제는 제거하거나 낮추지 않는다.
2. 활성 기능의 symptom -> entrypoint -> real journey -> check -> evidence를 기존 registry에 연결한다.
3. 기존 verify 진입점에 docs/focused/conditional full 선택을 연결한다.
   실행기는 하나만 유지하고 같은 check를 두 번 감싸서 실행하지 않는다.
4. 같은 기능의 정상 경로와 관련 실패 반례, 선택기 변경 테스트만 실행하고
   안정된 최종 상태의 검증을 한 번 수행한다. 전체 제품 회귀/모델 judge는 자동 추가하지 않는다.

실제 변경 파일·원천 상태·실행 명령·결과·미적용 사항·receipt 위치를 인계한다.
프로젝트 코드 수정/commit 권한이 없는 QA adapter라면 그 권한을 넘지 않는다.
자동 merge/deploy/외부 행동 및 durable 판단 승인선은 바꾸지 않는다.
```

## 실행 예시

POSIX와 PowerShell 모두 리포 루트에서 같은 Python 인자를 사용할 수 있다.
`origin/main`과 output 경로는 실제 승인된 비교 ref/새 경로로 바꾼다.

```text
python -B tools/verify.py --base origin/main --plan
python -B tools/verify.py --base origin/main --output ../rdc-evidence/local-001 --context fixture-v1
```

runner는 checkout 밖에 증거만 쓴다. output은 재사용 덮어쓰기를 거부한다.
되돌리기는 이 도입 diff만 revert하고 기존 진입점을 복원한다. 사용자 설정·데이터·증거는 삭제하지 않는다.
