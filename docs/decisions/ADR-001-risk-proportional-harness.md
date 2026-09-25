# ADR-001: Risk-proportional verification without micro-slicing

- **Status:** Proposed for repository/local adoption; implementation supplied in the same PR.
- **Request:** 2026-09-25 사용자 요청. 검증 가능성은 높이되 과도한 slice/회귀/QA 병목은 피한다.
- **Scope:** 개발 지원 도구. 제품 runtime, agent authority, merge/deploy 정책은 변경하지 않는다.

## Decision

의미 있는 기능 단위를 기본으로 하고, 짧은 AGENTS에서 상세 검증 정책으로 연결한다.
기존 registry/lease/verify 진입점은 정본을 유지한다. 별도 orchestration 계층은 만들지 않는다.
템플릿에는 하나의 stdlib 선택 실행기와 실제 자기검증 manifest를 제공한다.
변경 경로별 docs/focused/full을 선택하고 검증 증거를 남긴다. full은 조건부이며 중복 check는 한 번만 실행한다.
역할 확대·자동 병합·항상 켜진 다중 모델 eval·모든 수정의 전체 회귀는 도입하지 않는다.

## Consequences / tradeoffs

선택 정확도는 제품별 매핑 품질에 의존한다. 미매핑은 full로 승격해 누락을 숨기지 않는다.
명령 실행 권한·격리·브라우저 lifecycle은 기존 하네스가 소유한다. 이 실행기는 sandbox가 아니다.
정확한 영향 폐쇄를 증명하지 못한 증거 cache는 넣지 않는다. 먼저 중복 없는 한 번의 실행을 구현한다.
현재 제품용 템플릿 문서는 그대로 유지하고, 개발 도구의 CMP-H001/DF-H001/DF-H002만 별도 명시한다.

## Verification / rollback

선택, 중복 제거, 미매핑, 하향 거부, 실패/시간 초과, dirty/변경 원천을 작은 합성 시험으로 확인한다.
실제 로컬 도입은 한 활성 기능으로 확인하며 사용자 PC 적용 여부를 별도로 보고한다.
도입 diff를 revert하여 복구한다. 기존 lease/registry/전역 설정/제품 데이터는 건드리지 않는다.
