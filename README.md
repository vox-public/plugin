# vox.ai Plugin

Claude Code, Codex, Grok Build에서 vox.ai에 연결하고 음성 에이전트를 설계·개선하는 플러그인입니다.
매뉴얼 작성·개선, 버전 게시, 보유 번호 연결, 발신·캠페인 운영, 통화 결과 확인 등 업무별 지침 26개와 원격 MCP 연결 설정을 제공합니다.

스킬은 업무 진행 지침이며, 실행 가능한 기능은 연결된 서버가 제공하는 도구와 계정 권한에 따라 달라집니다. 로그인과 실제 업무 실행은 사용하는 환경에서 확인해야 합니다.

## 설치

하나의 GitHub 저장소(`https://github.com/vox-public/plugin.git`)로 세 호스트에 모두 설치할 수 있습니다. SSH 키가 없어도 되도록 HTTPS 주소를 사용합니다.

Claude Code:

```text
/plugin marketplace add https://github.com/vox-public/plugin.git
/plugin install vox-ai@vox-ai
/reload-plugins
```

Codex CLI:

```sh
codex plugin marketplace add https://github.com/vox-public/plugin.git
codex plugin add vox-ai@vox-ai
codex mcp login vox-ai
```

Grok Build:

```sh
grok plugin install https://github.com/vox-public/plugin.git
```

Grok Build는 `.claude-plugin`과 `.mcp.json`, `skills/`를 그대로 읽으므로 별도 파일이 필요 없습니다. marketplace로 추가하려면 `grok plugin marketplace add https://github.com/vox-public/plugin.git` 뒤 TUI의 `/plugins`에서 설치합니다.

`plugin` 명령이 없는 호스트는 플러그인을 지원하는 버전으로 업데이트합니다.
로컬 변경을 시험하려면 marketplace 추가 명령에 복제한 저장소의 절대 경로를 지정합니다.

### 이전 `vox-skills` marketplace가 있다면

이전 `vox-skills` 저장소의 marketplace도 이름이 `vox-ai`라서 이 plugin과 충돌합니다. 이전 설치가 있으면 먼저 제거한 뒤 위 명령으로 다시 설치하세요.

```text
# Claude Code
/plugin uninstall vox-ai@vox-ai
/plugin marketplace remove vox-ai
```

```sh
# Codex CLI
codex plugin marketplace remove vox-ai

# Grok Build
grok plugin uninstall vox-ai
grok plugin marketplace remove vox-ai
```

### 업데이트

- Claude Code: `/plugin marketplace update vox-ai`와 `/plugin update vox-ai@vox-ai`를 순서대로 실행합니다.
- Codex CLI: `codex plugin marketplace upgrade`를 실행합니다.
- Grok Build: `grok plugin update`를 실행합니다.

업데이트 후 호스트 안내에 따라 다시 로드하고 새 대화에서 스킬을 확인합니다.

## 연결

플러그인은 두 개의 MCP 서버를 연결합니다.

- `vox-ai`: `https://mcp.tryvox.co/mcp`. 제품 조작용입니다. 호스트에서 제공하는 OAuth 로그인 절차를 따르고 작업할 조직을 확인합니다. Claude Code는 `/mcp`, Codex는 `codex mcp login vox-ai`, Grok Build는 TUI의 `/mcps`에서 로그인합니다.
- `vox-docs`: `https://docs.tryvox.co/mcp`. 공식 문서 검색용이며 로그인이 필요 없습니다. 문서 MCP를 쓸 수 없는 호스트에서는 `https://docs.tryvox.co/llms.txt`를 읽습니다.

키나 토큰을 대화에 붙여 넣거나 설치 파일에 저장하지 않습니다.
조직이 여러 개인 계정은 `list_organizations`로 확인하고 `set_organization`으로 전환할 수 있습니다. 전환은 이 연결 전체의 대상 조직을 바꾸므로 대상 조직을 확인한 뒤 진행하며, 내장 Copilot에서는 조직을 바꿀 수 없습니다.

설치 후 연결된 서버의 도구 목록과 입력 스키마를 확인합니다. 번들에는 첫 배포 범위 도구(조직·agent·버전·템플릿·Manual·도구·지식·번호·통화·캠페인·시트·고객)와 work context·record·operation 도구의 schema 후보가 있습니다. 외부 공개 연결에는 작업 기록 도구가 없을 수 있으며 그때는 현재 대화나 handoff로 이어갑니다. 실제 호스트의 노출 도구와 권한은 다를 수 있습니다. workflow별 capability는 [workflow-capabilities.json](references/workflow-capabilities.json), 입력 schema와 출처 상태는 [implemented-tools.snapshot.json](references/implemented-tools.snapshot.json)에 있습니다. `get_work_context`는 자동 기록이 기본 켜짐인지와 현재 settings revision/epoch를 반환합니다. routine case/event를 저장하기 전 최신 값을 읽고 둘을 요청에 복사하며, 꺼져 있거나 값이 바뀌면 automatic API가 쓰기를 거부하므로 저장하지 말고 설정 변경 또는 새 context를 기다립니다. 사용자가 현재 대화에서 저장하지 말라고 직접 요청하면 설정과 무관하게 기록하지 않습니다. OFF는 자동 수집·기록을 중지하지만 사용자가 명시적으로 요청한 기존 기록 조회·정정·삭제는 지원합니다. user-principal `save_agent`/`save_manual`에는 별도로 직전 `get_work_context`의 일회용 receipt가 필요하며, 이 읽기는 `max_tokens`를 기본값(3000) 아래로 낮추지 않고 `MEMORY_CONTEXT_BUDGET_TOO_SMALL`이 오면 `details.required_tokens`로 한 번만 다시 호출합니다. 작업 기록 도구가 없는 호스트에서는 receipt 없이 저장을 시도하고 서버가 거부하면 초안을 안내합니다. 설치 성공만으로 로그인, 도구 노출 또는 제품 작업이 완료된 것은 아닙니다.

