# vox.ai Plugin

vox.ai의 원격 MCP 연결과 음성 업무 스킬을 배포하는 [공개 저장소](https://github.com/vox-public/plugin)입니다.
MCP 서버 구현은 `fleek-fitness/vox-mcp`에 있으며 이 저장소에는 포함하지 않습니다.
Plugin 이름은 `vox-ai`입니다. 현재는 구현 후보이며 외부 호스트 설치·로그인·업무 완주 검증은 아직 수행하지 않았습니다.

공통 스킬 26개는 general 8 / mcp 2 / architect 16으로 구성되며 `catalog.json`에 분류합니다.
Codex와 Claude Code가 모두 발견할 수 있도록 `skills/<name>/SKILL.md`에 배치합니다.
ElevenLabs Plugin의 연결 설정 + 업무 스킬 + 공통 references 구조를 참고했습니다.

## 설치와 업데이트

아래 설치 명령은 marketplace 파일이 포함된 릴리스가 `main`에 병합된 뒤 사용할 수 있습니다.
설치는 스킬 발견·MCP 연결 등록이며, 로그인이나 제품 업무 완료를 뜻하지 않습니다.

Claude Code:

```text
/plugin marketplace add vox-public/plugin
/plugin install vox-ai@vox-ai
```

업데이트는 `/plugin marketplace update vox-ai` 후 `/plugin update vox-ai@vox-ai`를
실행하고 호스트 안내에 따라 다시 로드합니다.

Codex CLI:

```sh
codex plugin marketplace add vox-public/plugin
codex plugin add vox-ai@vox-ai
```

Codex의 업데이트 명령은 설치 버전의 `codex plugin marketplace --help`에서 확인합니다.
플러그인 UI/CLI에서 업데이트한 뒤 새 대화에서 스킬·연결이 발견되는지 확인합니다.
지원 CLI에서 `plugin` 하위 명령이 없으면 해당 호스트를 먼저 업데이트합니다.

PR 단계의 로컬 검증은 저장소를 clone한 뒤 각 호스트의 marketplace add에
저장소 절대 경로를 전달합니다. 기존 설치와 섞이지 않는 별도 테스트 프로필을 사용합니다.
스킬 호출 예는 Claude Code에서 `/vox-ai:voice-agent-design`이며,
Codex에서는 설치된 vox.ai 스킬을 선택하거나 관련 업무를 요청합니다.

## 연결과 사용

`.codex-plugin/plugin.json`과 `.claude-plugin/plugin.json`은 같은 스킬을 읽습니다.
`.mcp.json`은 `https://mcp.tryvox.co/mcp`에 연결합니다. 호스트의 OAuth 로그인으로 조직을 선택합니다.
설치 파일에 키를 저장하거나 대화에 사용자 토큰을 붙이지 않습니다.

현재 원격 endpoint는 이전 구현입니다. 새 서버 배포 전 이 후보를 출시 완료로 취급하지 마세요.
설계 도구 수 117은 런타임 지원 수가 아닙니다. 매 연결에서 실제 tools/list를 확인합니다.
저장 확인, 직접 음성 시험, 실제 전화 운영 완료는 따로 확인합니다.

## 현재 가능한 범위

공개 URL의 기존 서버와 새 Vultr 서버 후보를 구분합니다. 새 MCP 후보의 확인 기준은
서버 커밋 `2a216aa`이며, 아래 표는 공개 서버에 배포됐다는 의미가 아닙니다.
항상 연결된 서버의 실제 tools/list와 schema가 우선합니다.

| 새 서버 후보의 범위 | 상태 |
| --- | --- |
| 조직·agent·Manual 조회, 모델·schema 탐색 | 구현된 10개 도구에 포함 |
| Single agent·Manual 생성/수정 및 재조회 | 구현됨; 실제 계정·환경에서 확인 필요 |
| 직접 음성 시험 진입, 통화 조회·분석 | 후보 서버에서 미구현 |
| 번호 연결·발신·캠페인·SMS·위젯·채팅 | 후보 서버에서 미구현 |

스킬 26개는 업무 원고의 수입니다. 실행 가능한 제품 기능 수가 아닙니다.
미지원 단계에서는 준비한 원고·저장된 ID·남은 작업을 전달하며, 도구를 발명하거나
직접 REST 호출로 우회하지 않습니다.

## 새 dev 서버 검증

공개 패키지는 계속 `https://mcp.tryvox.co/mcp`를 사용합니다.
Vultr dev 배포만으로 이 주소가 전환되지 않습니다. 테스트는 배포 담당자가
`https://mcp.dev.services.tryvox.co/mcp`의 DB 초기화·OAuth 등록 완료를 확인한 뒤 진행합니다.

1. 별도 테스트 프로필과 저장소 복사본을 준비합니다. 실제 고객 조직·기존 공개 연결과 섞지 않습니다.
2. 테스트 복사본의 `.mcp.json`에서 `mcpServers.vox-ai.url`만 dev 주소로 변경합니다.
   이 변경을 commit하거나 공개 bundle로 배포하지 않습니다. 공개 빌드는 이를 거부합니다.
3. Claude Code는 `claude --plugin-dir /absolute/path/to/test-copy`로 로드할 수 있습니다.
   Codex는 별도 테스트 프로필에서 로컬 marketplace로 설치합니다. 같은 이름의 기존
   공개 plugin이 동시에 활성화되지 않게 하고 새 대화에서 실제 연결 주소를 확인합니다.
4. 호스트 OAuth로 dev 계정·조직을 연결하고 실제 도구 목록을 확인합니다.
   토큰을 대화나 저장소에 복사하지 않습니다.
5. 사용자에게 허용된 테스트 Manual/agent를 조회 → 생성 또는 수정 → 재조회합니다.
   호스트 재시작 후 재연결·조회와 연결 해제까지 확인합니다.
6. 스킬 발견, OAuth 성공, 저장·재조회 성공을 각각 기록합니다. 전화·발신 성공으로 확대하지 않습니다.

공개 출시 전에는 별도로 새 production 서버를 검증하고 공개 주소 전환을 결정해야 합니다.
새 서버 전환 후 기존 OAuth 연결을 그대로 재사용할 수 있다고 가정하지 말고 재연결을 확인합니다.

## 외부와 내장에 같은 원고 공급

```sh
python3 -m pip install -r requirements-build.txt
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

- `dist/vox-ai-plugin.zip`: 외부 호스트 manifest, MCP 연결, 스킬과 references.
- `dist/vox-ai-skills.zip`: 동일한 스킬·references·digest. MCP 설정과 host manifest는 제외.
- `bundle-manifest.json`: 파일별 SHA-256, 묶음 digest와 capability directory.

내장 백엔드는 skill-only 파일을 `/workspace/vox-ai` 아래 공급하고
`/workspace/vox-ai/skills`를 Agents API capability directory로 등록합니다.
제품 호출은 service-origin MCP로 구성하며, 연결 자격 증명은 이 묶음이나 sandbox에 넣지 않습니다.

원고 출처·ElevenLabs에서 가져온 판단과 변경점은 `references/elevenlabs-adaptation.md`에 있습니다.
이 후보의 스킬 실행 품질과 전체 업무 완주는 아직 검증하지 않았습니다.

빌드는 catalog 경로·이름·layer와 실제 SKILL frontmatter, 호스트 manifest의 버전·연결,
marketplace의 plugin 경로를 검사합니다. 공통 원고 digest는 skills와 references의 내용만
나타내며, 외부 연결 설정이나 ZIP 전체의 digest가 아닙니다.
CI는 회귀 테스트·빌드·커밋된 bundle-manifest 일치를 확인하고 후보 ZIP을 artifact로 남깁니다.
배포 변경 시 두 host manifest의 버전을 함께 올리고 빌드해 bundle-manifest를 갱신합니다.
