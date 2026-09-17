---
name: troubleshoot-agent-tool
description: "vox.ai 통화 중 외부 도구가 호출되지 않거나 오류·타임아웃·결과 누락이 발생했을 때 실제 call 근거로 원인을 좁힌다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# troubleshoot-agent-tool

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 증거
오류가 저장 시점인지 통화 실행 시점인지 구분한다. 실행 문제면 [당시 통화](../inspect-call-evidence/SKILL.md)의 도구 입력·응답·버전·관련 발화를 읽는다. tool 저장 오류면 실제 오류 필드와 현재 config를 비교한다.

## 원인별 행동
| 근거 | 확인/수정 |
| --- | --- |
| 호출 자체가 없음 | Manual/agent 연결, 해당 조건 도달, 도구 설명과 입력 확보 여부 |
| schema 오류 | 현재 저장 형식과 공개 스키마 비교; 같은 payload 반복 금지 |
| 외부 4xx/5xx | 실제 method·인증 경로·입력과 외부 계약 대조; 무조건 Manual 탓으로 돌리지 않음 |
| timeout/결과 불명 | 외부 실행 성공 여부와 지원 결과 조회 확인; 부작용 재요청 금지 |
| 응답 성공이나 발화/저장 오해 | 반환값 사용·본문 지시·추출 설정의 연결 검토 |

고객 시스템 장애면 확인한 요청과 오류를 필요한 범위로 정리한다. 비밀키·개인정보는 보고서에 노출하지 않는다. 동일한 가설·요청으로 실패만 반복하지 않고 새 근거가 없으면 미확인 원인과 필요한 진단 정보를 남긴다.

수정할 곳이 확인되면 [도구 연결](../connect-agent-tools/SKILL.md), [본문 편집](../edit-manual-safely/SKILL.md), [결과 설정](../configure-call-results/SKILL.md) 중 해당 작업만 수행한다. 시험 조건과 실제 결과로 수정 효과를 확인한다.
