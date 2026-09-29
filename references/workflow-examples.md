# 합성 고객 여정: 만들기, 다듬기, 직접 시험, 운영, 재개

이 예시는 합성 자료와 도구 호출 형식을 보여준다. 실제 요청 전에 연결된 호스트의 실제 도구와 schema를 확인한다. 번들에는 14개 도구의 schema 후보가 있으며 실제 사용 가능 여부는 연결된 서버에서 확인한다. user-principal save_agent/save_manual에는 직전 get_work_context에서 받은 context receipt가 필요하다. 도구나 receipt가 없으면 제품 쓰기 대신 초안과 빠진 capability를 안내한다.

## 합성 요청과 완료 기준

고객이 “샘플 홈케어 문의를 받는 음성 에이전트를 만들고 싶어요”라고 요청한다. 제공된 합성 자료에는 세 가지 업무가 있다.

- 어떤 서비스를 원하는지와 가능한 날짜 범위를 접수한다.
- 위치와 주소는 업무 범위를 파악한 뒤 한 번만 확인한다.
- 가격표나 예약 API는 연결되어 있지 않으므로 가격·방문 시간·예약 확정을 약속하지 않는다. 접수 내용 요약과 담당자 확인이 다음 단계다.

성공은 Manual에 접수 흐름과 제한이 저장되고 재조회되는 것이다. 이는 예약 기능 연결이나 고객 음성 시험 통과를 뜻하지 않는다.

## 1. Authoring: 첫 Manual 저장

조직이 의도한 곳인지 확인한 뒤, 반환된 ID만 후속 호출에 사용한다.

```mcp-call
{"tool":"get_organization","arguments":{}}
```

user-principal 저장 직전에 context를 읽는다. 응답의 context_receipt.token을 아래 한 번의 save_agent에 복사한다. placeholder는 실제 호출 전에 응답 token으로 바꾼다.

```mcp-call
{"tool":"get_work_context","arguments":{"purpose":"새 Single 생성 전 관련 결정 확인","max_tokens":1000}}
```

```mcp-call
{"tool":"save_agent","arguments":{"mode":"create","context_receipt":"<paste the recent context_receipt.token here>","payload":{"name":"샘플 홈케어 문의"}}}
```

`save_agent` 응답의 실제 `agent_id`를 받아 현재 상태와 revision을 읽는다. 아래 UUID는 모양을 보이는 합성값이며 실제 호출에서는 반환된 ID를 쓴다.

```mcp-call
{"tool":"get_agent","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111"}}
```

아래 `expected_head_revision`은 형식을 보이는 예시값이다. 실제 호출에서는 방금 읽은 revision으로 바꾼다. Manual은 현재 agent에 귀속된다.

방금 읽은 agent revision을 확인한 뒤, 제품 저장마다 새 context receipt를 받는다. 이 placeholder는 실제 get_work_context 응답 token으로 바꾼다.

```mcp-call
{"tool":"get_work_context","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111","purpose":"Manual 생성 전 agent 결정과 열린 작업 확인","max_tokens":1000}}
```

```mcp-call
{"tool":"save_manual","arguments":{"mode":"create","agent_id":"11111111-1111-4111-8111-111111111111","context_receipt":"<paste the recent context_receipt.token here>","payload":{"expected_head_revision":7,"name":"샘플 홈케어 문의 접수","trigger":"고객이 홈케어 서비스나 방문 가능성을 문의할 때","content":"목표: 서비스 문의를 정확히 접수하고 담당자가 이어서 확인할 수 있도록 요약한다.\n\n진행: 1) 원하는 서비스 종류를 묻는다. 2) 가능한 날짜 범위를 묻는다. 3) 서비스 범위를 좁힌 뒤 위치와 주소를 한 번 확인한다. 4) 접수 내용을 요약하고 빠진 점이나 정정이 있는지 묻는다.\n\n제한: 연결된 가격표와 예약 확인 기능이 없다. 확정 가격, 방문 시각, 예약 완료를 말하지 않는다. 확인이 필요한 질문은 추측하지 말고 담당자 확인이 필요하다고 설명한다.\n\n마무리: 접수된 내용을 요약하고 담당자가 확인할 다음 단계를 안내한다. 고객이 정정하면 요약을 갱신한다."}}}
```

