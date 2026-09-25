## Outcome and scope

사용자 결과 / 변경 범위 / 제외 범위. 기능 구현·배선·시험·필요 문서를 함께 묶었는가?

계획한 기능/AC와 현재 PR head SHA에 실제로 커밋된 경로:
빠진 기능 또는 다음 슬라이스로 넘긴 범위:

## Verification

SHA·dirty 여부 / profile·선택 이유 / 실행 결과 / receipt 위치.
필수 미실행·실패·잔여 위험을 명시한다. full은 해당 사유가 있을 때만 수행한다.
후속 수정 뒤 영향 검증을 다시 실행했는가? 이전 SHA의 결과라면 구분한다.

## Risk and next action

계약·권한·데이터 영향 / rollback / 필요한 승인. 영향 없으면 짧게 N/A.
검증 통과가 merge/deploy 승인을 뜻하지 않는다.
PR 제출, 병합, 사용 환경 반영은 각각 확인된 사실만 적는다.
