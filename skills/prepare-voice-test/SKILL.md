---
name: prepare-voice-test
description: "고객이 vox.ai 에이전트를 직접 음성 시험하도록 준비하고 기대 결과와 고객 보고 또는 조회 가능한 통화 근거를 구분할 때 사용한다. 고객용 자동 시뮬레이션 플랫폼은 생성하지 않는다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# prepare-voice-test

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 준비
agent·대상 버전·해당 Single의 agent-scoped Manual을 확인한다. 현재 구현 도구가 조회를 제공하지 않으면 사용자가 준 정보만 사용하고 이를 표시한다. 자료가 아웃바운드 업무면 합성 사전 정보를 사용해 도입/거절을 시험할 수 있는지 현재 진입 경로를 확인한다. 실고객 데이터나 실제 발신을 기본값으로 쓰지 않는다.

[시험 사례](../../references/voice-test-cases.md)에서 목표에 맞는 정상/변경/오류 상황을 고른다. 시험 대화와 기대 저장값을 짝짓고 브라우저 음성으로 확인할 것과 실제 전화로 확인할 것을 구분한다.

## 고객 직접 시험과 결과
고객은 기존 vox.ai 제품 UI에서 대상 agent와 버전을 확인해 음성 시험을 직접 실행한다. `open_voice_test_session`은 호스트의 실시간 도구 목록에 있고 입력 스키마가 확인된 경우에만 선택한다. 현재 구현 baseline에는 시험 시작/통화 조회 도구가 없다. 제공되지 않으면 시험할 대상·발화·기대 결과를 안내하고 고객의 작업을 기다린다. 임의 URL이나 토큰 포함 링크를 만들지 않는다.

고객이 알려준 결과는 customer_reported로 표시한다. 이후 작업에 영향을 줄 결과는 사용자가 별도 기억 키워드를 말하지 않아도 feedback_reported 또는 evaluation_reported의 customer_voice_report로 짧게 기록한다. get_work_context에서 자동 기록의 enabled/revision/epoch를 확인하고 routine event에 최신 CAS 값을 전달한다. 사용자가 OFF로 바꾼 상태라면 자동 기록을 중단하며, 사용자가 현재 대화에서 저장하지 말라고 직접 요청해도 기록하지 않는다. OFF와 별개로 사용자가 명시적으로 요청한 기존 기록 조회·정정·삭제는 지원한다. 외부 call transcript 전체를 수집하지 않는다. text_contract holdout은 고객의 voice test가 아니다. 실제 call 원문·분석·저장 결과는 호스트가 call 조회 도구를 제공하고 응답에서 확인한 경우에만 독립 call evidence로 기록한다. ID가 없거나 조회되지 않으면 추측하지 않는다.

## 완료 표시
‘시험 상황 작성’, ‘음성 시험 준비’, ‘실제 대화 수행’, ‘결과 확인’은 다른 단계다. 하나가 완료됐다고 뒤 단계를 완료로 표시하지 않는다. 수정이 필요하면 증거와 함께 해당 전문 스킬로 연결한다.

세부 실행 순환은 [합성 고객 여정](../../references/workflow-examples.md)을 따른다. 제품 설정 readback, 고객의 음성 수행, 고객 보고, 서버에서 조회한 call 증거를 서로 다른 완료 단계로 전달한다.