저장 결과의 `manual_id`를 보존하고 실제 리소스를 재조회한다.

```mcp-call
{"tool":"get_manual","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111","manual_id":"22222222-2222-4222-8222-222222222222"}}
```

본문과 `head_revision`이 의도한 값인지 확인한다. Manual만 저장됐다면 새 agent를 만들지 않고 같은 `agent_id`로 이어간다. 저장 성공과 readback 성공은 별도 결과로 보고한다.

## 2. Refine: 정책을 좁게 바꾸고 확인

고객이 “주소를 먼저 묻지 말고, 어떤 서비스를 원하는지 파악한 다음 한 번만 물어봐 주세요”라고 한다. 먼저 같은 agent의 전체 Manual을 읽고 변경 지점과 보존할 제한을 확인한다.

```mcp-call
{"tool":"get_manual","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111","manual_id":"22222222-2222-4222-8222-222222222222"}}
```

Manual 본문 저장은 전체 본문 교체다. 아래 `content`에는 변경 문장뿐 아니라 가격·예약 확정 제한, 요약과 정정 흐름을 포함한 **전체 새 본문**을 보낸다. `expected_head_revision`은 방금 조회한 Manual의 현재 revision으로 교체한다.

Manual의 최신 revision을 다시 읽고, 저장 직전에 새 context receipt를 받는다. 이 placeholder를 실제 token으로 교체한다.

```mcp-call
{"tool":"get_work_context","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111","purpose":"Manual 수정 전 최신 결정과 agent head 확인","max_tokens":1000}}
```

```mcp-call
{"tool":"save_manual","arguments":{"mode":"update","agent_id":"11111111-1111-4111-8111-111111111111","manual_id":"22222222-2222-4222-8222-222222222222","context_receipt":"<paste the recent context_receipt.token here>","payload":{"expected_head_revision":8,"content":"목표: 서비스 문의를 정확히 접수하고 담당자가 이어서 확인할 수 있도록 요약한다.\n\n진행: 1) 원하는 서비스 종류를 묻는다. 2) 가능한 날짜 범위를 묻는다. 3) 고객이 원하는 업무 범위를 파악한 다음 위치와 주소를 한 번만 확인한다. 이미 주소를 들었다면 반복 질문하지 않는다. 4) 접수 내용을 요약하고 빠진 점이나 정정이 있는지 묻는다.\n\n제한: 연결된 가격표와 예약 확인 기능이 없다. 확정 가격, 방문 시각, 예약 완료를 말하지 않는다. 확인이 필요한 질문은 추측하지 말고 담당자 확인이 필요하다고 설명한다.\n\n마무리: 접수된 내용을 요약하고 담당자가 확인할 다음 단계를 안내한다. 고객이 정정하면 요약을 갱신한다."}}}
```

`get_manual(agent_id, manual_id)`로 다시 읽어 주소 규칙이 한 번만 반영되고 다른 제한이 남았는지 확인한다. `409`이면 최신 본문을 다시 읽고 의도를 재적용한다. 쓰기 응답이 불명이면 중복 update를 보내지 말고 알려진 ID를 재조회한다.

## 3. Customer direct test: 고객이 직접 말해 보고 피드백

Assistant는 고객이 확인할 사례와 기대 동작을 준비한다. 예를 들어 고객은 “이번 주 금요일에 에어컨 청소 가능해요? 가격도 알려주세요”라고 말해 본다. 기대 동작은 서비스 종류와 날짜 범위를 접수하고, 연결되지 않은 가격·예약 확정을 약속하지 않는 것이다. 두 번째 사례에서는 고객이 먼저 주소를 말하고 서비스 종류를 바꾼다. 기대 동작은 주소를 되묻지 않고 새 서비스 범위를 반영하는 것이다.

