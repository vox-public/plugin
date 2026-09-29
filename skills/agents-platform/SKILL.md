---
name: agents-platform
description: "연결된 vox.ai Agents MCP에서 조직·현재 도구 capability와 작업 context를 확인하고 agent·Manual 작업을 수행할 때 적용한다. 상담원의 실시간 통화 업무에는 적용하지 않는다."
metadata:
  product: vox.ai
  layer: mcp
  status: preview
---

# agents-platform

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 제품 모듈 선택
이 스킬은 Agents 제품의 연결과 도구 사용을 안내한다. 사용자의 요청이 음성 agent 구축·시험·통신 운영이면 이 모듈을 선택한다. desk의 상담원 수신·이어받기·상담원 발신 요청을 비슷한 이름의 Agents 도구에 넘기지 않는다. 현재 연결에서 지원 여부를 확인하고 미지원 범위를 알려준다. 현재 번들의 구현 기준은 [워크플로 capability 표](../../references/workflow-capabilities.json)다.

## 연결과 발견
호스트에서 제공하는 인증 절차를 사용한다. 키나 토큰을 프롬프트/파일에 요구하지 않는다. 연결 조직은 고정이며 모델 인자로 전환하지 않는다. 조직 변경은 호스트의 연결 UX로 처리한다.

호스트가 실제 제공한 MCP 도구 이름과 스키마를 먼저 확인한다. 이름 검색 후 정확한 ID를 확보한다. `list_models`, `list_schemas`, `get_schema`는 제품 설정 탐색용이며 호스트의 MCP 도구 발견 기능과 혼동하지 않는다. 여러 서버가 있으면 연결 식별자와 제품 모듈을 함께 확인한다. Manual은 Single에 귀속되므로 `list_agents`로 대상을 정하고 `list_manuals` 또는 `get_manual`로 같은 `agent_id` 범위의 현재 Manual을 읽는다.

## 도구 선택
- 구축: `list_agents`, `get_agent`, `list_manuals`, `get_manual`, `save_agent`, `save_manual`. 생성/수정 mode와 연결된 서버의 실제 payload를 사용한다. Manual 저장에는 `agent_id`와 현재 `head_revision`에 해당하는 `expected_head_revision`을 포함한다. Agent 수정에도 현재 `head_revision`을 사용한다.
- 현재 번들에는 조직·agent·Manual·모델·설정 schema 10개와 work context·record·operation 도구 4개의 schema 후보가 있다. 실제 사용 가능 여부는 연결된 서버의 목록과 schema로 확인한다. 직접 음성 시험, call history, 발신, 번호, 캠페인, SMS, 채팅과 위젯 동작은 포함되지 않는다. 예제와 schema 검증은 [합성 고객 여정](../../references/workflow-examples.md)을 따른다.
- 호스트가 추가 tool을 실제로 노출하면 그 tool list와 입력 schema를 확인한 뒤 해당 업무를 진행한다. agent 저장이 실고객 발신을 허가하지 않고, plugin의 skill 목록만으로 구현 여부를 추정하지 않는다.

## Context와 기록

다음 작업에 영향을 줄 결정, 고객 피드백, 확인된 제품 변경, 미완료 다음 단계가 생기면 get_work_context와 get_work_record로 관련 case를 확인하고 save_work_record로 필요한 요약을 기록한다. “기억해” 같은 키워드를 요구하지 않는다. get_work_context의 background_settings로 자동 기록 상태와 revision/epoch를 확인하고 routine case/event에 최신 값을 전달한다. 기본은 켜짐이며 OFF이면 routine 자동 기록을 중단한다. 사용자가 명시적으로 요청한 기존 기록 조회·정정·삭제는 OFF와 별개로 지원한다. 사용자가 현재 대화에서 저장하지 말라고 직접 요청하면 기록하지 않는다. 외부 통화 transcript 전체를 수집하지 않고 간결한 보고와 최소 locator만 남긴다. 고객 음성 결과는 reported evidence로 유지하며 text_contract 평가를 고객 voice 결과로 표시하지 않는다.

user-principal save_agent 또는 save_manual을 호출하기 직전에 매번 get_work_context를 실행하고, 결과의 context_receipt.token을 다음 한 번의 저장에 최상위 context_receipt로 전달한다. receipt를 재사용하지 않는다. 실제 도구 목록이나 schema에 context/receipt가 없으면 초안만 준비하고 제품 쓰기는 하지 않는다.

## 응답과 복귀
저장/접수/최종 완료/부분 실패/불명을 분리한다. 저장 성공 뒤 조회가 실패했다면 받은 `agent_id`와 `manual_id`부터 이어간다. `409` conflict는 현재 상태를 다시 읽고 사용자의 변경 의도를 다시 적용할 때만 처리하며 무조건 재시도하지 않는다. 쓰기 응답이 불명이면 새 생성이나 같은 쓰기를 반복하지 말고 [resume-agent-work](../resume-agent-work/SKILL.md)로 지원되는 조회를 이어간다. OAuth 만료를 조직 전체 키나 직접 REST로 우회하지 않는다.

스킬 부재를 제품 접근 차단 사유로 만들지 않는다. 도구 설명·스키마만으로도 지원 업무를 수행할 수 있어야 한다. 세부 업무 판단은 관련 Architect 스킬, 개념·작성 품질은 general을 필요할 때 읽는다.
