---
name: resume-agent-work
description: "vox.ai 구축·운영 작업이 연결 단절·권한 만료·부분 성공·불명 응답으로 끊겼을 때 완료된 단계를 보존하고 이어간다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# resume-agent-work

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다. 현재 저장·재개 capability는 [워크플로 capability 표](../../references/workflow-capabilities.json)와 [합성 고객 여정](../../references/workflow-examples.md)에 있다.

## 복귀 자료
현재 연결 조직·주체를 확인하고 이전 목표, 완료 리소스 ID, 응답 상태를 읽는다. 호스트가 `get_work_context`, `get_work_record`, `save_work_record`, `get_work_operation`을 실제 도구와 schema로 제공하면 shared improvement case를 통해 재개한다. 그 도구가 없을 때는 현재 호스트의 접근 가능한 대화나 사용자가 제공한 handoff로 fallback한다.

## 상태별 다음 행동
| 상태 | 행동 |
| --- | --- |
| Manual 저장 성공, 후속 단계 실패 | 받은 `agent_id`와 `manual_id`로 Manual을 조회하고 그 Single에서 이어간다 |
| 저장 성공, 재조회 실패 | 같은 `agent_id`·`manual_id`를 재조회; 새 리소스 생성 금지 |
| Manual create 응답 불명 | 같은 `agent_id`에서 `list_manuals`로 후보를 찾고 `get_manual`로 ID·전체 본문·revision을 비교한다; 일치 후보는 현재 대상으로 사용할 수 있지만 exact receipt 없이는 원 create 성공으로 단정하지 않는다 |
| 실제 제품 작업 응답 불명 | 현재 도구가 해당 동작·결과 조회를 제공하는지 먼저 확인; 제공하지 않으면 제품 UI에서 상태를 확인하도록 안내하고 재실행하지 않음 |
| 인증 만료/철회 | 호스트의 재연결 경로로 권한 복구 후 실제 상태 재조회 |
| 다른 조직으로 바뀜 | 이전 조직 자격 증명/리소스를 재사용하지 않음 |

MCP의 동일 키 재호출 계약이 실제 도구 schema/설명에서 확인되고 허용하는 경우에만 같은 요청을 사용한다. 현재 구현 baseline에는 공통 operation 조회 도구가 없다. 키를 새로 만들어 재전송하거나 직접 API로 우회하지 않는다.

## 결과
지금까지 확인된 완료, 미확인 동작, 현재 막힌 이유, 가능한 다음 조회/사용자 행동을 구분한다. 콜이 이미 접수됐으면 연결을 끊거나 대화를 취소해도 전화가 자동 취소된다고 말하지 않는다. 파일·모델 요약은 제품 상태의 정본이 아니다.

복귀 시 [업무 판단 기준](../../references/workflow-guidance.md)의 작은 업무 요약에서 목표·사용자 결정·완료 참조·다음 행동을 읽는다. shared-work 도구가 없을 때 새 Thread나 호스트에서 그 요약에 접근할 수 없다면 사용자에게 최신 ID와 결정 요약을 요청한다. 모델 요약만으로 실행 권한이나 제품 상태를 확정하지 않는다. delivery.reference는 원문 읽기를, delivery.unavailable은 알려진 결과 조회를 이어간다. 새 환경이 생겨도 이미 시도한 제품 쓰기를 다시 실행하지 않는다. handoff 예는 [합성 고객 여정](../../references/workflow-examples.md)에 있다.
