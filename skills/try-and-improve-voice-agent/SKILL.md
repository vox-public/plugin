---
name: try-and-improve-voice-agent
description: "vox.ai 에이전트를 직접 말해 보고 피드백·실패 통화를 근거로 수정하고 재시험할 때 사용한다."
metadata:
  product: vox.ai
  layer: architect
  status: authoring-draft-not-runtime-verified
---

# try-and-improve-voice-agent

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구명은 출시 설계이며 연결된 서버의 실제 도구·스키마 확인 후 사용한다.

## 시험 또는 증거부터
아직 통화가 없으면 [시험 준비](../prepare-voice-test/SKILL.md)로 진입한다. 실패 통화나 callId가 있으면 [통화 근거](../inspect-call-evidence/SKILL.md)를 먼저 읽는다. 기대 결과와 실제 결과의 차이를 한 가지 이상 구체적으로 적는다.

## 필요한 수정만 조합
- 말/질문/정정/마무리: [Manual 편집](../edit-manual-safely/SKILL.md).
- 도구 미호출·오류·불명: [도구 진단](../troubleshoot-agent-tool/SKILL.md).
- 추출·저장: [결과 설정](../configure-call-results/SKILL.md).
- 끼어들기·지연·음성: [음성 조정](../tune-voice-behavior/SKILL.md).
- 공유 변경: [영향 확인](../review-shared-impact/SKILL.md).

한 번의 틀린 응답을 전체 프롬프트 재작성으로 확대하지 않는다. 과거 버전 문제를 현재 설정에 이미 해결됐는지 확인하지 않고 다시 고치지 않는다. 인프라/외부 API 문제를 Manual로 덮지 않는다.

## 재시험과 완료
수정 저장·재조회 뒤 같은 상황과 관련 정정/실패 상황을 직접 시험한다. 발화뿐 아니라 실제 도구·추출·저장 결과를 대조한다. 아직 사용자가 시험하지 않았다면 ‘수정 저장 완료·재시험 필요’다. 텍스트 검토나 합성 시나리오 작성은 실제 음성 통과가 아니다.

원인과 변경, 확인한 근거, 남은 시험을 전달한다. 더 큰 운영 추세가 필요하면 [기간 분석](../review-call-performance/SKILL.md)을 추가한다.

## 피드백을 다음 작업으로 바꾸기

[FDE 판단 기준](../../references/fde-decisions.md)의 피드백 표로 원고·연결·결과 저장·시험 조건 중 변경할 범위를 좁힌다. ‘대시보드 우선’ 결정은 전달 위치와 결과 설정의 변경일 수 있으며 모든 외부 도구를 제거하라는 뜻은 아니다. 현재 목표·확인한 근거·변경한 대상·다음 시험을 작업 요약에 갱신하고, 이미 저장한 리소스는 재사용한다.
