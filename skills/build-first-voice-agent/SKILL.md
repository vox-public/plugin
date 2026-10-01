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
기존 agent를 고치는 요청인지 새 구축인지 구분한다. 기존 대상이 있으면 [현재 상태](../explore-agent-context/SKILL.md)를 읽는다. 자료는 [근거 정리](../knowledge-grounding/SKILL.md), 업무 선택은 [음성 업무 설계](../voice-agent-design/SKILL.md)를 적용한다. 핵심 업무·방향·실제 완료 결과를 짧게 제안하고 중요한 미확정 판단만 묻는다. 새 구축이면 [유형 선택](../voice-agent-design/SKILL.md)을 적용하고, 유형과 이유를 한 줄로 알린다. 첫 `save_agent` 호출 직전 응답에 `유형: <Single + Manual n개 | Flow>. 이유: <한 문장>`을 반드시 쓴다(무인 실행이어도 쓴다). 사용자가 Flow를 지정했더라도 대화로 받는 접수·상담이 중심이면, 첫 저장 전에 'Single + Manual이 더 맞는 이유'를 한 번만 말하고 요청대로 진행한다. 기본은 Single + Manual이며 Flow로 정해지면 이 스킬 대신 [Flow 절차](../agents-platform/SKILL.md)를 따른다.

## 사용자가 준 자료 나눠 넣기
파일(이미지·PDF·CSV·엑셀·TXT)이나 웹 주소를 받으면 먼저 직접 읽고, 아래처럼 나눠 넣은 뒤 자료마다 "어디에 무엇을 넣었는지" 한 줄씩 알린다.
- **바뀔 수 있는 사실**(가격표·메뉴·진료비·운영시간·주소·FAQ): 텍스트로 정리해 `import_knowledge_documents`(`document_type=text`)로 지식에 넣고 에이전트에 연결한다. 지식이 없으면 `list_knowledges`로 찾은 뒤 `create_knowledge`로 만들고, 연결은 `save_agent`의 `data.knowledge.knowledgeIds`에 그 지식 ID를 넣어 하며 `ragEnabled`가 꺼져 있으면 함께 켠다. 표는 한 행을 한 줄 문장으로 풀어 쓴다(예: "순대 1인분 5,500원"). 프롬프트에는 한두 줄 요약만 두고, Manual 본문에는 가격·번호·주소를 쓰지 않는다("가격은 지식에서 확인해 안내한다"). 넣은 뒤 `list_knowledge_documents`로 상태를 확인하고 `get_agent`로 연결을 다시 읽는다. 지식 import는 텍스트와 URL만 받으므로 파일은 직접 읽어 텍스트로 바꿔 보낸다.
- **절차·조건·그대로 말할 문장**: Manual에 넣는다. 그대로 말할 문장은 원문 그대로 큰따옴표로 옮긴다.
- **통화 대상 목록**(CSV·엑셀): 번호 형식 오류와 중복을 정리하고 그 결과를 표로 알린 뒤 시트를 만든다. 열 이름을 `{{변수}}`로 쓰면 같은 이름을 `presetDynamicVariables`에 선언하고 값이 비었을 때 할 말을 정한다. 발신·캠페인은 사용자가 따로 요청할 때만 한다.
- **읽기 불확실한 값**(흐린 숫자, 잘린 표, 손글씨): 추측해 넣지 않고 비워 둔 뒤 확인을 요청한다.
- 사용자가 "저장만"이라고 하면 버전 생성·게시 없이 저장과 확인까지만 한다.

