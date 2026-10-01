---
name: build-first-voice-agent
description: "URL·파일·설명으로 vox.ai의 첫 Single 음성 에이전트를 만들고 Manual·결과 저장·직접 시험까지 연결할 때 사용한다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# build-first-voice-agent

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다. 현재 구현 capability는 [구현 도구 스냅샷](../../references/implemented-tools.snapshot.json)과 [워크플로 capability 표](../../references/workflow-capabilities.json)에 있다.

## 먼저 읽을 상태와 판단
기존 agent를 고치는 요청인지 새 구축인지 구분한다. 기존 대상이 있으면 [현재 상태](../explore-agent-context/SKILL.md)를 읽는다. 자료는 [근거 정리](../knowledge-grounding/SKILL.md), 업무 선택은 [음성 업무 설계](../voice-agent-design/SKILL.md)를 적용한다. 핵심 업무·방향·실제 완료 결과를 짧게 제안하고 중요한 미확정 판단만 묻는다. 새 구축이면 [유형 선택](../voice-agent-design/SKILL.md)을 적용하고, 첫 `save_agent` 전에 고른 유형과 이유를 한 줄로 알린다(예: ‘유형: Single + Manual 3개. 이유: 대화로 받는 접수이고 키패드 메뉴나 원문 낭독이 없습니다’). 기본은 Single + Manual이며 Flow로 정해지면 이 스킬 대신 [Flow 절차](../agents-platform/SKILL.md)를 따른다.

## 구축
1. [Manual 작성](../manual-authoring/SKILL.md)으로 고객 의도별 Manual 목록(이름·트리거)을 정하고, 프롬프트·Manual·지식에 무엇을 둘지 나눈다. 각 Manual은 정상·정정·거절·범위 밖·마무리를 갖춘다. 외부 동작이 필수라면 [도구 연결](../connect-agent-tools/SKILL.md)의 의존성을 먼저 확인한다.
2. 시작점을 고른다. 맞는 업무 템플릿이 있으면 `list_agent_templates` → `get_agent_template`로 내용을 확인하고 `instantiate_agent_template`(payload.name)으로 Single을 만든다. 템플릿은 자동 게시되지 않으며 부분 실패 결과를 그대로 읽는다. 템플릿의 기본 프롬프트와 Manual은 업종·방향·완료 문구가 새 업무와 충돌할 수 있으므로 그대로 두지 않고 고쳐 쓴다. 없으면 `save_agent(mode=create)`로 Single을 만들고 다시 쓴 프롬프트를 `data.prompt.prompt`에 넣는다. 반환된 `agent_id`를 보존한다.
3. `get_agent` 또는 `list_manuals`로 현재 `head_revision`을 읽은 뒤 Manual마다 `save_manual`로 본문을 저장한다(생성이면 `mode=create`와 같은 `agent_id`, `payload.expected_head_revision`, `name`, `trigger`, `content`; 템플릿이 만든 Manual은 수정). 이 호출이 Manual을 에이전트에 연결하며, Manual을 저장할 때마다 revision이 바뀌므로 다음 Manual 전에 다시 읽는다. 폐기된 `manualIds`를 agent payload에 만들지 않는다. Manual이 쓰는 내장 도구는 본문에서 `@tool:이름`으로 참조해야 실행된다.
4. `list_manuals`로 Manual 수와 진단 건수를, `get_manual(agent_id, manual_id)`와 `get_agent(agent_id)`로 본문·참조·현재 revision을 재조회한다. 자료는 [지식](../knowledge-grounding/SKILL.md)(텍스트·URL), 외부 연동은 [도구](../connect-agent-tools/SKILL.md), 내부 추출·저장은 [결과 설정](../configure-call-results/SKILL.md)으로 연결한다. 실제 입력·ID 흐름은 [완성된 합성 여정](../../references/workflow-examples.md)에 있다.
5. 저장한 상태를 `create_agent_version`으로 버전에 남긴다(반환된 버전 번호 보존, `list_agent_versions`로 확인). 운영에 쓰려면 사용자에게 어느 버전을 production으로 지정할지 요약해 확인받고 `publish_agent_version`을 호출한 뒤 `get_agent`(production)로 재조회한다. 게시는 번호·발신 경로에 바로 영향을 주며 모든 의존성의 불변 게시가 아니다.
6. 이미 가진 번호에 연결하려면 [번호 연결](../connect-phone-service/SKILL.md), 발신하려면 [발신 운영](../operate-outbound-and-followup/SKILL.md), 결과 확인은 [통화 근거](../inspect-call-evidence/SKILL.md)로 이어간다. 음성 시험은 [직접 음성 시험](../prepare-voice-test/SKILL.md)에서 고객이 직접 한다. 번호 획득은 웹에서만 하며 첫 체험의 필수 단계가 아니다.

## 부분 성공과 전달
Single만 저장됐다면 그 `agent_id`에서 Manual 생성 단계를 계속한다. Manual 저장 성공 뒤에는 같은 `agent_id`·`manual_id`로 확인한다. 게시 응답이 불명이면 `list_agent_versions`/`get_agent`로 production 상태를 읽고 다시 호출하지 않는다. `409` revision conflict는 최신 상태를 다시 읽고 의도를 다시 적용할 때만 처리하며, unknown 응답은 새 Single·Manual 생성이나 같은 쓰기로 자동 재시도하지 않는다. Agent 저장 성공을 시험 성공으로 보고하지 않는다. 실제 예약이 목표인데 연동이 없으면 그 결손을 알리고 사용자 목표를 유지한다.

전달은 agent/Manual 참조, 처리 범위, 시험 상황, 결과 위치, 현재 완료 단계와 남은 의존성으로 구성한다. 사용자가 변경 의견을 주면 해당 전문 스킬을 읽어 필요한 부분만 고친다.

## 업무 판단

첫 업무 선택·외부 의존성·질문 범위는 [업무 판단 기준](../../references/workflow-guidance.md)을 읽는다. 고객의 중요도, 자료에서 보이는 반복성과 업무 경계, 지금 확인 가능한 결과를 비교해 첫 완료 지점을 제안한다. 기술 설정 설문으로 시작하지 않는다. 독립적인 준비는 진행하고, 결정을 기다려야 하는 실행은 구분한다.

내부 접수가 목표라면 Manual의 질문과 추출·저장 필드를 함께 설계한다. 실제 예약이 목표라면 필요한 조회/등록 도구가 없는 상태를 숨기지 않는다. 음성 시험 도구는 없으므로 고객이 직접 확인할 사례와 남은 단계를 구분해 전달한다. 번호 연결·발신·통화 조회는 연결된 도구가 목록에 있을 때 위 단계로 진행하고, 없으면 해당 단계가 막혔다고 알린다.
