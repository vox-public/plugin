# 업무 호출 예와 ID 흐름

도구명은 AC1 출시 설계 117개에서 가져왔다. 아직 배포된 117개라는 뜻이 아니다. 아래 JSON은 대표 6개 계약의 **합성 비실행 예제**이며 다른 도구의 payload를 추정하지 않는다. 실제 연결 schema와 일치하는지 확인 후 사용한다.

## 구축: Manual → agent → 재조회

```json
{"tool":"save_manual","arguments":{"mode":"create","payload":{"name":"샘플 견적 접수","content":"청소 유형과 희망일을 확인하고 내용을 요약한다. 마무리 후 @tool:end_call","built_in_tools":[{"toolType":"end_call","name":"end_call"}]}}}
```

Manual 응답의 실제 ID를 다음 agent payload의 실제 `manualIds` 스키마에 맞춰 전달한다. 이 문서의 UUID 예시를 실사용 ID로 복사하지 않는다. Single 설정, 필수 모델/음성, postCall의 구체 형식은 `get_schema`와 공개 도구 입력으로 확인한다.

`save_manual(create)` → 반환 Manual ID → `save_agent(create, payload)` → 반환 agent ID → `get_agent/get_manual` → 실제 지원 시 `open_voice_test_session` → 실제 callId → `get_call`.

Manual 저장만 성공했으면 ID를 보존하고 연결 단계부터 이어간다. 두 리소스를 처음부터 다시 만들지 않는다. 시험 미실행이면 저장과 시험 준비까지만 보고한다.

## 기존 조회·수정 예

```json
{"tool":"get_agent","arguments":{"agent_id":"00000000-0000-4000-8000-000000000001"}}
```

```json
{"tool":"save_manual","arguments":{"mode":"update","manual_id":"00000000-0000-4000-8000-000000000002","payload":{"config":{"tool_call_sound":null}}}}
```

두 번째는 허용된 config 옵션의 null 예제이며 content를 null로 지우라는 뜻이 아니다. `get_manual`의 본문과 관련 설정을 읽고 전체 본문을 보존하는 편집은 해당 계약을 따른다. 파생 `tool_ids`를 save_manual 입력으로 보내지 않는다.

## 나머지 업무: 구체 schema는 연결 도구에서 읽는다

| 업무 | 대표 도구 흐름 | 재개/검증 |
| --- | --- | --- |
| 인바운드 | list_numbers/get_number → set_number_agents → get_number | 실제 수신 통화의 callId 확인 |
| 번호 신청 | list_available_numbers/구분에 맞는 request 도구 → 번호/신청 조회 | 접수/심사/확보/연결 분리 |
| 단건 발신 | get_agent/get_number → place_call → get_call | 불명 결과는 새 키로 재발신 금지 |
| 캠페인 | launch_campaign → get_campaign; pause/resume/cancel 별도 | 대상별 상태; 중지 의미는 실제 계약 |
| SMS | send_sms/send_sms_batch → get_sms/get_sms_batch | 접수와 전달 상태 분리 |
| 위젯/채팅 | get_widget → save_widget → 별도 publish_widget; create_chat/create_chat_message/get_chat | 설정·게시·대화 성공 분리 |

전체 도구 입력을 이 파일에 복제하지 않는다. authoritative design은 도구 원장 (제품 계약은 연결된 MCP의 실제 스키마를 확인), 예제 정본은 대표 예제 JSON (제품 계약은 연결된 MCP의 실제 스키마를 확인)이다. 원고 변경 시 이 세 합성 입력을 대표 schema로 재검증한다.