고객은 기존 vox.ai 제품 UI에서 음성 시험을 직접 실행한다. 이 번들 후보에는 시험 시작이나 통화 결과 조회가 없다. 고객이 “두 번째 사례에서 주소를 다시 물었어요”라고 보고하면 이후 작업에 영향을 줄 피드백으로 보고 기록한다. 실제 call 조회가 확인되지 않았으므로 independent call evidence라고 부르지 않는다. call reference는 locator로만 남기고 전체 transcript를 수집하지 않는다.

피드백이 Manual 분기 수정으로 이어지면 위 refine 흐름으로 좁게 바꾸고 저장값을 재조회한다. 고객의 보고는 feedback_reported 또는 customer_voice_report로 요약 기록하고 계속 reported 상태로 둔다. 전달에는 고객이 다시 말할 문장과 기대 결과를 적는다. 실제 재시험 전에는 “저장 확인·고객 재시험 대기”로 상태를 표현한다.

## 4. Operate: 실제 운영과 개선 근거 구분

고객이 “오늘부터 실제 문의를 받아도 될까요?”라고 묻는다. `get_agent`와 `get_manual`은 설정을 확인하는 선택적 조회다. 현재 구현 도구에는 번호 연결, 게시·활성화, 실전화·캠페인 발신, call history 조회가 없다. 저장된 설정만 보고 운영 가능하다고 판정하거나 MCP로 실제 전화를 실행했다고 말하지 않는다.

고객이 제품 UI에서 권한·연결 상태를 확인하고 실제 운영을 진행한다. 이후 고객이 “오늘 접수는 괜찮았지만 주소를 중복 질문했다”고 알려주면, 그 내용을 고객 보고로 분류하고 수정 가설·확인 사례를 제안한다. 실제 통화 원문이나 결과가 필요하면 고객이 접근 가능한 근거를 제공하도록 안내한다. 조회가 되지 않은 운영 결과는 관측된 call 통계로 표현하지 않는다.

## 5. Resume: 부분 성공을 보존하고 다른 세션에서도 안전하게 이어가기

### Manual 생성 응답이 불명인 경우

agent 생성은 성공해 실제 `agent_id`를 받았지만 Manual 생성 응답이 사라졌다고 하자. 새 Manual을 즉시 만들지 않는다. 같은 `agent_id`에서 목록을 확인한다.

```mcp-call
{"tool":"list_manuals","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111"}}
```

Manual 이름이 맞는 항목이 하나여도 기존 리소스와 이번 create 요청을 구분할 수는 없다. 후보의 실제 `manual_id`로 전체 본문과 revision을 읽어 의도한 내용인지 대조한다. 일치하면 그 리소스를 현재 대상으로 이어갈 수 있지만, exact receipt나 별도 증거가 없으면 불명 쓰기의 성공이라고 보고하지 않는다. 없거나 여러 후보가 있거나 내용이 다르면 상태 불명으로 남기고 create를 반복하지 않는다.

### 다른 Thread나 호스트에서 다시 시작하는 경우

번들 후보에는 shared-work 도구 네 개가 있다. 새 Thread나 다른 호스트에서는 실제 tool list와 schema를 먼저 확인하고 get_work_context/get_work_record로 case와 version을 읽는다. 관련 결정·피드백은 별도 기억 키워드를 요구하지 않고 짧게 save_work_record로 남긴다. routine case/event 저장 전 `get_work_context.data.background_settings`의 enabled/revision/epoch를 확인한다. 기본은 켜짐이며 OFF이면 automatic 저장을 멈춘다. 명시적으로 요청한 기존 기록 조회·정정·삭제는 계속 지원한다. 사용자가 현재 대화에서 저장하지 말라고 직접 요청하면 새 기록이나 수정을 하지 않는다. 도구가 없을 때만 현재 대화나 아래 사용자 제공 handoff로 이어가며 다른 Thread를 검색했다고 말하지 않는다.

