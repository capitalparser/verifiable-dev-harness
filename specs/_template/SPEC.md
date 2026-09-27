# Feature: <name>

> 실질적인 기능에 사용합니다. 자잘한 수정은 기존 SPEC/PR의 짧은 작업 노트로 충분합니다.

## Business Requirement

`BR-xxx`

## Affected Workflow

`WF-xxx`

## Affected Data Flow

`DF-xxx`, `DF-xxx`

## Affected Components

`CMP-xxx`

## Input

(입력 형식/스키마)

## Output

(출력 형식/스키마)

## Invariant

(절대 깨면 안 되는 계약)

## Exception

(실패/예외 상태와 복구 경로)

## Delivery and verification scope

- 사용자에게 완결되는 결과 / 제외 범위:
- 기존 canonical owner / 재사용할 구현:
- 하나의 PR로 묶을 변경 / 분리가 꼭 필요하다면 이유:
- 영향 기능 ID / 실제 실행 entrypoint:
- focused 검사 / full로 확대할 구체적 조건:

<!-- 별도 PLAN/TASK 파일을 의무로 만들지 않습니다. 완료 조건은 ACCEPTANCE.md에만 적습니다. -->

## Plan and delegated handoff (필요한 기능에만)

- 실제로 읽은 소스·소비자 / 확인된 사실과 가정:
- 구현 방법·순서 / 공식 입력→처리→저장·반환→소비자 연결:
- 정상·반례의 독립 기대값 / 미해결 결정과 승인 경계:
- 계획 파일 참조·SHA-256 / 이번 인계의 원천 snapshot:
- 계획 안의 가역적 선택 / 계획자에게 돌려보낼 중요한 변경:

기존 작업 기록을 재사용하며 필드별 파일/승인을 만들지 않습니다.
역할별 지침과 라우팅은 [ORCHESTRATION](../../docs/ORCHESTRATION.md)을 따릅니다.
