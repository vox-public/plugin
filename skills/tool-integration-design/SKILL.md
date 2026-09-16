---
name: tool-integration-design
description: "vox.ai 음성 에이전트가 외부 API로 실제 조회·예약·접수·전달을 수행하도록 연동 계약과 실패 대응을 설계할 때 사용한다."
metadata:
  product: vox.ai
  layer: general
  status: authoring-draft-not-runtime-verified
---

# tool-integration-design

## 완료를 정의한다
사용자가 원하는 외부 결과와 API의 응답 의미를 먼저 맞춘다. HTTP 수락, 작업 접수, 예약 확정, 담당자 수신은 다른 상태다. 내부 추출 결과 저장을 외부 작업 성공으로 대체하지 않는다.

## 설계에 필요한 근거
endpoint·method·인증 방식·필수 입력·응답/오류 예·부작용·지원되는 중복 판별/결과 조회를 API 문서나 사용자의 명시 정보로 확인한다. 부족한 입력은 질문하되 원시 비밀키를 대화로 요구하지 않는다. 자격 증명은 제품이 제공하는 설정 경로를 사용한다.

입력값의 출처를 고객 발화, 사전 정보, 고정 설정, 이전 도구 결과로 구분한다. 반환값은 다음 판단과 사용자 설명에 필요한 필드를 중심으로 설계한다. 도구 설명에는 언제 호출하고 언제 호출하지 않을지, 오류 시 무슨 말을 할지 적는다.

## 실행 위치
음성 agent가 통화 중 호출하는 도구와 코파일럿이 agent를 관리하는 MCP 도구를 구분한다. 브라우저 동작이 필요하다고 ElevenLabs client tool이나 code sandbox가 vox.ai에도 있다고 가정하지 않는다. vox.ai에서 실제 지원하는 도구 종류·스키마로 표현 가능한지 확인한다.

반복·불명 결과의 처리와 인증 오류를 정상 결과와 구분한다. 외부 실행이 불명일 때 새 요청을 보내는 정책을 임의로 만들지 않는다.

저장·연결은 [connect-agent-tools](../connect-agent-tools/SKILL.md), 실제 오류는 [troubleshoot-agent-tool](../troubleshoot-agent-tool/SKILL.md)로 이어간다.
