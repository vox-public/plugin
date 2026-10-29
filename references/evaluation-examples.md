# 평가 작성·실행 예시

[평가 스킬](../skills/evaluate-voice-agent/SKILL.md)의 입력 예시다. 이름·문장·ID는 합성 값이며, 실제 입력은 연결된 서버의 도구 스키마와 대상 agent의 실제 값으로 채운다.

## 유닛 테스트: 정정한 날짜 반영

`save_unit_test`의 인자다. 이력의 assistant는 `eval.enabled=false`, 마지막 검사 하나만 `true`와 `expected_behavior`를 쓴다.

```json
{
  "mode": "create",
  "payload": {
    "name": "정정한 날짜 반영",
    "messages": [
      {"role": "user", "content": "다음 주 수요일 오전으로 예약하고 싶어요."},
      {"role": "assistant", "content": "수요일 오전으로 확인했어요. 성함을 알려 주세요.", "eval": {"enabled": false}},
      {"role": "user", "content": "아, 수요일 말고 금요일로 바꿔 주세요."},
      {"role": "assistant", "content": "", "eval": {"enabled": true, "expected_behavior": "날짜를 금요일로 정정해 다시 확인하고, 수요일 예약으로 진행하지 않는다."}}
    ]
  }
}
```

## 유닛 테스트: 도구 결과가 이력에 있는 경우

도구 요청은 assistant의 `tool_calls`, 결과는 바로 뒤 `role=tool` 메시지의 문자열이다. 마지막 검사는 도구 결과를 읽은 뒤의 안내다.

```json
{
  "mode": "create",
  "payload": {
    "name": "조회 결과의 이용 가능일 안내",
    "messages": [
      {"role": "user", "content": "이용 방법을 알려 주세요."},
      {"role": "assistant", "content": "", "eval": {"enabled": false}, "tool_calls": [{"function_info": {"name": "lookup_document"}, "arguments": {"topic": "이용 방법"}}]},
      {"role": "tool", "content": "{\"summary\":\"평일에 이용할 수 있습니다.\"}"},
      {"role": "assistant", "content": "", "eval": {"enabled": true, "expected_behavior": "조회 결과의 이용 가능일(평일)을 그대로 안내하고 주말 이용을 약속하지 않는다."}}
    ]
  }
}
```

## 유닛 테스트: Flow 전환

Flow는 `flow_agent_id`와 `flow_start_node_id`를 함께 쓰고, 마지막 검사에 `expected_kind`와 전환 목적지 `eval.to_node_id`를 쓴다.

```json
{
  "mode": "create",
  "payload": {
    "name": "예약 조회로 전환",
    "flow_agent_id": "11111111-1111-4111-8111-111111111111",
    "flow_start_node_id": "greeting",
    "messages": [
      {"role": "user", "content": "예약을 확인해 주세요."},
      {"role": "assistant", "content": "", "eval": {"enabled": true, "expected_kind": "transition", "to_node_id": "lookup-booking", "expected_behavior": "예약 조회로 전환한다."}}
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

사용자가 진행을 확인한 뒤의 `run_tests` 인자다. 유닛 테스트는 `count` 1~10, 시나리오 테스트는 1~3이다. `idempotency_key`는 같은 시도의 재전송에만 같은 값을 쓴다.

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
  "idempotency_key": "evaluate-2026-10-29-01"
}
```
