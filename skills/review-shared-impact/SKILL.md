---
name: review-shared-impact
description: "특정 vox.ai Single의 Manual·지식·도구 변경 범위를 확인할 때 사용한다. 제품이 보장하지 않는 격리나 자동 복제를 약속하지 않는다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# review-shared-impact

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 범위와 실제 참조
사용자가 바꾸려는 Single의 `agent_id`와 그 Manual·지식·도구의 현재 참조를 조회한다. Manual은 agent-scoped이므로 전역 공유 원본이라고 가정하지 않는다. 전용 dependency 조회가 없으면 지원되는 agent 조회·목록의 범위만 사용하고 확인하지 못한 영향 범위를 표시한다.

‘A만 수정’이면 A의 `agent_id` 범위를 벗어나 저장하지 않는다. 제품이 지원하는 create/save와 A의 연결 변경으로 필요한 사본을 만들 수 있는지 확인한다. 사용자가 전체 공유 변경을 요청했다면 실제로 공유되는 리소스만 그 범위로 진행한다. 자동으로 모든 도구·지식까지 깊은 복제하지 않는다.

## 저장과 확인
사본 생성이나 연결 변경이 실제 도구에 있다면 받은 ID를 보존하고 대상 `agent_id`를 재조회한다. 중간 실패 시 이미 받은 ID와 현재 상태를 남기고 처음부터 다시 생성하지 않는다. 다중 리소스 자동 롤백이나 CAS를 보장하지 않는다.

검증 결과는 ‘A 연결 변경 확인’, ‘공유 원본 불변 확인’, ‘다른 대상 영향 미확인’처럼 근거별로 표시한다. 참조를 모두 조회하지 못했는데 ‘모든 agent 안전’이라고 하지 않는다. 연결 해제·삭제는 사용자 요청 범위와 실제 권한에 따른다.
