---
name: tune-voice-behavior
description: "vox.ai 에이전트의 끼어들기·무응답·속도·언어·음성 또는 모델 선택을 실제 시험 근거로 조정할 때 사용한다."
metadata:
  product: vox.ai
  layer: architect
  status: authoring-draft-not-runtime-verified
---

# tune-voice-behavior

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구명은 출시 설계이며 연결된 서버의 실제 도구·스키마 확인 후 사용한다.

## 관찰과 가설
[음성 설계](../voice-interaction-design/SKILL.md)를 읽고 고객의 증상을 재현 상황으로 바꾼다. 현재 설정과 실제 통화의 지원 지표를 읽는다. 지표가 없으면 체감 관찰이라는 한계를 표시하고 임의의 밀리초 수치를 만들지 않는다.

## 변경
`list_models`와 실제 schema로 지원 조합을 확인한다. 코파일럿을 실행하는 모델과 고객과 대화하는 음성 agent의 모델을 혼동하지 않는다. 가설에 필요한 설정만 `save_agent`로 바꾸고 같은 묶음의 나머지 값을 보존한다. ElevenLabs 설정명·기본값을 옮기지 않는다.

## 비교
같은 발화·정정·잠깐의 침묵·끼어들기 상황을 변경 전후에 비교한다. 브라우저와 전화망 시험의 차이를 남긴다. 여러 설정을 한꺼번에 바꿨다면 어떤 설정의 효과인지 분리해 증명하지 못했음을 밝힌다.

설정 재조회 후 실제 시험을 하지 않았다면 ‘변경 저장·재시험 필요’로 끝낸다. 실고객 발신은 이 스킬의 자동 다음 단계가 아니다.
