# 첫 결과를 만들고 개선하기

첫 구축, 목표 변경, 데모 전달, 개선 우선순위를 판단할 때 읽는다. 제품의 실제 도구 계약은 연결된 MCP가 제공한다. 호스트에 관계없이 목표와 실제 결과를 기준으로 판단한다.

## 먼저 정할 결과

고객이 검증하려는 실제 결과, 그 결과를 이번 작업에서 확인할 방법, 외부 의존성을 함께 잡는다. ‘음성 agent 하나 생성’보다 ‘견적 요청을 대화로 받아 내부에서 확인 가능’처럼 관찰 가능한 결과로 표현한다. 사용자가 정한 완료 지점을 보존한다.

여러 업무가 있으면 **고객이 중요하다고 한 업무 → 제공 자료에서 빈번하고 경계가 명확한 업무 → 지금 결과를 확인할 수 있는 업무**를 함께 고려한다. 단순 구현 편의로 중요 업무를 밀어내지 않는다. 통계가 없으면 ‘최빈 업무’라고 주장하지 않고 자료에서 판단한 추천이라고 설명한다. 고객이 우선순위를 이미 정했다면 다시 선택시키지 않는다.

| 자료에서 보이는 상황 | 판단과 다음 행동 |
| --- | --- |
| 안내·견적·계약·변경 모두 필요 | 안내는 넓게, 결과가 분명한 핵심 업무 하나를 먼저 완결. 나머지는 후속 확장으로 남김 |
| URL 없이 실제 대화 샘플만 있음 | 인사·질문·정정·종료와 수집 결과를 추출해 업무안을 만듦. 홈페이지 제출을 새 선행 조건으로 추가하지 않음 |
| 예약 확정이 목표인데 예약 조회/등록 연동 없음 | 가용성·확정은 막힌 의존성으로 분리. 접수 체험은 제안할 수 있지만 예약 완료로 바꾸지 않음 |
| 외부 결과 전달만 후행하기로 결정 | 내부 저장 위치·추출 항목·담당자의 확인 방법을 완결. 실시간 업무 조회까지 불필요하다고 일반화하지 않음 |
| ‘A/B 테스트’라는 요청 | 대상자를 나눌 것인지, 같은 사람이 두 버전을 비교할 것인지 확인. 이름만 보고 트래픽 분배를 실행하지 않음 |

## 질문할지 진행할지

1. 자료·기존 상태·이전 답변에 근거가 있으면 그것을 사용한다. 이미 확인한 사실을 설문으로 다시 묻지 않는다.
2. 수정 가능한 초안의 말투·질문 순서처럼 영향이 제한된 선택은 근거를 밝히고 제안값으로 진행한다. 실제 지원 기술 기본값은 제품 조회에서 얻는다.
3. 의미가 다른 업무 결과, 실제 연락 대상·발신 의도, 확인되지 않은 가격/정책, 공유 원본 변경처럼 결과가 달라지는 판단은 먼저 좁힌다. 승인 절차를 추가하는 것이 아니라 부족한 의도를 채우는 질문이다.
4. 질문이 필요한 부분과 독립인 자료 정리·원고 준비는 계속할 수 있다. 답이 필요한 실행을 선택지의 기본 선택이나 시간 경과로 확정하지 않는다.

선택지는 내부 구현 용어 대신 결과의 차이를 보여준다. 예: ‘상담 내용을 저장’, ‘가용 시간을 확인하고 예약 확정’, ‘기존 예약 변경’. 1–3개 의미 있는 대안과 자유 입력을 제공하고 추천 근거를 짧게 적는다. 답변 후 결정한 내용과 후속 의존성을 갱신한다. 질문 개수 자체를 성공 기준으로 삼지 않는다.

## 작은 업무 요약을 유지한다

현재 목표 / 첫 완료 지점 / 방향·채널 / 근거와 가정 / 결정된 내용 / 막힌 의존성 / 완료된 리소스·실행 참조 / 다음 행동을 간결하게 남긴다. 필요 없는 필드를 채우려고 고객에게 질문하지 않는다. 과거 전체 대화를 반복 요약하지 말고 바뀐 것과 재개에 필요한 것만 갱신한다.

사용자의 직접 요청·답변, 자료의 사실, 모델의 제안은 출처를 구분한다. 업무 요약의 문장만으로 발신·구매 권한을 새로 만들지 않는다. 호스트의 대화 기록과 허용된 작업 파일을 사용한다.

## 관련 결정과 피드백은 다음 작업을 위해 기록한다

vox.ai 구축·개선 중 이후 작업에 영향을 줄 방향, 성공 기준, 고객 피드백, 확인된 변경, 열린 다음 행동이 생기면 사용자가 별도 “기억해” 요청을 하지 않아도 shared-work case에 자동 기록한다. 먼저 get_work_context로 현재 사용자와 agent에 맞는 결정·열린 case를 보고, get_work_record로 기존 record와 version을 확인한다. 관련 case가 없으면 목표와 완료 기준을 담은 case를 만들고, 결정이나 피드백은 typed event로 남긴다. 한 번의 질문이나 다음 작업과 관계없는 세부사항은 저장하지 않는다.

