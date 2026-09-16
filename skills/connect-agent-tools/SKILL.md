---
name: connect-agent-tools
description: "vox.ai 음성 에이전트가 외부 업무 API를 호출하도록 지원되는 도구를 생성·수정·Manual에 연결할 때 사용한다. 코파일럿 MCP 서버 설치와는 다른 작업이다."
metadata:
  product: vox.ai
  layer: architect
  status: authoring-draft-not-runtime-verified
---

# connect-agent-tools

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구명은 출시 설계이며 연결된 서버의 실제 도구·스키마 확인 후 사용한다.

## 기존 상태와 계약
[연동 설계](../tool-integration-design/SKILL.md)로 endpoint·인증·입출력·결과 의미를 확인한다. `list_tools/get_tool`로 재사용 가능한 도구와 공유 범위를 읽고 `get_agent/get_manual`에서 연결 위치를 확인한다.

## 생성·수정·연결
실제 `save_tool` 스키마와 제품이 지원하는 tool type을 확인한다. ElevenLabs의 value source/parameter 배열이나 client/code runtime 규칙을 복사하지 않는다. 수정은 현재 config를 읽고 실제 교체 의미에 따라 보존한다.

도구 저장 결과의 정확한 ID를 Manual의 지원 참조 문법으로 연결하고 agent 연결까지 확인한다. 이름 변경은 본문 참조에도 영향을 줄 수 있으므로 실제 참조를 확인한다. 저장된 도구가 있다는 사실만으로 통화에서 호출된다고 말하지 않는다.

## 시험과 완료
통제된 상황에서 올바른 입력으로 도구가 호출되고 실제 반환 결과를 다음 발화/저장에 사용했는지 확인한다. 외부 부작용이 있으면 사용자가 허용한 시험 대상만 쓴다. 제품에 없는 mock API를 만들지 않는다. 고객 테스트 endpoint가 제공됐다면 그 계약을 사용한다.

실패는 schema 저장 실패, 미연결/잘못된 호출 조건, 외부 API 오류로 나누고 [도구 오류 진단](../troubleshoot-agent-tool/SKILL.md)에 증거를 전달한다. 고객 코드 수정이 필요한 경우 정확한 부족한 계약을 설명한다.

get_tool의 omitted_fields에 auth_credentials/headers가 있으면 보이지 않는 기존 인증값이다. 이번 변경에 포함하지 않는 인증 필드는 payload에서 생략한다. 빈 맵이나 마스킹 문자열로 기존 값을 재구성하지 않는다.
