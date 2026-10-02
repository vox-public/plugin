# Flow 업무 계약: 조회·확인·결과 기록

[Flow 설계](../skills/voice-agent-design/SKILL.md)로 정해진 업무에서만 적용한다. 아래 이름과 값은 가상 예시다. 사용자가 준 작업 명세·API 계약이 있으면 그 필드명과 enum을 그대로 사용한다. 없는 API를 구현했다고 보고하지 않는다.

## 문항·단계별 결과
생성 전에 각 문항의 결과 변수와 저장 payload를 표로 정한다. 예: `q1_result`(string: 명세의 enum), `q1_said`(string: 정규화 답), `q1_reprompt_count`(number: 실제 재안내 수), `q1_failure_reason`(string: 명세의 사유), 재안내 결과 `q1_r_result`. 모든 문항에 같은 규칙을 적용하고 복수 상품은 상품별 결과를 보존한다. 명세가 `question_id`, `interpreted_answer`, `validation_result`, `reprompt_count`, `failure_reason`, `callback_required`, `completed`를 요구하면 그 이름으로 매핑한다. 미도달·불명확·명확한 NO·불일치를 성공으로 채우지 않는다.

전체 기록은 실패 단계(`failure_stage`), 사유(`failure_reason`), 실제 재안내 수(`reprompt_count`), 문항별 결과(`answers`)와 `outcome`을 포함한다. 명세가 `COMPLETED`, `CALLBACK`, `WRONG_NUMBER`라면 대소문자까지 그대로 쓴다. `callback_required`를 outcome 대신 쓰지 않는다. 전체 확인 성공일 때만 완료로 기록한다. 실패 종료 직전에 해당 단계와 사유를 보존하고 마지막 요약 추출로 앞 단계 결과를 덮어쓰지 않는다. 통화 후 분석 문구만으로 통화 중 API 기록을 대체하지 않는다. 저장 응답의 성공 근거도 확인한다.

**저장 전 점검: 문항·재안내 결과, 실패 단계·사유·실제 횟수, outcome과 payload 필드명이 작업 명세의 이름·값과 정확히 같은가?**

## 연결 실패 복귀
실패 뒤 접수 또는 대표 연결이 요구되면 원본 `transferCall`은 `transfer_type: "warm"`으로 하고 실패 `fallback` edge를 해당 경로에 연결한다. cold는 쓰지 않는다. 대표 연결 실패는 명세의 종료·접수 정책을 따른다. validator 통과만으로 warm을 보장하지 않으므로 저장 뒤 원본을 다시 읽는다. mock 사전 연결 확인 성공은 실제 cold 실패 복귀를 입증하지 않는다.

## 중복 조회의 재조회
후보가 여러 건이면 구 같은 상위 조건을 질문하고 extraction으로 뽑은 뒤 **같은 조회 API에 기존 조건과 새 조건을 합쳐 다시 조회**한다. 첫 후보를 고르거나 fallback API에 조건을 보내 놓고 재조회라고 하지 않는다. 재조회 결과가 하나일 때만 응답의 목적지 변수를 연결 인자로 사용한다. 0건·여러 건·오류는 명세의 대표 경로로 가고 무한 재질문하지 않는다.

먼저 실제 mock/API의 method·입력 계약에서 재조회가 가능한지 확인한다. GET body는 런타임에서 전달되지 않는다. GET 쿼리 계약이면 1차 URL은 정의된 동 변수만, 2차 URL은 동·구를 모두 추출해 정의한 경로에서만 호출한다. 미정의 URL 쿼리 변수는 fallback 대신 통화를 끝낼 수 있으므로 1차 URL에 아직 없는 구 변수를 넣지 않는다. URL 쿼리가 금지된 시험 계약이라면 GET body나 미지원 POST로 우회하지 않는다. "현재 계약으로 상위 조건을 합친 재조회는 지원하지 않는다"고 보고하고 필요한 계약을 명시한다.

logic의 오른쪽 `{{변수}}`는 치환되지 않아 변수끼리 비교가 거짓이 될 수 있다. extraction/API가 만든 상태 코드를 `MATCH`, `MISMATCH`, `NO`, `UNCLEAR` 같은 **리터럴**에 비교한다. 실제 노드·edge·응답 매핑은 최신 MCP schema를 확인한다.

## 등록값 비교
주소·날짜처럼 표기가 흔들리는 값은 AI edge에 원문끼리 비교하라는 지시만 넣지 않는다. extraction에서 고객 답과 등록값을 같은 규칙으로 정규화하고 비교 결과와 정규화 답을 함께 추출한다. 가상 주소 `일 동 이 호`와 `1동 2호`는 동·호 구성요소로 정규화하되 address2의 동·호가 빠지면 MATCH로 만들지 않는다. 추출 프롬프트에 등록값과 address2 포함 조건을 명시하고 logic은 결과 리터럴로 분기한다. LLM 추출은 결정적 검증을 보장하지 않으므로 정확한 주소·누락·다른 호수·정정 사례를 시험한다. 검증 API가 실제 계약에 있으면 정규화 답과 등록값을 보내 결과로 분기한다. 없는 검증 API를 연결했다고 하지 않는다.

## mock·채팅 시험
모든 mock/API 노드에 같은 조합 사례 헤더 `X-Fixture-Case: {{fixture_case}}`와 추적 헤더 `X-Trace: {{chat_id}}`를 넣는다. 조회·연결·문자·접수·결과 기록·fallback도 빠짐없이 적용하고 단계별 case 변수로 나누지 않는다. 실제 서비스 API는 헤더 계약을 확인한다.

채팅 생성 요청의 `dynamic_variables`에 **필요 입력 전체**를 명시한다. preset이 자동 적용된다고 가정하지 않는다. 가상 ARS는 `last_menu`, `unknown_count`, 시각 분기 시 `current_time`, mock의 `fixture_case`가 필요하다. 등록값 확인 업무는 계약자·학습자 이름/생년월일/관계/성별, `address1`, `address2`, 상품 목록·유형·개수, 라이프 제휴 값 등 그래프에서 읽는 사전 입력을 모두 열거한다. 실제 API 반환값과 extraction 출력은 사전 입력과 구분하고 성공값을 미리 심지 않는다. `chat_id`는 서버 주입값이다. 입력→노드→변수→기록 매핑을 저장 보고에 남긴다.

전환·문자는 별도 mock 시험 변형을 사용하고 원본을 보존한다. 연결 완료는 같은 trace의 mock 성공 응답과 런타임 수신·자연 종료로 확인한다. 음성 접수는 최종 요약 확인에 "네, 맞아요"로 답한 뒤 저장 응답까지 확인한다. 그래프 저장·정적 예상 경로·실행 결과를 구분해 보고한다.