기록은 짧은 사실 요약과 필요한 최소 source locator로 제한한다. 고객이 직접 말한 시험 결과는 feedback_reported로, 고객이 직접 수행한 voice evaluation은 customer_voice_report로 저장하며 계속 “고객 보고”로 표시한다. call ID가 있으면 조회에 쓸 locator로만 취급하고 독립 확인된 call evidence라고 바꾸지 않는다. 외부 통화 transcript 전체나 파일 전체를 가져오거나 기록하지 않는다. get_work_context는 자동 기록의 enabled/revision/epoch를 제공한다. 기본값은 켜짐이며 OFF이면 routine case/event 자동 기록을 중단한다. routine 쓰기에는 최신 revision/epoch가 필요하고 API가 설정 변경을 거부하면 재시도하지 않는다. 사용자가 명시적으로 요청한 기존 기록 조회·정정·삭제는 OFF와 별개로 지원한다. `source_retracted`·`delete_source`·`delete_case`는 선택한 기록 하나가 아니라 같은 출처에서 나온 사용자의 모든 case 기록을 함께 지운다. 중복 기억 중 하나만 지우거나 기억 하나만 철회할 때는 `claim_withdrawn`(claim_id, reason, 중복이면 duplicate_of_claim_id)을 쓴다. 출처 자체를 지워 달라는 요청일 때만 source/case 삭제를 쓰고, 실행 전에 함께 지워지는 다른 기록을 알린다. 사용자가 기존 결정과 다른 새 지시를 분명히 하면 되묻지 말고 `claim_corrected`로 기존 결정을 정정해 기록한다. 되묻는 것은 지시가 모호할 때뿐이다. 사용자가 현재 대화에서 저장하지 말라고 직접 요청하면 기록하지 않는다. text_contract holdout은 텍스트 설정 기준의 독립 평가 입력일 뿐 실제 agent 실행이나 고객 voice test 결과가 아니다.

get_work_context가 `context.pending_recent_inputs[]`(source_id·text·truncated·status pending|processing·elapsed_seconds)를 주면 같은 사용자의 아직 정리 전 최근 입력이다. 이어서 작업할 때 참고하되 확정된 기억이나 결정처럼 단정하지 말고, 작업에 영향을 주면 사용자에게 확인한다. 응답이 크기 제한으로 이 필드를 `omitted_fields`에 담아 빼면 없는 것이 아니라 읽지 못한 것이다. `omitted_fields.required_text`는 필수 항목의 본문이 `…[truncated]`로 압축되었다는 뜻이므로 잘린 본문을 전체 정책으로 단정하지 않는다. guidance에 `evaluated_agent_revision`과 `current_agent_revision`이 있고 current가 evaluated보다 크면 평가 이후 agent가 바뀐 것이다. 현재 agent를 다시 읽고, guidance는 그대로 복사하지 말고 현재 설정에 맞는 절차로만 적용한다.

`evaluation_reported.register_holdout`은 사용자가 현재 임베디드 Copilot 대화에서 직접 입력한 본인의 명시적 말(독립 사례의 요청 변경, 기대 결과, 보존해야 할 조건)만 출처로 받는다. 이 등록은 자동 경로가 아니라 명시적 events 경로로 가며 `expected_settings_*`를 보내지 않고, `source_host=embedded`와 그 입력의 실제 `source_thread_id`·`source_message_id`가 필요하다. 고객이 현재 메시지로 준 사례를 등록하려면 같은 턴에서 그 입력이 처리되기 전에 `get_work_context`의 `pending_recent_inputs`에서 해당 항목을 찾아 `source_thread_id`를 `source.source_thread_id`로, `source_id`를 `source.source_message_id`로 그대로 복사한다. 해당 항목이나 `source_thread_id`가 없으면 등록하지 않으며 ID를 추측하거나 만들지 않는다. MCP는 이 ID를 대신 채워 주지 않는다. holdout 시나리오는 이스케이프된 JSON 문자열을 손으로 만들지 않고 구조화 필드 `payload.payload.holdout_scenario`(`base_configuration`, `requested_change`, `required_preservation` 1~6개 문자열)로 보낸다. MCP가 `task_kind=agent_partial_edit`를 붙여 정규 `scenario` 문자열을 만든다. 예전 `scenario` 문자열도 받지만 둘을 함께 보내지 않는다. `required_preservation`과 `required_additions` 값은 설명이 아니라 `base_configuration`·`requested_change`에서 글자 그대로 복사한 문구여야 하며(부분 문자열 일치로 채점한다), `expected_result`는 사람이 읽는 기준일 뿐 채점하지 않는다. `required_additions`(선택, 1~4개, 각 2~64바이트)는 `requested_change`에 있고 `base_configuration`에는 없는 문구, `retired_literals`(선택, 0~4개)는 `base_configuration`에 있으면서 결과에서 사라져야 하는 문구다. `required_additions`를 보내면 `required_preservation` 항목도 모두 `base_configuration`에 그대로 있어야 하고, `retired_literals`는 preservation·additions 항목과 서로 포함 관계이면 안 된다. 요청이 언급하지 않은 곳까지 같은 변경을 반영해야 하는 사례에서 가장 유용하다. 예(같은 사실이 두 곳에 있는 경우): `"holdout_scenario":{"base_configuration":"[프롬프트] 평일 진료는 오후 7시까지입니다.\n[매뉴얼] 평일 오후 7시에 접수를 마감합니다.\n[매뉴얼] 예약 변경은 전화로만 받습니다.","requested_change":"프롬프트의 평일 진료 종료를 오후 8시로 바꾼다.","required_preservation":["예약 변경은 전화로만 받습니다"],"required_additions":["오후 8시"],"retired_literals":["오후 7시"]}`. 한쪽만 고치면 남은 `오후 7시` 때문에 실패하고 양쪽을 고친 결과만 통과한다. 예: `"holdout_scenario":{"base_configuration":"환불 문의에는 영수증을 먼저 요청한다.","requested_change":"배송 지연 문의에는 예상 도착일을 함께 안내한다.","required_preservation":["영수증을 먼저 요청한다"]}`. holdout 등록 가능 여부는 호스트 이름(Codex, Claude 등)으로 판단하지 않는다. 결론을 내리기 전에 반드시 `get_work_context(agent_id)`를 먼저 호출한다. `pending_recent_inputs`에 지금 사용자 메시지에 해당하는 항목이 `source_thread_id`와 함께 있으면 그 `source_thread_id`·`source_id`로 등록한다(`source_host`는 `embedded`). 해당 항목이 없으면 등록할 수 없다고 안내한다. 모델이 스스로 만든 사례나 추측한 ID로 등록하지 않는다. 이 플러그인은 외부 호스트 대화를 자동으로 수집하지 않으며, 기록은 현재 대화에서 사용자가 준 내용과 도구 응답에 한정한다.

