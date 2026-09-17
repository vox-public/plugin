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
[get_agent/get_manual의 실제 결과](../explore-agent-context/SKILL.md)에서 완전한 원문을 확보한다. 사용자 요청 부분과 보존할 규칙을 구분한다. 공유 리소스라면 [영향 범위](../review-shared-impact/SKILL.md)를 먼저 확인한다.

## 본문 편집
긴 문자열은 현재 원문을 파일에서 수정하고 변경 전후를 비교할 수 있다. 동일 문장이 여러 번 나오면 첫 항목을 임의 치환하지 않고 대상 문맥을 고른다. sandbox 파일 편집을 제품 저장으로 말하지 않는다.

Manual `content`는 전체 교체다. 새 본문에서 누락된 도구 참조·종료 규칙·정정 처리·내장 도구 설정을 확인한다. 파생 `tool_ids` 등을 임의로 save payload에 넣지 않는다. agent의 설정 묶음은 실제 교체 의미에 맞춰 현재 값을 보존한다. 구체 입력은 [공통 계약과 예제](../../references/workflow-examples.md)를 사용한다.

## 저장과 실패
`save_manual(mode=update)` 또는 해당 `save_agent`로 저장하고 같은 ID를 재조회한다. 저장 성공 뒤 재조회 실패는 ‘저장 응답 성공·확인 미완료’다. 새 Manual을 다시 생성하지 않는다. 이전 조회 이후 다른 변경이 보이면 다시 읽고 의도를 재적용하되 동시 수정 방지 기능이 있는 것처럼 말하지 않는다.

수정이 행동에 영향을 주면 [음성 시험](../prepare-voice-test/SKILL.md)에 재현 상황을 전달한다. 사용자가 원고 수정만 요청했다면 시험 준비/미실행을 분명히 하며 외부 전화는 시작하지 않는다.
