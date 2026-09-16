---
name: manual-authoring
description: "vox.ai Single용 Manual의 질문·조건·정정·도구 사용·마무리를 작성하거나 긴 프롬프트를 재구성할 때 사용한다. 기존 제품 본문 저장은 별도 편집 스킬로 수행한다."
metadata:
  product: vox.ai
  layer: general
  status: authoring-draft-not-runtime-verified
---

# manual-authoring

## Manual의 역할
Manual은 고객과 대화하는 음성 에이전트의 업무 절차다. 코파일럿을 위한 SKILL.md와 다르다. 초기에는 완결된 Manual 하나를 만들고 독립 재사용·시험 가치가 생길 때 분리한다. Flow나 ElevenLabs의 procedure draft/compile을 도입하지 않는다.

## 작성 순서
1. 시작 조건과 처리 범위를 적고 알려진 사전 정보를 확인한다. 아웃바운드는 연락 이유·통화 가능 여부·거절을, 인바운드는 문의 목적·분류를 포함한다.
2. 목표 달성에 필요한 질문을 순서와 조건으로 표현한다. 이미 답한 내용은 재질문하지 않고 정정된 값으로 요약을 갱신한다.
3. 도구 호출 조건, 필요한 입력, 성공의 근거, 실패/무응답 시 대응을 함께 쓴다. 존재하지 않는 도구 참조나 예약 기능을 적지 않는다.
4. 종료 전 고객에게 확인할 요약과 실제 결과를 구분한다. 종료 동작은 현재 제품의 지원 참조 문법·내장 도구 설정으로 연결한다.

## 좋은 원고의 기준
‘친절히 처리한다’만 쓰지 말고 결정에 필요한 조건을 적는다. 가격·정책·가용 시간을 출처 없이 채우지 않는다. 도구의 성공 응답 전 완료를 약속하지 않는다. 필수 단계가 순서대로 실행됐는지는 실제 시험에서 확인한다. prose만으로 결정적 상태 머신을 만들었다고 말하지 않는다.

정정/정보 제공 거절/범위 밖 요청/도구 실패 중 업무에 해당하는 사례를 붙인다. 과거 원고를 분리할 때 각 규칙의 새 위치를 표시하고 빠진 종료·예외를 점검한다.

저장은 [edit-manual-safely](../edit-manual-safely/SKILL.md), 근거 자료 정리는 [knowledge-grounding](../knowledge-grounding/SKILL.md)를 사용한다.
