---
name: evaluate-voice-agent
description: "vox.ai 에이전트의 평가(유닛 테스트·시나리오 테스트)를 작성·수정·삭제·실행하고 결과를 읽을 때 사용한다. 유닛 테스트는 고정 대화 이력 뒤 다음 행동 하나를, 시나리오 테스트는 AI 고객과의 대화 전체를 판정한다. 실행은 비용이 들어 사용자 확인 뒤에만 한다. 고객이 직접 하는 음성 시험은 prepare-voice-test가 담당한다."
metadata:
  product: vox.ai
  layer: architect
  status: stable
---

# evaluate-voice-agent

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버의 실제 이름과 스키마를 확인한 뒤 쓰고, 처음 작성·실행할 때 `get_eval_help`가 있으면 먼저 읽는다. 연결에 평가 도구가 없으면 없다고 알리고 [직접 음성 시험](../prepare-voice-test/SKILL.md)으로 안내하며, 작성·실행했다고 말하지 않는다.

평가는 저장한 정의로 에이전트의 응답을 판정하며 실제 전화나 음성 품질 확인이 아니다.

## 먼저 읽을 것
대상 agent와 검사할 행동을 정한다. `get_agent`로 설정과 버전, `list_manuals`/`get_manual`로 그 Single의 Manual, `get_tool`로 쓰는 도구를 읽고 읽지 못한 상품·정책 값은 추측하지 않는다. 작성 요청이면 정의 저장과 유효성 확인까지 한다.

## 평가 종류
- 유닛 테스트(`kind=unit`, `save_unit_eval`): 고정 대화 이력 뒤 다음 행동 하나(응답·도구 호출·Flow 전환)를 통과·실패로 판정한다. `count` 1~10.
- 시나리오 테스트(`kind=scenario`, `save_scenario_eval`): AI 고객과 이어가는 대화 전체를 하나로 판정한다. `user_prompt`(고객의 목표·행동)·`rubric`(대화 전체의 성공 기준)·`max_turns` 3~30(기본 15), `count` 1~3.

정정·거절처럼 한 지점의 행동은 유닛 테스트, 여러 turn에 걸친 업무 완료는 시나리오 테스트다.

## 유닛 테스트 messages
`get_call(include_transcript=true)`의 `transcript`와 같은 항목 형식이다. `user`(`content`), `agent`(`content`), `tool_call_invocation`(`tool_call_id` 선택, `name`, 객체 `arguments`), `tool_call_result`(`tool_call_id` 선택, 문자열 `content`)를 `role`로 구분한다. 예시는 [입력 예시](../../references/evaluation-examples.md)에 있다.

- 가장 쉬운 작성법: 근거 통화가 있으면 그 `transcript`를 확인할 응답까지 자르고 마지막 항목에 `eval`을 붙인다. 항목은 그대로 붙여도 되며 `start_at` 같은 다른 키는 저장되지 않는다. 잘못된 실제 응답을 기대 행동으로 옮기지 않는다.
- 검사는 마지막 항목 하나다. `eval`은 그 항목에만 두고 `expected_behavior`(Flow 전환 검사는 `to_node_id`도)만 쓰며, 다른 키는 거절된다.
- 마지막이 `agent`면 그 자리의 응답을 검사한다. Flow는 정의에 `flow_agent_id`·`flow_start_node_id`를 쓰고, 전환 검사는 `eval.to_node_id`에 목적지 노드 id를 쓰며 응답 검사에는 이 키를 넣지 않는다.
- 마지막이 `tool_call_invocation`이면 그 자리의 도구 호출을 검사하고 뒤에 결과를 두지 않는다. `name`·`arguments`는 생략할 수 있고 판정은 `expected_behavior` 문장으로 하므로, 기대하는 도구와 인자를 그 문장에 쓴다.
- 이력의 `tool_call_invocation` 바로 뒤에는 그 `tool_call_result`가 온다. 이 쌍은 여러 번 이어도 된다. 호출에 `tool_call_id`를 쓰면 결과는 같은 id를 쓰거나 생략한다.
- Manual 시작 이력은 `name`이 정확히 `StartManual`, `arguments.id`가 실제 Manual UUID인 호출과 `status`(`loaded`·`already_loaded`·`rejected`·`error`)를 담은 JSON 객체 문자열 결과의 쌍이다.
- 검사에 필요한 질문·정정·확인·도구 결과를 이력에 남기고 맨 끝 질문만 남기지 않는다.

