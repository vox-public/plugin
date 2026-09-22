---
name: edit-manual-safely
description: "기존 vox.ai Manual이나 agent의 긴 prompt 문구를 일부 수정할 때 사용한다. 기존 내용·참조·공유 범위를 보존하고 저장 후 실제 본문을 확인한다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# edit-manual-safely

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 쓰기 전
[get_agent/get_manual의 실제 결과](../explore-agent-context/SKILL.md)에서 대상 Single의 `agent_id`, Manual의 `manual_id`, 현재 `head_revision`, 완전한 원문을 확보한다. 사용자 요청 부분과 보존할 규칙을 구분한다. 다른 agent와의 영향이 의심되면 [영향 범위](../review-shared-impact/SKILL.md)를 먼저 확인한다.

## 본문 편집
긴 문자열은 현재 원문을 파일에서 수정하고 변경 전후를 비교할 수 있다. 동일 문장이 여러 번 나오면 첫 항목을 임의 치환하지 않고 대상 문맥을 고른다. sandbox 파일 편집을 제품 저장으로 말하지 않는다.

Manual `content`는 전체 교체다. 새 본문에서 누락된 도구 참조·종료 규칙·정정 처리를 확인한다. `tool_ids`, `linked_manual_ids` 같은 파생 필드를 임의로 save payload에 넣지 않는다. Agent 설정의 `data.manuals`는 UUID 키를 사용하며 이를 보낼 때 현재 Manual 값을 보존한다. 구체 입력은 [공통 계약과 예제](../../references/workflow-examples.md)를 사용한다.

## 저장과 실패
`save_manual(mode=update)` 또는 해당 `save_agent`에 방금 읽은 `expected_head_revision`을 포함해 저장하고 같은 `agent_id`·`manual_id`를 재조회한다. 저장 성공 뒤 재조회 실패는 ‘저장 응답 성공·확인 미완료’다. `409` conflict면 현재 값을 다시 읽고 사용자 의도를 재적용한다. unknown 쓰기나 재조회 실패 뒤 새 Manual을 만들거나 같은 쓰기를 자동 재실행하지 않는다.

수정이 행동에 영향을 주면 [음성 시험](../prepare-voice-test/SKILL.md)에 재현 상황을 전달한다. 사용자가 원고 수정만 요청했다면 시험 준비/미실행을 분명히 하며 외부 전화는 시작하지 않는다.
