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
현재 연결 조직·주체를 확인하고 먼저 get_work_context로 관련 결정·열린 작업을 찾은 뒤 get_work_record에서 기존 case와 version을 확인한다. 실제 도구 목록과 schema에 shared-work 도구가 있으면 해당 case로 재개하고 필요한 결정·피드백을 짧게 기록한다. get_work_context의 background_settings에서 기본 켜짐 상태와 revision/epoch를 확인한다. OFF이면 자동 기록을 중지하되 사용자가 명시적으로 요청한 기존 기록 조회·정정·삭제는 계속 지원한다. routine save가 settings CAS로 거부되면 재시도 전에 최신 설정을 다시 읽는다. 사용자가 현재 대화에서 기록하지 말라고 하면 쓰지 않는다. 도구가 없을 때는 현재 호스트의 접근 가능한 대화나 사용자가 제공한 handoff로 이어간다. `pending_recent_inputs`는 같은 사용자의 아직 정리 전 최근 입력이므로 참고만 하고 확정 기억처럼 단정하지 않으며 필요하면 사용자에게 확인한다. guidance의 `current_agent_revision`이 `evaluated_agent_revision`보다 크면 평가 이후 agent가 바뀐 것이니 현재 agent를 다시 읽고 guidance를 절차로만 적용한다. `evaluation_reported.register_holdout`은 사용자가 현재 임베디드 Copilot 대화에서 직접 입력한 독립 사례(요청 변경·기대 결과·보존 조건)를 같은 턴에서 처리되기 전에 get_work_context의 pending_recent_inputs 해당 항목에서 그대로 복사한 source_thread_id(→source.source_thread_id)·source_id(→source.source_message_id)와 함께 명시적 경로로 보낼 때만 등록한다. 외부 호스트(codex, claude, api)에서는 등록할 수 없고, 모델이 만든 사례나 추측한 ID로 등록하지 않는다.

## 상태별 다음 행동
| 상태 | 행동 |
| --- | --- |
| Manual 저장 성공, 후속 단계 실패 | 받은 `agent_id`와 `manual_id`로 Manual을 조회하고 그 Single에서 이어간다 |
| 저장 성공, 재조회 실패 | 같은 `agent_id`·`manual_id`를 재조회; 새 리소스 생성 금지 |
| Manual create 응답 불명 | 같은 `agent_id`에서 `list_manuals`로 후보를 찾고 `get_manual`로 ID·전체 본문·revision을 비교한다; 일치 후보는 현재 대상으로 사용할 수 있지만 exact receipt 없이는 원 create 성공으로 단정하지 않는다 |
| save_work_record 응답 불명 | 동일 UUID operation_id로 get_work_operation을 조회; POST를 반복하거나 새 ID를 만들지 않음 |\n| 실제 제품 작업 응답 불명 | 현재 도구가 해당 동작·결과 조회를 제공하는지 먼저 확인; 제공하지 않으면 제품 UI에서 상태를 확인하도록 안내하고 재실행하지 않음 |
| 인증 만료/철회 | 호스트의 재연결 경로로 권한 복구 후 실제 상태 재조회 |
| 다른 조직으로 바뀜 | 이전 조직 자격 증명/리소스를 재사용하지 않음 |

제품이나 작업 기록의 unknown 결과를 임의로 재실행하지 않는다. save_work_record는 처음 사용한 UUID operation_id로 get_work_operation을 조회해 영수증을 확인한다. 새 operation ID, POST 재시도, 직접 API 우회를 하지 않는다.

## 결과
지금까지 확인된 완료, 미확인 동작, 현재 막힌 이유, 가능한 다음 조회/사용자 행동을 구분한다. 콜이 이미 접수됐으면 연결을 끊거나 대화를 취소해도 전화가 자동 취소된다고 말하지 않는다. 파일·모델 요약은 제품 상태의 정본이 아니다.

복귀 시 [업무 판단 기준](../../references/workflow-guidance.md)의 작은 업무 요약과 get_work_context/get_work_record 결과에서 목표·사용자 결정·완료 참조·다음 행동을 읽는다. shared-work 도구가 없을 때 새 Thread나 호스트에서 그 요약에 접근할 수 없다면 사용자에게 최신 ID와 결정 요약을 요청한다. 모델 요약만으로 실행 권한이나 제품 상태를 확정하지 않는다. delivery.reference는 원문 읽기를, delivery.unavailable은 알려진 결과 조회를 이어간다. 새 환경이 생겨도 이미 시도한 제품 쓰기를 다시 실행하지 않는다. handoff 예는 [합성 고객 여정](../../references/workflow-examples.md)에 있다.
