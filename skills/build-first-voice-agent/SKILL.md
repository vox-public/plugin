---
name: build-first-voice-agent
description: "URL·파일·설명으로 vox.ai의 첫 Single 음성 에이전트를 만들고 Manual·결과 저장·직접 시험까지 연결할 때 사용한다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# build-first-voice-agent

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 먼저 읽을 상태와 판단
기존 agent를 고치는 요청인지 새 구축인지 구분한다. 기존 대상이 있으면 [현재 상태](../explore-agent-context/SKILL.md)를 읽는다. 자료는 [근거 정리](../knowledge-grounding/SKILL.md), 업무 선택은 [음성 업무 설계](../voice-agent-design/SKILL.md)를 적용한다. 핵심 업무·방향·실제 완료 결과를 짧게 제안하고 중요한 미확정 판단만 묻는다.

## 구축
1. [Manual 작성](../manual-authoring/SKILL.md)으로 정상·정정·거절·범위 밖·마무리를 갖춘 본문을 준비한다. 외부 동작이 필수라면 [도구 연결](../connect-agent-tools/SKILL.md)의 의존성을 먼저 확인한다.
2. 먼저 `save_agent(mode=create)`로 Single을 만들고 반환된 `agent_id`를 보존한다. `get_agent` 또는 `list_manuals`로 현재 `head_revision`을 읽은 뒤 `save_manual(mode=create)`에 같은 `agent_id`와 `payload.expected_head_revision`을 전달한다. Manual은 해당 Single에 저장되며 폐기된 `manualIds`를 agent payload에 만들지 않는다.
3. Manual 생성 응답의 `manual_id`를 보존하고 `get_manual(agent_id, manual_id)`와 `get_agent(agent_id)`로 본문·참조·현재 revision을 재조회한다. [결과 설정](../configure-call-results/SKILL.md)으로 내부 추출·저장을 포함한다. 구체 입력·ID 흐름은 [대표 호출 예](../../references/workflow-examples.md)에 있다.
4. [직접 음성 시험](../prepare-voice-test/SKILL.md)으로 이어간다. 번호 구매와 CRM 구축은 첫 브라우저 체험의 필수 단계가 아니다.

## 부분 성공과 전달
Single만 저장됐다면 그 `agent_id`에서 Manual 생성 단계를 계속한다. Manual 저장 성공 뒤에는 같은 `agent_id`·`manual_id`로 확인한다. `409` revision conflict는 최신 상태를 다시 읽고 의도를 다시 적용할 때만 처리하며, unknown 응답은 새 Single·Manual 생성이나 같은 쓰기로 자동 재시도하지 않는다. Agent 저장 성공을 시험 성공으로 보고하지 않는다. 실제 예약이 목표인데 연동이 없으면 그 결손을 알리고 사용자 목표를 유지한다.

전달은 agent/Manual 참조, 처리 범위, 시험 상황, 결과 위치, 현재 완료 단계와 남은 의존성으로 구성한다. 사용자가 변경 의견을 주면 해당 전문 스킬을 읽어 필요한 부분만 고친다.

## 업무 판단

첫 업무 선택·외부 의존성·질문 범위는 [업무 판단 기준](../../references/workflow-guidance.md)을 읽는다. 고객의 중요도, 자료에서 보이는 반복성과 업무 경계, 지금 확인 가능한 결과를 비교해 첫 완료 지점을 제안한다. 기술 설정 설문으로 시작하지 않는다. 독립적인 준비는 진행하고, 결정을 기다려야 하는 실행은 구분한다.

내부 접수가 목표라면 Manual의 질문과 추출·저장 필드를 함께 설계한다. 실제 예약이 목표라면 필요한 조회/등록이 없는 상태를 숨기지 않는다. 구축 후 대상·시험 발화·기대 결과·확인 위치를 묶어 전달하고 아직 검증하지 않은 운영 연결을 남긴다.
