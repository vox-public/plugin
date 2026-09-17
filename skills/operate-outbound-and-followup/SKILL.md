---
name: operate-outbound-and-followup
description: "vox.ai의 단건 발신·캠페인 실행/중단·통화 전환·후속 SMS를 사용자의 명시 업무 범위에서 수행하고 실제 결과를 확인할 때 사용한다."
metadata:
  product: vox.ai
  layer: architect
  status: preview
---

# operate-outbound-and-followup

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 실행 전 상태
실행 의도, agent/버전, 발신 번호, 대상, 사전 변수, 현재 권한·한도를 확인한다. ‘에이전트 만들어줘’나 ‘발신 계획을 짜줘’는 실제 발신 요청이 아니다. 이미 구체적인 실행을 위임받았다면 MCP 전용 반복 승인을 추가하지 않는다.

## 동작별 계약
| 업무 | 실행/조회 | 완료 판단 |
| --- | --- | --- |
| 단건 발신 | `place_call` → `get_call` | 접수·연결·종료·업무 결과 구분 |
| 캠페인 | `launch_campaign` 및 pause/resume/cancel → `get_campaign` | 대상별 시도·결과; 중지가 진행 콜을 끊는지 실제 계약 확인 |
| 전환 | `transfer_call` → 지원되는 call 상태 조회 | 명령 수락과 상대 응답 구분 |
| SMS | `send_sms`/`send_sms_batch` → `get_sms`/`get_sms_batch` | 요청 수락·제공자 상태·확인 가능한 전달 결과 구분 |

설정 저장과 실행 도구를 혼동하지 않는다. 정확한 ID와 반환된 결과 참조를 보존한다. 응답 불명은 [복귀](../resume-agent-work/SKILL.md)로 넘기며 새 키로 재발신/재발송하지 않는다. 지원되지 않는 예약 발신·상시 감시를 추가하지 않는다.

## 결과와 후속
모수와 성공/실패/미응답/불명/처리 중을 구분한다. 실패 대상만 재실행할 때도 실제 실행 여부를 먼저 확인하고 사용자 의도 범위 안에서 진행한다. 대상 목록이나 상세 통화는 필요한 접근 범위로만 사용한다. 내용 분석은 [통화 성과](../review-call-performance/SKILL.md)로 이어간다.

‘A/B 비교’ 요청은 같은 대상에게 두 버전을 각각 시험할지, 대상자를 분할할지에 따라 실행이 다르다. 실제 의도가 불명확하면 [업무 판단 기준](../../references/workflow-guidance.md)에 따라 질문한다. 시험 설계 합의를 실고객에 대한 추가 발신 위임으로 확대하지 않는다.
