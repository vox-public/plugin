# 호스트별 실행 어댑터

공통 업무 흐름은 [합성 고객 여정](workflow-examples.md)을 따른다. 각 호스트는 독립적으로 사용할 수 있다. plugin/skill 파일은 지침을 제공하고, MCP 권한·제품 상태·도구 schema는 연결된 서버가 제공한다. 현재 번들의 구현 baseline은 [구현 도구 스냅샷](implemented-tools.snapshot.json)이며, 업무별 현재/설계 capability와 미지원 fallback은 [워크플로 capability 표](workflow-capabilities.json)에 있다. 매 작업에서 호스트가 실제 보여주는 도구와 입력 schema를 다시 확인한다.

## 내장 Copilot

- 제품이 제공하는 연결과 인증을 사용한다. 외부 marketplace 설치나 Claude/Codex OAuth 절차를 요구하지 않는다.
- 호스트가 아래 네 shared-work 도구를 실제 도구 목록과 schema에 제공하면 해당 capability로 공통 improvement case를 조회·갱신한다. 그 도구가 없을 때만 현재 Thread에서 접근 가능한 대화·파일을 사용하고, 다른 Thread 검색이나 공통 기억을 가정하지 않는다.
- 필요한 도구가 현재 도구 목록에 있으면 그 schema를 확인한다. authoring의 필수 저장/조회 도구가 빠지면 Manual 초안을 준비하고 저장은 할 수 없다고 설명한다.
- 고객 직접 음성 시험과 실사용 운영은 고객이 기존 vox.ai 제품 UI에서 수행한다. 완료 여부는 고객 보고와 MCP readback을 구분한다.
- 예: “첨부한 합성 서비스 설명으로 첫 Manual을 만들고, 저장 후 전체 본문과 revision을 다시 읽어줘.” 공유 도구가 없고 이전 Thread에도 접근할 수 없을 때만 실제 ID와 마지막 결정을 사용자에게 받아 검증한다.

## Codex

- Codex plugin marketplace 흐름으로 plugin을 설치하고 MCP 연결은 Codex 호스트의 OAuth UI에서 완료한다. 토큰을 대화나 작업 파일에 복사하지 않는다.
- 설치 후 현재 연결, 조직과 노출 도구를 확인한다. plugin이 내장 Copilot의 Thread DB, E2B 작업 경로 또는 private 파일을 읽을 수 있다고 가정하지 않는다.
- 저장소 작업공간의 자료나 사용자가 첨부한 파일만 실제 호스트가 읽을 수 있는 범위에서 사용한다. URL 열람 여부도 그 Codex 세션의 도구로 확인한다.
- 자연어로 요청하거나 설치된 vox.ai skill을 호출한다. 저장은 받은 실제 `agent_id`/`manual_id`와 현재 revision을 사용하고, 결과를 재조회한다.
- 직접 음성 시험·운영은 고객이 vox.ai 제품 UI에서 한다. 공통 improvement case 도구가 있으면 해당 기록으로 재개하고, 없을 때만 Codex가 접근 가능한 대화 기록이나 사용자 handoff를 사용한다.
- 예: “`service-brief.md`를 근거로 첫 Manual을 만들고 저장값을 확인해줘.” 공유 도구가 없고 새 Codex 대화에서 이어갈 때는 사용자가 실제 ID, 마지막 결정, 시험 상태를 전달한다.

## Claude Code

- Claude Code plugin marketplace 흐름으로 plugin을 설치하고 MCP OAuth 연결을 호스트에서 완료한다. Codex 설정이나 내장 연결을 재사용한다고 가정하지 않는다.
- Claude Code에서는 `/vox-ai:build-first-voice-agent` 또는 `/vox-ai:try-and-improve-voice-agent`처럼 관련 skill을 명시적으로 부를 수 있고, 일반 자연어 요청도 가능하다.
- shared-work 도구가 없으면 현재 Claude Code 세션이 읽을 수 있는 파일만 근거로 사용하며, plugin이 내장 Thread·Codex 세션·다른 조직의 로컬 작업공간을 검색한다고 가정하지 않는다. 도구가 있으면 그 MCP 기록을 통해 공통 case를 읽고 갱신한다.
- 제품 변경 뒤 실제 MCP 응답을 재조회한다. 고객이 직접 시험한 결과는 `customer_reported`; 실제 제품 call 조회 근거는 조회 도구와 결과가 확인된 경우에만 별도로 표시한다.
- 직접 시험과 실운영은 기존 vox.ai 제품 UI에서 고객이 수행한다. 공통 improvement case 도구가 없을 때에만 새 Claude Code 대화에서 사용자가 제공한 handoff로 재개하고, 도구가 있으면 해당 MCP 기록을 다시 확인한다.
- 예: `/vox-ai:build-first-voice-agent`를 사용해 사용자가 제공한 서비스 자료로 첫 Manual을 만들고, 저장한 `agent_id`와 `manual_id`를 기록해줘. shared-work 도구가 있으면 그 기록을 확인하고, 없으면 새 호스트 대화에 상태가 자동 전달됐다고 가정하지 않는다.

## 연결·파일·재개 공통 원칙

- MCP 연결 성공, 인증, 제품 업무 완료는 서로 다른 상태다. 실제 호스트가 제공하는 조직·도구·schema를 확인한다.
- 호스트가 required tool을 제공하지 않으면 제품 write를 추측하거나 REST/CLI/DB로 우회하지 않는다. 가능한 자료 정리와 Manual 초안을 이어가고 빠진 capability를 말한다.
- 제품 file reference, 호스트 첨부, 로컬 경로는 서로 대체할 수 없다. 자료를 실제로 읽지 못했으면 분석했다고 표현하지 않는다.
- Thread/호스트 간 연속성은 현재 호스트가 `get_work_context`, `get_work_record`, `save_work_record`, `get_work_operation`을 실제 tool list와 schema에 제공하면 공통 improvement case로 처리한다. 그 도구가 없을 때만 접근 가능한 대화 기록이나 사용자 제공 handoff로 fallback하며, 공통 memory 저장이라고 설명하지 않는다. capability 표는 이 경계를 기계적으로 구분한다.
- 시험과 운영은 사용자 또는 고객이 제품 UI에서 한다. 설계 시나리오, 고객 보고, MCP에서 독립 조회한 call 근거를 서로 다른 증거로 기록한다.