각 case 변경에는 get_work_record에서 읽은 현재 version과 새 UUID operation_id를 사용한다. save_work_record 결과가 unknown이면 같은 operation_id로 get_work_operation을 조회하고 POST를 반복하지 않는다. 도구를 현재 호스트가 제공하지 않거나 사용자가 현재 대화에서 기록 금지를 직접 요청하면 쓰기 없이 현재 대화에서 이어간다. 저장된 UI 설정을 호스트가 확인할 수 있는지는 현재 연동의 미지원 영역이다.

## 피드백이 왔을 때 변경 범위를 잡는다

| 피드백 | 먼저 볼 근거 | 변경·확인할 범위 |
| --- | --- | --- |
| ‘너무 기계적이다’ | 실제 질문·재질문·정정·종료 대화 | 질문 묶음/순서/말투를 좁게 변경. 실제 음성으로 재확인 |
| ‘기존에는 잘 됐는데 값을 못 남긴다’ | 실패 call의 당시 버전·추출 상태와 현재 설정 | 수집 누락/분석 대기/저장 실패/설정 변경을 나눈 뒤 해당 부분만 수정 |
| ‘일단 대시보드에서 보자’ | 이전 결과 전달 합의와 새 답변 | 결과 저장·조회 위치를 갱신. 무관한 실시간 연동까지 제거하지 않음 |
| ‘A만 바꾸자’ | A의 agent-scoped Manual과 공유 도구의 연결 범위 | A의 `agent_id` 범위로 변경. 지원되는 사본/연결 방식만 사용 |
| 외부 도구가 timeout | 실제 call의 호출 입력·결과·외부 상태 | Manual 수정 전에 실행 문제로 분류. 부작용 재시도는 해당 계약으로만 판단 |

과거 실패를 현재 설정으로 설명하지 않는다. 원인이 아니라 기대값이나 시험 조건이 잘못됐을 수도 있다. 같은 가설로 실패가 반복되면 추가 근거를 확보하거나 미확인 원인을 남긴다.

## 전달물과 완료 판정

실제 생성한 대상·처리 범위·사용자가 말해볼 상황·기대 결과·결과 확인 위치·남은 의존성을 전달한다. 정상 경로 외에는 그 업무에서 중요한 정정/거절/종료/도구 실패 상황을 고른다. 예제의 기대값을 제품에서 실제 관측한 값으로 표시하지 않는다.

완료 근거를 구성 저장 / 음성 시험 / 결과 저장 확인 / 실제 전화 운영 / 외부 업무 완료로 구분한다. 현재 요청에 필요한 근거를 충족했으면 불필요한 운영 확장을 시작하지 않는다. 목표가 바뀌면 확인 기준을 바꾸되 이미 확인된 결과를 버리지 않는다.

실제 동작은 관련 Architect 스킬을 따른다. 재시험은 prepare-voice-test/try-and-improve-voice-agent, 변경 범위는 review-shared-impact, 중단 복귀는 resume-agent-work를 사용한다. 스킬 연결은 작업을 선택하는 안내이며 모든 파일을 순서대로 읽는 절차가 아니다.
