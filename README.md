# vox.ai Plugin

Claude Code, Codex, Grok Build에서 vox.ai에 연결하고 음성 에이전트를 설계·개선하는 플러그인입니다.
매뉴얼 작성·개선, 버전 게시, 보유 번호 연결, 발신·캠페인 운영, 통화 결과 확인 등 업무별 지침 26개와 원격 MCP 연결 설정을 제공합니다.

실행 가능한 기능은 연결된 서버가 제공하는 도구와 계정 권한에 따라 달라집니다.

## 설치

하나의 GitHub 저장소(`https://github.com/vox-public/plugin.git`)로 세 호스트에 모두 설치할 수 있습니다.

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

Codex는 `codex mcp login vox-ai`까지 실행해야 vox.ai 도구를 쓸 수 있습니다. Grok Build는 설치할 때 신뢰 확인을 묻습니다. 비대화형 환경에서는 `--trust`를 붙입니다. `plugin` 명령이 없으면 호스트를 플러그인을 지원하는 버전으로 업데이트합니다.

## 연결과 로그인

플러그인은 두 개의 MCP 서버를 연결합니다.

| 이름 | 주소 | 용도 | 로그인 |
| --- | --- | --- | --- |
| `vox-ai` | <https://mcp.tryvox.co/mcp> | 에이전트·번호·통화·캠페인 등 vox.ai 조작 | 필요 |
| `vox-docs` | <https://docs.tryvox.co/mcp> | vox.ai 공식 문서 검색 | 불필요 |

`vox-ai`는 호스트에서 로그인합니다. Claude Code는 `/mcp`, Codex는 `codex mcp login vox-ai`, Grok Build는 TUI의 `/mcps`를 사용합니다.

첫 연결은 다음 순서로 진행됩니다.

1. vox.ai에 로그인합니다.
2. 승인 화면에서 **연결 승인**을 한 번 누릅니다.

조직을 고르는 단계는 없습니다. 계정이 속한 모든 조직에서 쓸 수 있으며 기본 조직으로 시작합니다. 대화에서 "다른 조직으로 바꿔줘"처럼 요청하면 바뀌고 다시 연결할 필요는 없습니다. 연결은 vox.ai 로그인 세션 동안 유지되며, 오래 쓰지 않으면 다시 로그인합니다.

키나 토큰을 대화에 붙여 넣거나 파일에 저장하지 않습니다.

## 데이터와 보안

- 플러그인에는 업무 지침인 스킬과 원격 MCP 연결 설정만 들어 있습니다. hook, 설치할 때 실행되는 코드, 내려받는 패키지는 없습니다.
- `vox-ai` 도구를 부르면 요청이 <https://mcp.tryvox.co>로 가고, 로그인한 vox.ai 계정의 권한으로 그 조직의 데이터를 읽고 씁니다.
- `vox-docs`는 문서 검색어만 <https://docs.tryvox.co>로 보냅니다.
- `cli-authoring` 스킬은 사용자가 vox CLI 사용을 요청했을 때만 로컬에 설치된 `vox` CLI를 실행합니다. 이때 CLI에 이미 로그인된 사용자 본인의 인증을 쓰며, 플러그인이 인증값을 읽어 다른 곳으로 보내지 않습니다.
- 개인정보는 [개인정보처리방침](https://www.tryvox.co/legal/privacy-policy)에 따라 처리합니다.

## 사용 예

원하는 업무를 자연어로 요청합니다.

- “예약 문의를 받는 음성 에이전트의 매뉴얼을 작성해줘.”
- “이 에이전트의 기존 설정을 확인하고 안내 문구를 수정해줘.”
- “템플릿으로 에이전트를 만들고 버전을 게시한 뒤 보유 번호에 연결해줘.”
- “이 번호로 시험 발신을 걸고 통화 결과를 확인해줘.”
- “동네 치과 예약 전화를 받는 에이전트를 만들어줘. 초진/재진·연락처·희망 시간을 받고, 많이 아프다고 하면 데스크로 연결해줘.” (Single + Manual로 만듭니다.)
- “1번 영업시간, 2번 오시는 길, 9번 직원 연결인 키패드 메뉴 ARS를 Flow 에이전트로 만들고 검증해줘.”

에이전트 유형은 기본이 Single + Manual입니다. 키패드 메뉴 ARS나 원문 낭독처럼 규칙이 분명한 업무일 때만 Flow를 쓰며, 만들기 전에 고른 유형과 이유를 먼저 알려 줍니다.

Claude Code에서는 `/vox-ai:voice-agent-design`처럼 스킬을 직접 호출할 수도 있습니다.

안전 원칙은 다음과 같습니다.

- 실제 전화 발신·캠페인 실행·게시·번호 연결 변경 전에는 대화에서 내용을 요약해 확인을 받습니다.
- 발신·캠페인 결과가 불명이면 다시 실행하지 않고 `get_call`/`get_campaign`으로 조회합니다.
- 지식은 텍스트·URL만 등록하며, 번호 획득·해지는 웹에서 합니다.
- 음성 시험 도구는 없으므로 제품 UI에서 직접 시험합니다.

## 업데이트와 제거

업데이트:

- Claude Code: `/plugin marketplace update vox-ai`와 `/plugin update vox-ai@vox-ai`를 순서대로 실행합니다.
- Codex CLI: `codex plugin marketplace upgrade`를 실행합니다.
- Grok Build: `grok plugin update`를 실행합니다.

업데이트 후 호스트 안내에 따라 다시 로드하고 새 대화에서 스킬을 확인합니다.

제거:

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

### 이전 `vox-skills`에서 옮기기

이전 `vox-skills` 저장소의 marketplace도 이름이 `vox-ai`라서 이 plugin과 충돌합니다. 이전 설치가 있으면 위 방법으로 먼저 제거한 뒤 [설치](#설치)의 명령으로 다시 설치합니다. 이름이 같아 버전 번호가 1.0.x에서 0.2.x로 낮아져도 정상입니다.

## 링크

- 문서: <https://docs.tryvox.co/docs/ai/plugin>
- 홈페이지·지원: <https://www.tryvox.co>, support@tryvox.co
- 개인정보처리방침: <https://www.tryvox.co/legal/privacy-policy>
- 이용약관: <https://www.tryvox.co/legal/terms-of-service>
- 라이선스: [MIT](LICENSE)

## 개발

저장소를 수정하거나 빌드·검증하려면 [DEVELOPMENT.md](DEVELOPMENT.md)를 봅니다. 업무 실행 원칙은 [execution-contract.md](references/execution-contract.md)에 있습니다.

## English

The vox.ai plugin connects Claude Code, Codex and Grok Build to vox.ai, a voice AI platform for phone agents that answer and place calls in Korean. It adds 26 skills for designing, building, testing and operating voice agents, and configures two remote MCP servers.

- `vox-ai` at <https://mcp.tryvox.co/mcp> reads and changes agents, manuals, knowledge, tools, numbers, calls and campaigns. Sign in with your vox.ai account. Every action runs with the permissions you already have in that workspace.
- `vox-docs` at <https://docs.tryvox.co/mcp> searches the public vox.ai documentation. No sign-in is needed.

Install with the commands in [설치](#설치). The plugin contains no hooks and runs no code at install time. Placing a call or launching a campaign makes real phone calls from your workspace numbers and uses your credits, so the skills confirm these actions with you first.

Documentation: <https://docs.tryvox.co/docs/ai/plugin> · Support: support@tryvox.co · [Privacy policy](https://www.tryvox.co/legal/privacy-policy) · [Terms of service](https://www.tryvox.co/legal/terms-of-service)
