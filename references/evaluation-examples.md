# 평가 작성·실행 예시

[평가 스킬](../skills/evaluate-voice-agent/SKILL.md)의 입력 예시다. 이름·문장·ID는 합성 값이며, 실제 입력은 연결된 서버의 도구 스키마와 대상 agent의 실제 값으로 채운다.

## 유닛 테스트 messages 형식

`get_call(include_transcript=true)`의 `transcript`와 같은 항목을 `role`로 구분한다.

| role | 필드 |
| --- | --- |
| `user` | `content` |
| `agent` | `content`, 마지막 항목이면 `eval` |
| `tool_call_invocation` | `tool_call_id`(선택), `name`, `arguments`(객체), 마지막 항목이면 `eval`. `eval`이 붙은 항목에서는 `name`·`arguments`를 생략할 수 있다. |
| `tool_call_result` | `tool_call_id`(선택), `content`(문자열) |

- `eval`은 마지막 항목에만 두고 `expected_behavior`를 쓴다. Flow 전환을 검사하는 `agent` 항목만 `to_node_id`를 더하며, 응답 검사에는 이 키를 null이나 빈 문자열로도 넣지 않는다. `eval` 안에 다른 키를 쓰면 거절된다.
- 마지막 `agent`의 `content`는 참고용이며 비워 둘 수 있다. 판정은 실행 때 에이전트가 낸 응답을 `expected_behavior`와 비교한다.
- 마지막 `tool_call_invocation`도 판정은 `expected_behavior` 문장으로 한다. `name`·`arguments`를 적든 생략하든 기대하는 도구와 인자를 그 문장에 쓴다.
- 이력의 `tool_call_invocation` 바로 뒤에는 그 `tool_call_result`가 온다. 이 쌍은 여러 번 이어도 된다. 호출에 `tool_call_id`를 쓰면 결과는 같은 id를 쓰거나 생략하고, 모두 생략하면 저장할 때 호출 순서대로 `call_1`, `call_2`가 붙는다.
- 항목의 다른 키(통화의 `start_at`·`end_at`, 채팅의 `id`·`created_at` 등)는 받아들이되 저장하지 않으며 조회에도 나오지 않는다.

## 유닛 테스트: 통화에서 잘라 만들기

`get_call(include_transcript=true)`가 돌려준 `transcript`에서 확인할 응답까지 잘라 붙이고 마지막 항목에 `eval`만 더한 `save_unit_eval` 인자다. 복사한 항목의 `start_at`·`end_at`과 `tool_call_id`는 그대로 두어도 된다. 실제 통화의 응답이 잘못됐다면 그 응답을 기대로 옮기지 않고 `expected_behavior`에 올바른 행동을 쓴다.

```json
{
  "mode": "create",
  "payload": {
    "name": "예약 변경",
    "messages": [
      {"role": "user", "content": "예약 바꾸려고요", "start_at": 1793502312000, "end_at": 1793502313100},
      {"role": "tool_call_invocation", "tool_call_id": "c1", "name": "lookup_booking", "arguments": {"phone": "01012345678"}},
      {"role": "tool_call_result", "tool_call_id": "c1", "content": "{\"date\": \"11-03\"}"},
      {"role": "agent", "content": "11월 3일 예약 확인했어요. 언제로 바꿔 드릴까요?", "start_at": 1793502314400, "end_at": 1793502317300,
       "eval": {"expected_behavior": "확인한 예약 날짜를 말하고 바꿀 날짜를 묻는다"}}
    ],
    "metadata": {"team": "cs"}
  }
}
```

## 유닛 테스트: 정정한 날짜 반영

통화 없이 직접 쓴 이력이다. 검사에 필요한 정정까지 이력에 남긴다.

```json
{
  "mode": "create",
  "payload": {
    "name": "정정한 날짜 반영",
    "messages": [
      {"role": "user", "content": "다음 주 수요일 오전으로 예약하고 싶어요."},
      {"role": "agent", "content": "수요일 오전으로 확인했어요. 성함을 알려 주세요."},
      {"role": "user", "content": "아, 수요일 말고 금요일로 바꿔 주세요."},
      {"role": "agent", "content": "", "eval": {"expected_behavior": "날짜를 금요일로 정정해 다시 확인하고, 수요일 예약으로 진행하지 않는다."}}
    ]
  }
}
```