```text
목표: 샘플 홈케어 문의 접수 Manual 완성
agent_id: <실제 ID>
manual_id: <실제 ID>
마지막으로 확인한 agent/manual revision: <실제 값>
직접 표현한 결정: 업무 범위 파악 후 주소를 한 번만 묻기
시험 피드백: 고객 보고 — 주소를 다시 물었음; call 증거는 미확인
다음 행동: 최신 Manual을 다시 읽고 규칙을 좁게 수정한 뒤 고객에게 재시험 사례 전달
```

이 fallback 요약은 사용자 제공 handoff이며 서버 기록이 아니다. shared-work 경로에서는 MCP가 반환한 case/record ID와 version을 확인한다. save_work_record 결과가 unknown이면 동일 operation_id로 get_work_operation을 조회하고 POST를 반복하지 않는다. 어느 경로든 재개할 때는 [resume-agent-work](../skills/resume-agent-work/SKILL.md)의 동일 ID·최신 상태 확인 원칙을 적용한다.


## 6. Relevant work record: 결정과 고객 피드백

중요한 사용자 결정이나 이후 작업에 영향을 줄 고객 피드백이 나오면 “기억해” 요청을 기다리지 않고 관련 record를 확인한다. 먼저 get_work_context를 읽고, agent case 목록은 아래처럼 찾는다.

```mcp-call
{"tool":"get_work_context","arguments":{"agent_id":"11111111-1111-4111-8111-111111111111","purpose":"현재 agent의 결정과 열린 개선 case 찾기","max_tokens":1000}}
```

기존 case 목록은 get_work_record로 확인한다.

```mcp-call
{"tool":"get_work_record","arguments":{"record_type":"list","agent_id":"11111111-1111-4111-8111-111111111111","limit":20}}
```

기존 case가 없으면 goal과 success criteria, 최소 source locator로 case를 만든다. operation_id는 매 쓰기마다 새 UUID를 한 번 사용한다.

```mcp-call
{"tool":"save_work_record","arguments":{"action":"create","payload":{"operation_id":"33333333-3333-4333-8333-333333333333","agent_id":"11111111-1111-4111-8111-111111111111","goal":"홈케어 문의 Manual이 주소를 한 번만 확인하는지 개선한다","success_criteria":"서비스 범위를 확인한 다음 주소를 한 번만 묻고 가격이나 예약을 확정하지 않는다","source":{"source_host":"codex","explicit_quote":"샘플 홈케어 문의를 받는 음성 에이전트를 만들고 싶어요.","observed_at":1790670000000},"expected_settings_revision":1,"expected_settings_epoch":1}}}
```

Routine automatic 저장의 `expected_settings_revision`과 `expected_settings_epoch`는 최신 get_work_context의 `background_settings`에서 복사한다. 예시 값은 placeholder이므로 실제 설정이 OFF이거나 revision/epoch가 달라졌다면 자동 요청을 보내지 않는다.

기존 case라면 get_work_record의 case version을 읽고 decision_set 또는 feedback_reported event를 append한다. 고객의 “주소를 다시 물었어요”는 고객 보고이며 call 조회 결과가 아니다. 아래 version/ID는 예시이므로 실제 응답값으로 바꾼다.

```mcp-call
{"tool":"get_work_record","arguments":{"record_type":"case","case_id":"44444444-4444-4444-8444-444444444444"}}
```

결정은 짧은 typed event로 남긴다.

```mcp-call
{"tool":"save_work_record","arguments":{"action":"event","case_id":"44444444-4444-4444-8444-444444444444","payload":{"expected_version":1,"operation_id":"55555555-5555-4555-8555-555555555555","source":{"source_host":"codex","explicit_quote":"주소를 먼저 묻지 말고, 어떤 서비스를 원하는지 파악한 다음 한 번만 물어봐 주세요.","observed_at":1790670000000},"payload":{"kind":"decision_set","statement":"업무 범위를 파악한 뒤 주소를 한 번만 묻는다","applicability":"샘플 홈케어 문의"},"expected_settings_revision":1,"expected_settings_epoch":1}}}
```

고객의 음성 피드백도 같은 case에 보고 event로 기록한다. 고객 보고를 독립 call evidence로 바꾸지 않는다.