## 구축
1. Manual 목록(이름·트리거·제외절)과 프롬프트·Manual·지식 분담을 정한다. 아래 '프롬프트와 Manual 골격'과 '운영 수준 점검'은 반드시 지키고, 더 자세한 규칙과 예시는 [Manual 작성](../manual-authoring/SKILL.md)에 있다. 외부 동작이 필수라면 [도구 연결](../connect-agent-tools/SKILL.md)의 의존성을 먼저 확인한다.
2. 시작점을 고른다. 맞는 업무 템플릿이 있으면 `list_agent_templates` → `get_agent_template`로 내용을 확인하고 `instantiate_agent_template`(payload.name)으로 Single을 만든다. 템플릿은 자동 게시되지 않으며 부분 실패 결과를 그대로 읽는다. 템플릿의 기본 프롬프트와 Manual은 업종·방향·완료 문구가 새 업무와 충돌할 수 있으므로 그대로 두지 않고 고쳐 쓴다. 없으면 `save_agent(mode=create)`로 Single을 만들고 다시 쓴 프롬프트를 `data.prompt.prompt`에 넣는다. 반환된 `agent_id`를 보존한다.
3. `get_agent` 또는 `list_manuals`로 현재 `head_revision`을 읽은 뒤 Manual마다 `save_manual`로 본문을 저장한다(생성이면 `mode=create`와 같은 `agent_id`, `payload.expected_head_revision`, `name`, `trigger`, `content`; 템플릿이 만든 Manual은 수정). 이 호출이 Manual을 에이전트에 연결하며, Manual을 저장할 때마다 revision이 바뀌므로 다음 Manual 전에 다시 읽는다. 다른 Manual이 `@manual:<manual_id>`로 가리킬 대상은 UUID가 필요하므로 먼저 저장한다. 폐기된 `manualIds`를 agent payload에 만들지 않는다. Manual이 쓰는 내장 도구는 본문에서 `@tool:이름`, API 도구는 `list_tools`가 돌려준 `@tool:<tool_id>`로 참조해야 실행된다.
4. `list_manuals`로 Manual 수와 진단 건수를, `get_manual(agent_id, manual_id)`와 `get_agent(agent_id)`로 본문·참조·현재 revision을 재조회한다. 자료는 [지식](../knowledge-grounding/SKILL.md)(텍스트·URL), 외부 연동은 [도구](../connect-agent-tools/SKILL.md), 내부 추출·저장은 [결과 설정](../configure-call-results/SKILL.md)으로 연결한다. 실제 입력·ID 흐름은 [완성된 합성 여정](../../references/workflow-examples.md)에 있다. 그다음 아래 '운영 수준 점검' 1~8을 다시 읽은 본문에 대고 확인하고, 어긋난 Manual은 고친다.
5. 저장한 상태를 `create_agent_version`으로 버전에 남긴다(반환된 버전 번호 보존, `list_agent_versions`로 확인). 운영에 쓰려면 사용자에게 어느 버전을 production으로 지정할지 요약해 확인받고 `publish_agent_version`을 호출한 뒤 `get_agent`(production)로 재조회한다. 게시는 번호·발신 경로에 바로 영향을 주며 모든 의존성의 불변 게시가 아니다.
6. 이미 가진 번호에 연결하려면 [번호 연결](../connect-phone-service/SKILL.md), 발신하려면 [발신 운영](../operate-outbound-and-followup/SKILL.md), 결과 확인은 [통화 근거](../inspect-call-evidence/SKILL.md)로 이어간다. 음성 시험은 [직접 음성 시험](../prepare-voice-test/SKILL.md)에서 고객이 직접 한다. 번호 획득은 웹에서만 하며 첫 체험의 필수 단계가 아니다.

## 프롬프트와 Manual 골격
프롬프트(보통 1,500~4,000자)는 모든 업무에 공통인 것만 담는다.
```
# 역할
# 말투와 발화: 한 턴에 질문 하나, 이미 들은 값은 다시 묻지 않음, 숫자 읽는 법, 큰따옴표 문장은 그대로 말함, 대괄호는 실제 값으로 바꿔 말함
# 공통 규칙: 모든 업무의 금지와 범위 밖 응대
# Manual 선택: ① 위급·안전 ② 진행 중인 Manual 계속 ③ 트리거가 하나만 맞으면 그 Manual ④ 없으면 용건을 한 번 묻기
# 마무리: 더 필요한 것 묻기 → 끝인사 → 종료 도구. 고객이 말을 마치기 전에 끊지 않는다
```
Manual 하나는 고객 의도 하나다(보통 3~10개).
```
## 규칙
- 범위: 하는 일 / 하지 않는 일(→ @manual:<id>)
- 완료 조건: 무엇이 확인돼야 완료라고 말하는가
## 진행 절차
### 시작
1. 고객이 이미 말한 값은 확인만 하고 다음 단계로 간다.
### <단계 이름>
1. 질문 하나.
   - <조건>: <행동>
   - 답이 없거나 불분명하면 한 번 다시 묻는다. 그래도 안 되면 <행동>.
   - 말하기를 거절하면 <행동>.
### <도구 결과 처리>
1. 언제: <조건>. 입력: <값의 출처>. @tool:<이름 또는 tool_id>를 부른다.
   - 성공: <행동> / 없음: <행동> / 실패·지연: 다시 부르지 않고 <대안>.
### 완료
1. 완료 조건을 확인한 뒤 결과를 알리고, 마무리 인사 뒤 <종료 도구>.
```

