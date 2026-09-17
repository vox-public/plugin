---
name: agents-platform
description: "연결된 vox.ai Agents MCP에서 조직·도구를 확인하고 에이전트·Manual·통화·번호·캠페인 업무 도구를 사용할 때 적용한다. 상담원의 실시간 통화 업무에는 적용하지 않는다."
metadata:
  product: vox.ai
  layer: mcp
  status: preview
---

# agents-platform

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 제품 모듈 선택
이 스킬은 Agents 제품의 연결과 도구 사용을 안내한다. 사용자의 요청이 음성 agent 구축·시험·통신 운영이면 이 모듈을 선택한다. desk의 상담원 수신·이어받기·상담원 발신 요청을 비슷한 이름의 Agents 도구에 넘기지 않는다. 현재 연결에서 지원 여부를 확인하고 미지원 범위를 알려준다.

## 연결과 발견
호스트에서 제공하는 인증 절차를 사용한다. 키나 토큰을 프롬프트/파일에 요구하지 않는다. 연결 조직은 고정이며 모델 인자로 전환하지 않는다. 조직 변경은 호스트의 연결 UX로 처리한다.

호스트가 실제 제공한 MCP 도구 이름과 스키마를 먼저 확인한다. 이름 검색 후 정확한 ID를 확보한다. `list_models`, `list_schemas`, `get_schema`는 제품 설정 탐색용이며 호스트의 MCP 도구 발견 기능과 혼동하지 않는다. 여러 서버가 있으면 연결 식별자와 제품 모듈을 함께 확인한다.

## 도구 선택
- 구축: `get_agent`, `get_manual`, `save_agent`, `save_manual`. 생성/수정 mode와 API payload를 사용한다.
- 통화: `list_calls`, `get_call`; 실제 발신은 별도 `place_call`. agent 저장이 실고객 발신을 허가하지 않는다.
- 번호·캠페인·SMS·채팅·위젯은 [업무 호출 예](../../references/workflow-examples.md)의 목적별 도구를 실제 스키마로 확인한다.
- 직접 음성은 `open_voice_test_session`의 구현된 진입/결과 계약을 확인한다. 마이크를 MCP가 처리하지 않는다.

## 응답과 복귀
저장/접수/최종 완료/부분 실패/불명을 분리한다. 저장 성공 뒤 조회가 실패했다면 받은 ID부터 이어간다. 실행 응답이 불명이면 [resume-agent-work](../resume-agent-work/SKILL.md)를 사용한다. OAuth 만료를 조직 전체 키나 직접 REST로 우회하지 않는다.

스킬 부재를 제품 접근 차단 사유로 만들지 않는다. 도구 설명·스키마만으로도 지원 업무를 수행할 수 있어야 한다. 세부 업무 판단은 관련 Architect 스킬, 개념·작성 품질은 general을 필요할 때 읽는다.
