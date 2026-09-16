# vox.ai Plugin

vox.ai의 원격 MCP 연결과 음성 업무 스킬을 배포하는 [공개 저장소](https://github.com/vox-public/plugin)입니다.
MCP 서버 구현은 `fleek-fitness/vox-mcp`에 있으며 이 저장소에는 포함하지 않습니다.
Plugin 이름은 `vox-ai`입니다. 현재는 구현 후보이며 외부 호스트 설치·로그인·업무 완주 검증은 아직 수행하지 않았습니다.

공통 스킬 26개는 general 8 / mcp 2 / architect 16으로 구성되며 `catalog.json`에 분류합니다.
Codex와 Claude Code가 모두 발견할 수 있도록 `skills/<name>/SKILL.md`에 배치합니다.
ElevenLabs Plugin의 연결 설정 + 업무 스킬 + 공통 references 구조를 참고했습니다.

## 연결과 사용

`.codex-plugin/plugin.json`과 `.claude-plugin/plugin.json`은 같은 스킬을 읽습니다.
`.mcp.json`은 `https://mcp.tryvox.co/mcp`에 연결합니다. 호스트의 OAuth 로그인으로 조직을 선택합니다.
설치 파일에 키를 저장하거나 대화에 사용자 토큰을 붙이지 않습니다.

현재 원격 endpoint는 이전 구현입니다. 새 서버 배포 전 이 후보를 출시 완료로 취급하지 마세요.
설계 도구 수 117은 런타임 지원 수가 아닙니다. 매 연결에서 실제 tools/list를 확인합니다.
저장 확인, 직접 음성 시험, 실제 전화 운영 완료는 따로 확인합니다.

## 외부와 내장에 같은 원고 공급

```sh
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