## 저장
- 분류 값은 `metadata` 객체에 둔다. 수정은 `mode=update`와 `test_id`로 한다. `messages`는 전체 교체이므로 `get_eval`로 현재 값을 읽어 고친다.
- 의미가 틀린 초안도 저장되며 `validation.is_valid=false`와 `issues`(위치 `field`)가 온다. 같은 `test_id`를 고치고, 새로 만들거나 검사를 지우거나 기대를 느슨하게 해서 피하지 않는다. `is_valid=true`는 실행 가능이지 통과가 아니다.

`delete_eval`는 사용자가 지우라고 한 정의만 지운다. 실행 중이면 거절되고 과거 실행은 남는다.

## 판정 읽기
- 실행 하나는 진행 `status`(`queued`·`running`·`completed`·`error`)와 판정 `result`(`passed`·`failed`·`error`)로 나뉜다. `completed`는 통과가 아니고, `error_message`는 실행 오류 안내이지 판정 이유가 아니다.
- 유닛 테스트는 `checks`마다 `result`·`reason`·`transcript_index`(실행 `transcript`의 0부터 시작하는 위치)를, 시나리오 테스트는 대화 전체에 대한 `reason` 하나를 읽는다.
- `run_cost.status=pending`이면 비용 미확정이며, 비어 있는 `total_cost`를 0원으로 보고하지 않는다.
- 실패 원인이 정의(이력·기대·rubric)면 근거로 고치되 기대를 낮춰 통과시키지 않는다. 에이전트 수정은 [Manual 수정](../edit-manual-safely/SKILL.md)이나 [음성 조정](../tune-voice-behavior/SKILL.md)으로 근거와 함께 넘긴다.

## 실행과 반복
`run_evals`는 비용이 든다. 호출 전에 평가 이름·종류, 대상 agent와 버전, 횟수 합계를 요약해 알리고 사용자가 진행을 명시하면 호출한다. ‘평가를 만들어줘’는 실행 승인이 아니다.

- `payload.runs[]`는 `test_id`, `agent`(`agent_id`, `agent_version`: `current`·`production`·`v{n}`), `count`다. 한 요청의 `count` 합은 100 이하이며 넘으면 전체가 거절된다. 버전을 말하지 않았으면 현재(`current`)과 게시본(`production`) 중 확인한다.
- 선택 `idempotency_key`는 응답 유실에 대비해 최초 요청부터 정하고, 같은 시도의 재전송에만 같은 키와 본문을 쓴다.
- 응답은 접수(queued 배치와 run id)일 뿐이다. `get_eval_batch`의 건수, `list_eval_runs`(`batch_id`·`status`·`result` 필터), `get_eval_run`으로 읽는다. 목록은 기본 최신순이며 `sort_order=asc`면 오래된 순이다.
- `outcome=unknown`이면 다시 접수하지 않고 `list_eval_batches`·`list_eval_runs`로 실제 상태를 읽어 보고한다.
- `count`로 여러 번 돌려 일부만 통과하면 통과 비율과 실패 run을 함께 보고한다. `get_eval`는 현재 정의이며 과거 실행 당시의 설정이 아니다.

## 도구 응답
API·MCP 사용자 도구와 Flow API 노드는 실제로 호출되지 않고 `tool_mocks`(도구·노드마다 하나)가 응답을 대신한다. 형식은 `get_schema(namespace="contract", schema_type="save_unit_eval#payload.tool_mocks")`, 실제 도구 ID·입출력은 `get_tool`로 읽는다. 응답 값은 사용자 자료나 도구 명세의 응답 예시에서 가져오고 만들어 채우지 않는다. 도구 응답을 쓴 평가의 통과는 실제 API 동작 확인이 아니라고 보고한다.

## 완료 표시
‘정의 저장’·‘유효성 확인’·‘실행 접수’·‘판정 확인’·‘에이전트 수정 반영’은 다른 단계이며, 앞 단계가 끝났다고 뒤 단계를 완료로 표시하지 않는다.
