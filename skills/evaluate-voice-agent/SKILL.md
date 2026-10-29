---
name: evaluate-voice-agent
description: "vox.ai 에이전트의 평가(유닛 테스트·시나리오 테스트)를 작성·수정·삭제·실행하고 결과를 읽을 때 사용한다. 유닛 테스트는 고정 대화 이력 뒤 다음 행동 하나를, 시나리오 테스트는 AI 고객과의 대화 전체를 판정한다. 실행은 비용이 들어 사용자 확인 뒤에만 한다. 고객이 직접 하는 음성 시험은 prepare-voice-test가 담당한다."
metadata:
  product: vox.ai
  layer: architect
  status: stable
---

# evaluate-voice-agent

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버의 실제 이름과 스키마를 확인한 뒤 사용한다. 연결에 `list_tests`·`save_unit_test` 같은 평가 도구가 없으면 없다고 알리고 [직접 음성 시험](../prepare-voice-test/SKILL.md)으로 안내하며, 작성·실행했다고 말하지 않는다.

평가는 저장한 정의로 에이전트의 응답을 판정한다. 실제 전화나 음성 품질 확인이 아니며 API·MCP 도구는 실제로 호출하지 않고 mock이 대신한다.

## 먼저 읽을 것
대상 agent와 검사할 행동을 정한다. `get_agent`로 설정과 버전, `list_manuals`/`get_manual`로 그 Single의 Manual, `get_tool`로 쓰는 도구를 읽고 읽지 못한 상품·정책 값은 추측하지 않는다. 작성 요청이면 정의 저장과 유효성 확인까지 하고, 실행 요청이 없으면 `run_tests`를 호출하지 않는다.

사용자가 통화를 근거로 평가를 만들라고 한 경우에만 `get_call`의 `include_transcript`로 원문을 읽는다. 이력은 문제 응답 직전까지만 쓰고, 잘못된 실제 응답을 기대값으로 복사하지 않는다.

## 평가 종류
| 종류 | 검사하는 것 | 입력 | 판정 | 횟수 | 저장 |
| --- | --- | --- | --- | --- | --- |
| 유닛 테스트 (`kind=unit`) | 고정 대화 이력 뒤 다음 행동 하나(응답·도구 호출·Flow 전환) | `messages`: 이력 + 마지막 검사 | 검사마다 통과·실패 | 1~10 | `save_unit_test` |
| 시나리오 테스트 (`kind=scenario`) | AI 고객과 이어가는 대화 전체 | `user_prompt`(고객 목표·행동), `rubric`(성공 기준), `max_turns` 3~30(기본 15) | 대화 전체 하나 | 1~3 | `save_scenario_test` |

정정·거절처럼 한 지점의 행동은 유닛 테스트, 여러 turn에 걸친 업무 완료는 시나리오 테스트다. Single과 Flow 모두 두 종류를 쓴다. `list_tests`·`get_test`·`delete_test`에는 `kind`를 넘긴다.

## 작성 예시
유닛 테스트(Single·도구 결과 이력·Flow 전환), 시나리오 테스트, `run_tests` 인자는 [입력 예시](../../references/evaluation-examples.md)에 있다. 시나리오 테스트의 `user_prompt`에는 고객의 목표와 행동을, `rubric`에는 대화 전체의 성공 기준을 따로 쓴다.

- 유닛 테스트의 이력 assistant는 `eval.enabled=false`, 마지막 하나만 `true`와 `expected_behavior`를 쓴다. 검사에 필요한 질문·정정·확인·도구 결과를 이력에 남기고 맨 끝 질문만 남기지 않는다.
- 도구 호출 이력은 assistant의 `tool_calls`(`function_info.name`과 객체 `arguments`) 바로 뒤에 `role=tool` 메시지를 둔다. 기대하는 도구 호출은 마지막 검사의 `expected_behavior`로 적는다.
- Flow는 마지막 검사에 `expected_kind`(`message`·`tool_call`·`transition`)가 필요하다. 전환 목적지는 `eval.to_node_id`로 쓰고 `tool_calls`와 함께 보내지 않으며, `flow_agent_id`와 `flow_start_node_id`를 함께 지정한다.
- 수정은 `mode=update`와 `test_id`로 한다. `messages`는 전체 교체이므로 `get_test`로 현재 값을 읽어 고친다.
- 의미가 틀린 초안도 저장되고 `validation.is_valid=false`와 `issues`가 온다. 같은 `test_id`를 고치며, 새로 만들거나 검사를 지우거나 기대를 느슨하게 해서 피하지 않는다. `is_valid=true`는 실행할 수 있다는 뜻이지 통과가 아니다.

