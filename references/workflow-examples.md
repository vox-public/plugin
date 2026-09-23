# 업무 호출 예와 ID·revision 흐름

아래 JSON은 입력 구조를 설명하는 합성 예제다. 실행 전에 연결된 서버의 실제 도구·스키마와 일치하는지 확인한다. 다른 도구의 payload를 이 예제로 추정하지 않는다.

## 구축: Single → agent-scoped Manual → 재조회

```json
{"tool":"save_agent","arguments":{"mode":"create","payload":{"name":"샘플 견적 접수"}}}
```

반환된 실제 `agent_id`를 보존하고 `get_agent` 또는 `list_manuals`로 현재 `head_revision`을 읽는다. Manual은 전역 리소스가 아니라 이 Single에 귀속되므로, Manual 생성에도 같은 `agent_id`와 읽은 revision을 사용한다.

```json
{"tool":"save_manual","arguments":{"mode":"create","agent_id":"<agent-id>","payload":{"expected_head_revision":12,"name":"샘플 견적 접수","content":"청소 유형과 희망일을 확인하고 내용을 요약한다. 마무리 후 @tool:end_call","built_in_tools":[{"toolType":"end_call","name":"end_call"}]}}}
```

`expected_head_revision`의 `12`는 예시값이다. 항상 쓰기 직전에 읽은 현재 값으로 바꾸며 임의의 기본값을 넣지 않는다. 반환된 실제 `manual_id`와 `agent_id`를 사용해 다음처럼 재조회한다.

```json
{"tool":"get_manual","arguments":{"agent_id":"<agent-id>","manual_id":"<manual-id>"}}
```

`save_agent(create)` → 반환 `agent_id` → `get_agent/list_manuals` → `save_manual(create, agent_id, expected_head_revision)` → 반환 `manual_id` → `get_agent/get_manual` → 실제 지원 시 `open_voice_test_session` → 실제 `call_id` → `get_call`.

Single만 저장됐으면 그 `agent_id`에서 Manual 단계를 이어간다. Manual 저장만 성공했으면 두 리소스를 처음부터 다시 만들지 않고 같은 `agent_id`·`manual_id`로 재조회한다. 시험 미실행이면 저장과 시험 준비까지만 보고한다.

## 기존 조회·수정 예

```json
{"tool":"list_agents","arguments":{}}
```

```json
{"tool":"list_manuals","arguments":{"agent_id":"<agent-id>"}}
```

```json
{"tool":"get_agent","arguments":{"agent_id":"<agent-id>"}}
```

```json
{"tool":"save_manual","arguments":{"mode":"update","agent_id":"<agent-id>","manual_id":"<manual-id>","payload":{"expected_head_revision":13,"config":{"tool_call_sound":null}}}}
```

마지막 revision도 직전 조회에서 얻은 값으로 바꾼다. `config.tool_call_sound=null`은 허용된 옵션을 끄는 예시이며 content를 null로 지우라는 뜻이 아니다. Manual `content`를 바꾸면 전체 본문을 보내고, 파생 `tool_ids`·`linked_manual_ids`·`manualIds`를 save payload에 넣지 않는다. Agent 설정을 수정할 때는 `save_agent(mode=update)` payload에도 현재 `expected_head_revision`을 포함하고, `data.manuals`를 보낼 경우 현재 UUID-keyed 값을 보존한다.

409 revision conflict가 나오면 현재 agent와 Manual을 다시 읽어 사용자의 의도를 다시 적용한다. 저장 응답이 unknown이거나 재조회가 실패하면 같은 쓰기를 자동 재실행하거나 새 리소스를 만들지 않고 지원되는 조회로 상태를 확인한다.

## 나머지 업무: 구체 schema는 연결 도구에서 읽는다

| 업무 | 대표 도구 흐름 | 재개/검증 |
| --- | --- | --- |
| 인바운드 | list_numbers/get_number → set_number_agents → get_number | 실제 수신 통화의 callId 확인 |
| 번호 신청 | list_available_numbers/구분에 맞는 request 도구 → 번호/신청 조회 | 접수/심사/확보/연결 분리 |
| 단건 발신 | get_agent/get_number → place_call → get_call | 불명 결과는 새 키로 재발신 금지 |
| 캠페인 | launch_campaign → get_campaign; pause/resume/cancel 별도 | 대상별 상태; 중지 의미는 실제 계약 |
| SMS | send_sms/send_sms_batch → get_sms/get_sms_batch | 접수와 전달 상태 분리 |
| 위젯/채팅 | get_widget → save_widget → 별도 publish_widget; create_chat/create_chat_message/get_chat | 설정·게시·대화 성공 분리 |

예제를 변경할 때 해당 도구의 실제 입력 스키마로 검증한다.