## 유닛 테스트: 도구 호출 검사

마지막 항목이 `tool_call_invocation`이면 그 자리의 도구 호출을 검사하며 뒤에 결과를 두지 않는다. 어떤 도구를 어떤 인자로 부르기를 기대하는지 `expected_behavior`에 쓴다.

```json
{
  "mode": "create",
  "payload": {
    "name": "전화번호로 예약 조회",
    "messages": [
      {"role": "user", "content": "예약 바꾸려고요. 번호는 010-1234-5678이에요."},
      {"role": "tool_call_invocation", "eval": {"expected_behavior": "lookup_booking 도구를 고객 전화번호 01012345678로 부른다"}}
    ]
  }
}
```

## 유닛 테스트: Manual 시작 이력

Manual 시작은 `name`이 정확히 `StartManual`이고 `arguments.id`가 실제 Manual UUID인 호출과, 바로 뒤 JSON 객체 문자열 결과의 쌍이다. 결과의 `status`는 `loaded`·`already_loaded`·`rejected`·`error`이고, `loaded`·`already_loaded`면 `manual_id`가 호출의 `id`와 같다. 통화 transcript의 `M1` 같은 별칭은 UUID가 아니므로 해당 agent의 `list_manuals`/`get_manual`로 실제 UUID를 찾아 바꾸며 목록 순서로 짐작하지 않는다.

```json
{
  "mode": "create",
  "payload": {
    "name": "환불 Manual 시작 뒤 주문번호 확인",
    "messages": [
      {"role": "user", "content": "환불 받고 싶어요."},
      {"role": "tool_call_invocation", "name": "StartManual", "arguments": {"id": "44444444-4444-4444-8444-444444444444"}},
      {"role": "tool_call_result", "content": "{\"status\": \"loaded\", \"manual_id\": \"44444444-4444-4444-8444-444444444444\"}"},
      {"role": "agent", "content": "", "eval": {"expected_behavior": "환불 접수에 필요한 주문번호를 묻고, 확인 전에 환불을 약속하지 않는다."}}
    ]
  }
}
```

## 유닛 테스트: Flow 전환

Flow는 `flow_agent_id`와 `flow_start_node_id`를 함께 쓰고, 전환은 마지막 `agent` 항목의 `eval.to_node_id`에 목적지 노드 id를 쓴다.

```json
{
  "mode": "create",
  "payload": {
    "name": "예약 조회로 전환",
    "flow_agent_id": "11111111-1111-4111-8111-111111111111",
    "flow_start_node_id": "greeting",
    "messages": [
      {"role": "user", "content": "예약을 확인해 주세요."},
      {"role": "agent", "content": "", "eval": {"expected_behavior": "예약 조회로 전환한다.", "to_node_id": "lookup-booking"}}
    ]
  }
}
```

## 시나리오 테스트: 가격 확답 요구

`user_prompt`는 AI 고객의 목표와 행동, `rubric`은 대화 전체의 성공 기준이다.

```json
{
  "mode": "create",
  "payload": {
    "name": "가격 확답 요구",
    "user_prompt": "청소 견적을 묻고, 정확한 금액을 지금 확정해 달라고 두 번 이상 요구한다.",
    "rubric": "근거 없는 금액을 확정해 말하지 않고, 확인 가능한 범위와 다음 절차를 안내한다.",
    "max_turns": 8
  }
}
```

## 실행 접수

사용자가 진행을 확인한 뒤의 `run_evals` 인자다. 유닛 테스트는 `count` 1~10, 시나리오 테스트는 1~3이고, 한 요청의 `count` 합은 100 이하다. `idempotency_key`는 같은 시도의 재전송에만 같은 값을 쓴다.

```json
{
  "kind": "unit",
  "payload": {
    "runs": [
      {
        "test_id": "22222222-2222-4222-8222-222222222222",
        "agent": {"agent_id": "33333333-3333-4333-8333-333333333333", "agent_version": "current"},
        "count": 3
      }
    ]
  },
  "idempotency_key": "evaluate-2026-11-01-01"
}
```

접수 응답의 batch와 run id로 `get_eval_batch`·`get_eval_run`을 간격을 두고 조회한다. `status`가 `queued`·`running`이면 기다리고, 판정은 `result`, 비용은 `run_cost`에서 읽는다.