## 운영 수준 점검
Manual을 쓸 때 지키고, 저장한 뒤 `get_agent`·`get_manual`로 다시 읽어 하나씩 확인한다.
1. 질문 단계마다 "답이 없거나 불분명하면 한 번 다시 묻고, 그래도 안 되면 …" 가지를 둔다. 정보 제공 거절, 정정, 범위 밖 요청에도 할 행동을 적는다.
2. 도구 호출마다 언제·입력·결과별 행동(성공/없음/실패·지연)을 쓰고, "실패하면 다시 부르지 않고 …(메모·콜백·안내)"를 적는다. "완료·접수·전송했다"는 성공 결과를 받은 뒤에만 말한다. 전환·문자·등록처럼 부작용이 있는 도구는 고객이 동의한 뒤 부른다.
3. 순서가 중요한 곳은 게이트("…을 확인하기 전에는 …하지 않는다")로, 반복은 상한("최대 2회. 넘으면 …")으로 쓴다.
4. 상담원 연결·연락처 확인처럼 두 Manual 이상이 쓰는 단계는 공용 Manual 하나에 두고 `@manual:<id>`로 넘긴다. 마무리 인사 문장은 프롬프트 `# 마무리`에 한 번만 쓰고, Manual 완료 단계에는 결과에 맞는 종료 도구만 적는다.
5. 프롬프트에 둔 규칙(금지·말투·정해진 거절 문구)을 Manual에 다시 쓰지 않는다. 같은 대상(Manual·종료 도구)은 늘 같은 이름으로 부른다.
6. 내용이 가까운 형제 Manual의 트리거에는 "…은 제외한다(○○ 담당)"를 붙인다.
7. `{{변수}}`를 쓰면 `presetDynamicVariables`에 선언하고, 값이 비었을 때 할 말을 적는다.
8. 위급·안전 신호(통증·사고·누출 등)는 접수 Manual 끝에 묻어 두지 않고, 연결 도구를 가진 별도 진입 Manual로 둔다.

어긋난 곳은 같은 `manual_id`(또는 `agent_id`)로 고친 뒤, 사용자에게 "점검: ○○ 보완" 한 줄로 알린다.

## 부분 성공과 전달
Single만 저장됐다면 그 `agent_id`에서 Manual 생성 단계를 계속한다. Manual 저장 성공 뒤에는 같은 `agent_id`·`manual_id`로 확인한다. 게시 응답이 불명이면 `list_agent_versions`/`get_agent`로 production 상태를 읽고 다시 호출하지 않는다. `409` revision conflict는 최신 상태를 다시 읽고 의도를 다시 적용할 때만 처리하며, unknown 응답은 새 Single·Manual 생성이나 같은 쓰기로 자동 재시도하지 않는다. Agent 저장 성공을 시험 성공으로 보고하지 않는다. 실제 예약이 목표인데 연동이 없으면 그 결손을 알리고 사용자 목표를 유지한다.

전달은 agent/Manual 참조, 처리 범위, 시험 상황, 결과 위치, 현재 완료 단계와 남은 의존성으로 구성한다. 사용자가 변경 의견을 주면 해당 전문 스킬을 읽어 필요한 부분만 고친다. 가정한 값(번호·시간·정책)과 고객 확인이 필요한 문구는 따로 목록으로 적고, 시험 방법과 다음 할 일(시험 → 번호 연결 → 게시 확인 → 출시 뒤 통화 점검)을 짧게 안내한다.

## 업무 판단

첫 업무 선택·외부 의존성·질문 범위는 [업무 판단 기준](../../references/workflow-guidance.md)을 읽는다. 고객의 중요도, 자료에서 보이는 반복성과 업무 경계, 지금 확인 가능한 결과를 비교해 첫 완료 지점을 제안한다. 기술 설정 설문으로 시작하지 않는다. 독립적인 준비는 진행하고, 결정을 기다려야 하는 실행은 구분한다.

내부 접수가 목표라면 Manual의 질문과 추출·저장 필드를 함께 설계한다. 실제 예약이 목표라면 필요한 조회/등록 도구가 없는 상태를 숨기지 않는다. 음성 시험 도구는 없으므로 고객이 직접 확인할 사례와 남은 단계를 구분해 전달한다. 번호 연결·발신·통화 조회는 연결된 도구가 목록에 있을 때 위 단계로 진행하고, 없으면 해당 단계가 막혔다고 알린다.
