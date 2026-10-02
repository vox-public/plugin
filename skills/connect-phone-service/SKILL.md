---
name: connect-phone-service
description: "vox.ai 에이전트에 이미 가진 번호를 연결·해제하고 실제 인바운드 수신을 확인할 때 사용한다. 번호 획득·해지는 웹에서만 한다."
metadata:
  product: vox.ai
  layer: architect
  status: stable
---

# connect-phone-service

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구는 연결된 서버가 제공하는 실제 이름과 스키마를 확인한 뒤 사용한다.

## 먼저 확인
이 스킬은 이미 가진 번호를 agent에 연결한다. 번호 획득·해지와 대표번호·발신표기번호 신청·심사는 웹에서만 하며 도구가 없다. 새 번호가 필요하면 그 사실을 알리고 번호 확보 뒤 이어간다. `list_numbers`(`kind`: 일반 `general`, 대표 `uan`, 발신표기 `presentation`)와 `get_number`로 번호의 소유·상태·연결 agent/버전을 읽는다. 번호 문자열이 아니라 반환된 번호 ID를 쓴다.

## 연결
연결할 agent와 버전을 정한다. 운영 번호는 보통 production 버전이므로 `list_agent_versions`로 확인하고, 없으면 [버전 저장·게시](../build-first-voice-agent/SKILL.md)의 `create_agent_version` → `publish_agent_version`을 먼저 한다(게시도 확인 대상). 일반 번호·발신표기번호는 `set_number_agents`로 인바운드/아웃바운드(`agent_id`, `agent_version`: current·production·vN) 연결을 바꾼다. 대표번호의 착신 연결과 메모는 `update_number`다.

**`set_number_agents`의 null은 연결 해제다.** 바꾸지 않는 필드는 생략해 기존 연결을 유지하고, 해제하려는 쪽만 null로 보낸다. 해제는 그 번호로 오는 전화나 발신이 끊기므로 의도를 분명히 확인한다.

실제 영향이 있는 변경이므로 호출 전에 [실행 계약](../../references/execution-contract.md)대로 번호(끝 4자리)·종류·바꿀 연결(현재→변경 agent/버전)·해제 여부를 요약해 확인받는다. 번호 확보, agent 연결, 수신 라우팅/전환은 서로 다른 단계로 표시한다. 인증·서류를 스킬/작업 파일에 복사하지 않는다.

## 완료 근거
저장 응답만으로 끝내지 않고 `get_number`를 다시 읽어 연결된 agent/버전을 확인한다. 응답이 불명이면 다시 호출하지 말고 `get_number`로 현재 상태를 확인한다. 인바운드 수신은 통제된 전화로 확인하고 `list_calls`(`call_to`·`agent_id`·`start_at_after`)에서 callId를 찾아 `get_call`로 연결 agent·버전을 확인한다. 브라우저 음성 시험으로 전화망 수신을 검증했다고 말하지 않는다.

## 오류와 다음 행동
연결 오류면 번호 상태·소유와 agent 버전 존재를 먼저 읽는다. 인바운드 설정 요청을 실고객 아웃바운드 실행으로 바꾸지 않는다. desk 상담원 큐/이어받기 기능은 이 Agents 모듈에서 추정 실행하지 않는다. 구매·신청 상태 조회가 필요하면 고객이 웹에서 확인한 상태를 보고받는다.