```mcp-call
{"tool":"save_work_record","arguments":{"action":"event","case_id":"44444444-4444-4444-8444-444444444444","payload":{"expected_version":2,"operation_id":"66666666-6666-4666-8666-666666666666","source":{"source_host":"codex","explicit_quote":"두 번째 사례에서 주소를 다시 물었어요.","observed_at":1790670000000},"payload":{"kind":"feedback_reported","statement":"고객 보고: 두 번째 사례에서 주소를 다시 물음. 독립 call 조회는 아직 없음.","customer_tested":true},"expected_settings_revision":1,"expected_settings_epoch":1}}}
```

독립적인 text-contract holdout은 실제 voice test가 아니다. 아래 입력은 예시일 뿐이며 ID는 합성 값이다. holdout 등록은 자동 경로가 아니라 명시적 events 경로를 쓰므로 `expected_settings_*`를 보내지 않는다. 출처는 사용자가 현재 임베디드 Copilot 대화에서 직접 입력한 본인의 말이어야 하며 `source_host`는 `embedded`, `source_thread_id`·`source_message_id`는 그 입력의 실제 ID여야 한다. `explicit_quote`를 넣으면 그 입력의 부분 문자열이어야 한다. 외부 호스트(codex, claude, api)에서는 등록할 수 없으며, ID를 알 수 없으면 추측하지 말고 등록하지 않는다. 운영에서는 사용자가 제공한 독립 task와 exact expected artifact를 사용한다. `scenario`는 JSON 문자열이며 정확히 task_kind=agent_partial_edit, base_configuration, requested_change, required_preservation(1~6개)만 담는다. `observed_result`는 등록 필수 필드지만 `register_holdout: true`에서는 서버가 caller 값을 폐기하고 실행 전/unverified로 저장한다. expected artifact와 preservation 조건은 model prompt에 전달되지 않고 서버 grader에만 사용된다.

```mcp-call
{"tool":"save_work_record","arguments":{"action":"event","case_id":"44444444-4444-4444-8444-444444444444","payload":{"expected_version":3,"operation_id":"77777777-7777-4777-8777-777777777777","source":{"source_host":"embedded","source_thread_id":"88888888-8888-4888-8888-888888888888","source_message_id":"99999999-9999-4999-8999-999999999999","explicit_quote":"합성 text holdout 등록 예시이며 실제 고객 시험이나 음성 결과가 아닙니다.","observed_at":1790670000000},"payload":{"kind":"evaluation_reported","scenario":"{\"task_kind\": \"agent_partial_edit\", \"base_configuration\": \"Business hours: Monday-Friday 10:00-18:00. Reservations: accept by phone. Weekends: closed.\", \"requested_change\": \"Change weekday hours to 09:00-17:00.\", \"required_preservation\": [\"Reservations: accept by phone.\", \"Weekends: closed.\"]}","expected_result":"Business hours: Monday-Friday 09:00-17:00. Reservations: accept by phone. Weekends: closed.","observed_result":"Scenario registered; no provider execution.","evaluation_kind":"text_contract","register_holdout":true}}}}
```

외부 call transcript 전체를 읽거나 복사하지 않는다. 필요한 것은 짧은 피드백과, 사용자가 제공한 경우 조회에 필요한 call ID뿐이다. get_work_context의 background_settings가 OFF이면 routine create/event를 보내지 않는다. settings CAS가 거부되면 최신 context를 다시 읽기 전에는 반복하지 않는다. 사용자가 현재 대화에서 저장하지 말라고 직접 요청하면 자동 create/event 없이 현재 대화에서만 이어간다. 기존 기록을 사용자가 명시적으로 조회·정정·삭제해 달라고 요청한 경우에는 해당 요청을 지원한다.

save_work_record 응답이 unknown이면 같은 operation_id로 조회한다. 방금 보낸 UUID를 그대로 쓰고 POST를 재전송하지 않는다.

```mcp-call
{"tool":"get_work_operation","arguments":{"operation_id":"66666666-6666-4666-8666-666666666666"}}
```
