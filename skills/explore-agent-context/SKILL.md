---
name: explore-agent-context
description: "기존 vox.ai 에이전트의 설정·Manual·도구·버전을 파악하거나 변경 대상을 식별할 때 사용한다. 전체 통화 성과 분석은 별도 운영 분석 스킬로 처리한다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# explore-agent-context

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 필요한 상태부터 읽는다
이름이면 `list_agents`로 찾고 후보가 여러 개면 정확한 대상을 확정한다. 현재 화면의 agent ID는 힌트이며 연결 조직과 조회 결과로 확인한다. `get_agent`에서 현재 Single의 설정과 `head_revision`을 읽고, Manual은 같은 `agent_id`로 `list_manuals` 또는 `get_manual`을 호출한다. 이미 가진 값을 위해 반복 조회하지 않는다.

Manual 본문 수정이면 대상 Single의 `agent_id`와 연결된 Manual의 정확한 `manual_id`로 `get_manual`을 호출한다. 도구 오류면 `get_tool`, 과거 콜 분석이면 `get_call`과 당시 버전의 조회 지원 범위를 확인한다. 쓰기 직전에는 현재 `head_revision`을 다시 확보한다. 독립 조회만 병렬화하고 이전 응답 ID가 필요한 조회는 기다린다.

## 결과
agent/대상 버전/관련 Manual ID/현재 `head_revision`/현재값/불명 정보를 정리한다. 목록 응답에 본문이 없거나 반환이 잘렸다면 빈 설정으로 해석하지 않는다. 전체 교체에 필요한 완전한 원문이 없으면 해당 저장을 진행하지 않는다.

탐색 요청만 받았다면 변경하지 않는다. 변경까지 이미 요청받았다면 탐색 완료를 이유로 재승인을 요구하지 않고 해당 편집 스킬로 이어간다. 제품에 없는 snapshot 조회나 전체 의존성 복제 기능을 만들지 않는다.
