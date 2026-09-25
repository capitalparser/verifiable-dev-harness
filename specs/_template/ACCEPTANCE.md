# Acceptance Criteria: <feature name>

## AC-001: 실제 사용자/소비자 경로

Given (공식 입력·fixture·전제) — When (실제 UI/API/CLI 경로) — Then (기대 결과)

기존 기능 ID / 재현 명령 또는 journey:

## AC-002: 관련 실패 또는 불변조건

Given — When — Then (거부/보류/복구 등 실패 시 기대 동작)

보고된 버그의 원인이 entity/period/source 차원에 있으면 해당 차원을 바꾼 반례를 포함합니다.
관계없는 조합을 전수 생성하지 않습니다.

## Evidence / handoff

- 검증한 SHA와 dirty 여부 / fixture·환경 식별:
- 선택 profile과 확대/제외 이유:
- 실행 명령·실제 결과·receipt 위치:
- 미실행 검증 / 잔여 위험 / 다음 행동:

<!-- UI 시각 주장만 캡처, 성능·메모리 주장만 trace/profile. 모든 산출물을 일괄 요구하지 않습니다.
여기 정의한 필수 AC가 미실행이면 완료로 표시하지 않습니다. 계획은 실행 증거가 아닙니다. -->