`delete_test`는 사용자가 지우라고 한 정의만 지운다. 실행 중이면 거절되고 과거 실행은 남는다.

## 판정 읽기
- 실행 하나는 진행 `execution_status`(`queued`·`running`·`completed`·`error`)와 판정 `result`(`passed`·`failed`·`error`)로 나뉜다. `completed`는 통과가 아니다.
- 유닛 테스트는 `checks`마다 `result`·`reason`·`transcript_index`(응답 `transcript`의 0부터 시작하는 위치)를, 시나리오 테스트는 대화 전체에 대한 `reason` 하나를 읽는다.
- `error_message`는 실행이 오류로 끝났다는 공통 안내이며 판정 실패의 이유가 아니다.
- `billing.status=pending`이면 비용이 확정되지 않았다. `total_cost`가 비어 있으면 0원으로 보고하지 않는다.
- 실패 원인이 정의의 이력·기대·rubric일 수 있다. 근거를 확인해 정의를 고치되 기대를 낮춰 통과시키지 않는다. 에이전트 수정이 필요하면 [Manual 수정](../edit-manual-safely/SKILL.md)이나 [음성 조정](../tune-voice-behavior/SKILL.md)으로 근거와 함께 넘긴다.

## 실행과 반복
`run_tests`는 비용이 든다. 호출 전에 평가 이름·종류, 대상 agent와 버전, 횟수 합계를 대화에서 요약해 알리고, 사용자가 진행을 명시하면 호출한다. ‘평가를 만들어줘’는 실행 승인이 아니다.

- `payload.runs[]`의 항목은 `test_id`, `agent.agent_id`, `agent.agent_version`(`current`·`production`·`v{n}`), `count`다. 사용자가 버전을 말하지 않았으면 작업본(`current`)과 게시본(`production`) 중 무엇을 평가할지 확인한다.
- `idempotency_key`는 선택이다. 응답 유실 복구가 필요하면 최초 요청부터 정하고, 같은 시도의 재전송에만 같은 키와 본문을 쓴다. 키 없는 재전송은 새 실행이 된다.
- 응답은 접수(queued 배치와 run id)일 뿐이다. 진행은 `get_test_batch`의 건수, `list_test_runs`(`batch_id`·`result` 필터), 상세는 `get_test_run`으로 읽고 `list_test_batches`로 배치를 찾는다.
- `outcome=unknown`이면 다시 접수하지 않고 `list_test_batches`·`list_test_runs`로 실제 상태를 읽어 보고한다.
- 같은 정의를 `count`로 여러 번 돌려 변동을 본다. 일부만 통과하면 통과 비율과 실패 run을 함께 보고한다.
- `get_test`는 현재 정의이며 과거 실행 당시의 설정이 아니다.

## 도구 응답(mock)
정의의 `tool_mocks`가 API·MCP 사용자 도구의 응답을 대신한다. 종류는 `api`(도구 `tool_id`), `mcp`(부모 도구 `tool_id`와 이름별 `tools[]`), `flow_api`(Flow의 `agent_id`와 `node_id`)이고, 응답은 json 또는 text이며 지정하지 않으면 `{}`다. 같은 도구·노드의 mock은 하나만 둔다.

작성 전에 `get_schema`(`namespace="eval-schema"`, `schema_type="tool-mocks"`, `version="v1"`)와 `get_tool`로 형식과 실제 도구 ID·입출력을 읽는다. 조회 결과에 없는 필드나 상품·정책 값을 만들어 채우지 않고, 응답 값은 사용자가 준 자료나 도구 명세의 응답 예시에서 가져온다. mock 평가의 통과는 실제 외부 API의 동작을 확인한 것이 아니라고 보고한다.

## 완료 표시
‘정의 저장’, ‘유효성 확인’, ‘실행 접수’, ‘판정 확인’, ‘에이전트 수정 반영’은 다른 단계다. 하나가 끝났다고 뒤 단계를 완료로 표시하지 않는다.
