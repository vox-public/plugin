---
name: inspect-call-evidence
description: "vox.ai 특정 통화의 발화·도구·추출 결과와 당시 버전을 연결해 실패 원인을 확인할 때 사용한다. 기간별 집계는 운영 분석 스킬이 맡는다."
metadata:
  product: vox.ai
  layer: architect
  status: authoring-draft-not-runtime-verified
---

# inspect-call-evidence

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구명은 출시 설계이며 연결된 서버의 실제 도구·스키마 확인 후 사용한다.

## 순서
1. 사용자 또는 실제 조회 결과에서 callId를 확보한다. `get_call`로 상태와 당시 agent 버전·지원되는 분석 결과를 읽고 필요한 경우 transcript를 요청한다.
2. 보고된 발화 전후와 도구 입력/결과를 대조한다. 현재 agent/Manual이 당시와 같다고 가정하지 않는다. 지원 버전 조회로 당시 근거를 확인하고 API에 없는 snapshot은 조회했다고 말하지 않는다.
3. 발화 오류, 호출 누락, 외부 실행 실패/불명, 추출 누락, 후처리 대기, 시험 기대의 오류를 구분한다.

## 제한
목록의 요약을 전문 transcript처럼 해석하지 않는다. 녹음·본문이 없거나 잘렸으면 판단 가능한 범위를 명시한다. 다른 고객의 통화나 비공개 DB/GCP 로그를 고객용 스킬의 필수 자료로 요구하지 않는다. 공통 원고에는 합성 사례만 저장한다.

## 전달
원인 후보, 근거 call/버전/관련 발화, 실제 결과, 부족한 근거, 수정할 대상과 재현 상황을 남긴다. 실패 원인 확인만 요청했다면 변경하지 않는다. 수정을 요청받았다면 [본문 편집](../edit-manual-safely/SKILL.md), [도구 진단](../troubleshoot-agent-tool/SKILL.md), [결과 설정](../configure-call-results/SKILL.md)으로 필요한 부분만 이어간다.
