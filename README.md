# vox.ai Plugin

Codex와 Claude Code에서 vox.ai에 연결하고 음성 에이전트를 설계·개선하는 플러그인입니다.
매뉴얼 작성, 도구 연결, 통화 결과 검토 등 업무별 지침 26개와 원격 MCP 연결 설정을 제공합니다.

현재 **preview**입니다. 스킬은 업무 진행 지침이며, 실행 가능한 기능은 연결된 서버가 제공하는 도구와 계정 권한에 따라 달라집니다. 로그인과 실제 업무 실행은 사용하는 환경에서 확인해야 합니다.

## 설치

아래 명령은 marketplace 파일이 포함된 변경이 `main`에 병합된 뒤 사용할 수 있습니다.

Claude Code:

```text
/plugin marketplace add vox-public/plugin
/plugin install vox-ai@vox-ai
```

Codex CLI:

```sh
codex plugin marketplace add vox-public/plugin
codex plugin add vox-ai@vox-ai
```

`plugin` 명령이 없는 호스트는 플러그인을 지원하는 버전으로 업데이트합니다.
로컬 변경을 시험하려면 marketplace 추가 명령에 복제한 저장소의 절대 경로를 지정합니다.

Claude Code 업데이트는 `/plugin marketplace update vox-ai`와 `/plugin update vox-ai@vox-ai`를 순서대로 실행합니다.
Codex의 업데이트 방법은 설치된 버전의 `codex plugin marketplace --help`에서 확인합니다.
업데이트 후 호스트 안내에 따라 다시 로드하고 새 대화에서 스킬을 확인합니다.

## 연결

플러그인은 `https://mcp.tryvox.co/mcp`에 연결합니다. 호스트에서 제공하는 OAuth 로그인 절차를 따르고 작업할 조직을 확인합니다.
키나 토큰을 대화에 붙여 넣거나 설치 파일에 저장하지 않습니다.

설치 후 연결된 서버의 도구 목록과 입력 스키마를 확인합니다. 필요한 도구가 없으면 준비한 초안과 남은 작업을 안내합니다. 설치 성공만으로 로그인이나 제품 작업이 완료된 것은 아닙니다.

## 사용 예

원하는 업무를 자연어로 요청할 수 있습니다.

- “예약 문의를 받는 음성 에이전트의 매뉴얼을 작성해줘.”
- “이 에이전트의 기존 설정을 확인하고 안내 문구를 수정해줘.”
- “최근 통화에서 고객이 반복해서 되묻는 부분을 찾아 개선안을 제안해줘.”

Claude Code에서는 `/vox-ai:voice-agent-design`처럼 스킬을 직접 호출할 수도 있습니다. Codex에서는 설치된 vox.ai 스킬을 선택하거나 관련 업무를 요청합니다.

변경 전 대상 조직과 리소스를 확인하고, 저장 후 다시 조회해 결과를 확인합니다. 실제 전화 발신과 메시지 전송은 대상·비용·영향 범위를 확인한 뒤 진행합니다. 음성 시험과 실제 전화 운영의 성공 여부는 각각 확인합니다.

전체 스킬 목록은 [catalog.json](catalog.json), 실행 원칙은 [execution-contract.md](references/execution-contract.md)에 있습니다.

## 빌드와 검증

```sh
python3 -m pip install -r requirements-build.txt
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

빌드는 스킬 목록·경로·메타데이터, 문서 링크, 호스트 설정과 버전 일치를 검증합니다.

- `dist/vox-ai-plugin.zip`: 호스트 manifest, MCP 연결 설정, 스킬과 공통 문서.
- `dist/vox-ai-skills.zip`: 같은 스킬과 공통 문서. 연결 설정과 호스트 manifest는 제외.
- `bundle-manifest.json`: 공통 파일별 SHA-256과 묶음 digest.

공통 digest는 스킬과 공통 문서만 대상으로 하며 ZIP 전체나 연결 설정의 digest가 아닙니다.
CI는 테스트와 빌드를 실행하고 커밋된 bundle manifest가 최신인지 확인합니다.
배포 변경 시 두 호스트 manifest의 버전을 함께 올리고 빌드해 bundle manifest를 갱신합니다.