`get_work_context`의 각 항목은 일반 claim/case/evidence에 `guidance: null`을 포함하고, guidance 항목에는 종류·상태·현재 지침·보존 조건·버전이 든 typed object를 포함합니다. `evaluation_reported.register_holdout`은 별도 text-contract 사례 등록에만 사용하며, 사용자가 현재 임베디드 Copilot 대화에서 직접 입력한 본인의 말을 출처로 명시적 경로에서만 등록되며, 출처 ID는 `get_work_context`의 `pending_recent_inputs`에 있는 해당 입력의 값을 사용하고, 시나리오는 JSON 문자열 대신 구조화 필드 `holdout_scenario`(`base_configuration`, `requested_change`, `required_preservation`)로 보냅니다(등록 가능 여부는 호스트 이름이 아니라 `get_work_context`를 먼저 호출해 해당 항목이 있는지로 판단합니다). 등록이나 자동 text 비교는 실제 voice test가 아니며, 고객이 직접 수행한 시험 결과는 계속 고객 보고로 표시합니다.

## 사용 예

원하는 업무를 자연어로 요청할 수 있습니다.

- “예약 문의를 받는 음성 에이전트의 매뉴얼을 작성해줘.”
- “이 에이전트의 기존 설정을 확인하고 안내 문구를 수정해줘.”
- “고객이 직접 시험한 결과에서 반복 질문을 발견했어. 이 피드백으로 Manual의 바뀔 부분을 제안해줘.”
- “템플릿으로 에이전트를 만들고 버전을 게시한 뒤 보유 번호에 연결해줘.”
- “이 번호로 시험 발신을 걸고 통화 결과를 확인해줘.”
- “동네 치과 예약 전화를 받는 에이전트를 만들어줘. 초진/재진·연락처·희망 시간을 받고, 많이 아프다고 하면 데스크로 연결해줘.” (Single + Manual로 만듭니다.)
- “1번 영업시간, 2번 오시는 길, 9번 직원 연결인 키패드 메뉴 ARS를 Flow 에이전트로 만들고 검증해줘.”
- “동의를 받은 화자의 음원 URL로 음성 모델을 만들어줘.”

에이전트 유형은 기본이 Single + Manual입니다. 키패드 메뉴 ARS나 원문 낭독처럼 규칙이 분명한 업무일 때만 Flow를 쓰며, 만들기 전에 고른 유형과 이유를 먼저 알려 줍니다.

Claude Code에서는 `/vox-ai:voice-agent-design`처럼 스킬을 직접 호출할 수도 있습니다. Codex에서는 설치된 vox.ai 스킬을 선택하거나 관련 업무를 요청합니다.

변경 전 대상 조직과 리소스를 확인하고, 저장 후 다시 조회해 결과를 확인합니다. 실제 전화 발신·캠페인 실행·게시·번호 연결 변경 전에는 대화에서 요약 확인을 받고, 발신·캠페인에는 의도마다 새 `execution_key`를 만들며 결과가 불명이면 다시 실행하지 않고 `get_call`/`get_campaign`으로 확인합니다. 지식은 텍스트·URL만 등록하고 번호 획득·해지는 웹에서만 합니다. 음성 시험 도구는 없어 고객이 제품 UI에서 직접 시험하며, 고객 보고는 `get_call`로 조회하기 전까지 서버에서 확인한 call 결과처럼 설명하지 않습니다.

전체 스킬 목록은 [catalog.json](catalog.json)에 있습니다. 각 스킬의 `tools.implemented`는 현재 snapshot에서 실행 가능한 도구이고 `tools.designed_only`는 지침에 남아 있는 설계 참조입니다. 상단 `designed_tool_references`가 해당 참조의 전체 목록입니다. 실행 원칙은 [execution-contract.md](references/execution-contract.md)에 있습니다.

## 빌드와 검증

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build.py
```

빌드는 스킬 목록·경로·메타데이터, 문서 링크, 구현 tool/schema snapshot, 워크플로 required/optional capability, JSON 예제 입력 schema, 호스트 설정과 버전 일치를 검증합니다. `scripts/build.py --mcp-root <mcp-checkout>` 또는 `scripts/build.py --manifest <manifest.json>`을 주면 pinned MCP manifest와 tool schema digest도 대조합니다. 번들된 [구현 도구 스냅샷](references/implemented-tools.snapshot.json)은 원본 MCP commit·manifest digest와 각 입력 schema digest를 기록합니다.

- `dist/vox-ai-plugin.zip`: 호스트 manifest, MCP 연결 설정, 스킬과 공통 문서.
- `dist/vox-ai-skills.zip`: 같은 스킬과 공통 문서. 연결 설정과 호스트 manifest는 제외.
- `bundle-manifest.json`: 공통 파일별 SHA-256과 묶음 digest.

공통 digest는 스킬과 공통 문서만 대상으로 하며 ZIP 전체나 연결 설정의 digest가 아닙니다.
CI는 테스트와 빌드를 실행하고 커밋된 bundle manifest가 최신인지 확인합니다.
배포 변경 시 두 호스트 manifest의 버전을 함께 올리고 빌드해 bundle manifest를 갱신합니다.
