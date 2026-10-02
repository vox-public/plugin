# 개발

이 문서는 plugin 저장소를 수정하거나 배포 묶음을 만드는 개발자용입니다. 설치와 사용법은 [README.md](README.md)를 봅니다.

## 목차

- 빌드와 검증
- 번들 구성
- 스킬 목록과 도구 참조
- 연결된 도구와 snapshot
- 작업 기록(work context) 도구 계약
- 로컬에서 시험하기

## 빌드와 검증

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build.py
```

빌드는 스킬 목록·경로·메타데이터, 문서 링크, 구현 tool/schema snapshot, 워크플로 required/optional capability, JSON 예제 입력 schema, 호스트 설정과 버전 일치를 검증합니다. `scripts/build.py --mcp-root <mcp-checkout>` 또는 `scripts/build.py --manifest <manifest.json>`을 주면 pinned MCP manifest와 tool schema digest도 대조합니다. 번들된 [구현 도구 스냅샷](references/implemented-tools.snapshot.json)은 원본 MCP commit·manifest digest와 각 입력 schema digest를 기록합니다.

## 번들 구성

- `dist/vox-ai-plugin.zip`: 호스트 manifest, MCP 연결 설정, 스킬과 공통 문서.
- `dist/vox-ai-skills.zip`: 같은 스킬과 공통 문서. 연결 설정과 호스트 manifest는 제외.
- `bundle-manifest.json`: 공통 파일별 SHA-256과 묶음 digest.

공통 digest는 스킬과 공통 문서만 대상으로 하며 ZIP 전체나 연결 설정의 digest가 아닙니다.
CI는 테스트와 빌드를 실행하고 커밋된 bundle manifest가 최신인지 확인합니다.
배포 변경 시 두 호스트 manifest의 버전을 함께 올리고 빌드해 bundle manifest를 갱신합니다.

## 스킬 목록과 도구 참조

전체 스킬 목록은 [catalog.json](catalog.json)에 있습니다. 각 스킬의 `tools.implemented`는 현재 snapshot에서 실행 가능한 도구이고 `tools.designed_only`는 지침에 남아 있는 설계 참조입니다. 상단 `designed_tool_references`가 해당 참조의 전체 목록입니다. 실행 원칙은 [execution-contract.md](references/execution-contract.md)에 있습니다.

## 연결된 도구와 snapshot

설치 후 연결된 서버의 도구 목록과 입력 스키마를 확인합니다. 번들에는 첫 배포 범위 도구(조직·agent·버전·템플릿·Manual·도구·지식·번호·통화·캠페인·시트·고객)와 work context·record·operation 도구의 schema 후보가 있습니다. 외부 공개 연결에는 작업 기록 도구가 없을 수 있으며 그때는 현재 대화나 handoff로 이어갑니다. 실제 호스트의 노출 도구와 권한은 다를 수 있습니다. workflow별 capability는 [workflow-capabilities.json](references/workflow-capabilities.json), 입력 schema와 출처 상태는 [implemented-tools.snapshot.json](references/implemented-tools.snapshot.json)에 있습니다.

## 작업 기록(work context) 도구 계약

`get_work_context`는 자동 기록이 기본 켜짐인지와 현재 settings revision/epoch를 반환합니다. routine case/event를 저장하기 전 최신 값을 읽고 둘을 요청에 복사하며, 꺼져 있거나 값이 바뀌면 automatic API가 쓰기를 거부하므로 저장하지 말고 설정 변경 또는 새 context를 기다립니다. 사용자가 현재 대화에서 저장하지 말라고 직접 요청하면 설정과 무관하게 기록하지 않습니다. OFF는 자동 수집·기록을 중지하지만 사용자가 명시적으로 요청한 기존 기록 조회·정정·삭제는 지원합니다. user-principal `save_agent`/`save_manual`에는 별도로 직전 `get_work_context`의 일회용 receipt가 필요하며, 이 읽기는 `max_tokens`를 기본값(3000) 아래로 낮추지 않고 `MEMORY_CONTEXT_BUDGET_TOO_SMALL`이 오면 `details.required_tokens`로 한 번만 다시 호출합니다. 작업 기록 도구가 없는 호스트에서는 receipt 없이 저장을 시도하고 서버가 거부하면 초안을 안내합니다. 설치 성공만으로 로그인, 도구 노출 또는 제품 작업이 완료된 것은 아닙니다.

`get_work_context`의 각 항목은 일반 claim/case/evidence에 `guidance: null`을 포함하고, guidance 항목에는 종류·상태·현재 지침·보존 조건·버전이 든 typed object를 포함합니다. `evaluation_reported.register_holdout`은 별도 text-contract 사례 등록에만 사용하며, 사용자가 현재 임베디드 Copilot 대화에서 직접 입력한 본인의 말을 출처로 명시적 경로에서만 등록되며, 출처 ID는 `get_work_context`의 `pending_recent_inputs`에 있는 해당 입력의 값을 사용하고, 시나리오는 JSON 문자열 대신 구조화 필드 `holdout_scenario`(`base_configuration`, `requested_change`, `required_preservation`)로 보냅니다(등록 가능 여부는 호스트 이름이 아니라 `get_work_context`를 먼저 호출해 해당 항목이 있는지로 판단합니다). 등록이나 자동 text 비교는 실제 voice test가 아니며, 고객이 직접 수행한 시험 결과는 계속 고객 보고로 표시합니다.

## 로컬에서 시험하기

로컬 변경을 시험하려면 marketplace 추가 명령에 복제한 저장소의 절대 경로를 지정합니다.

```text
/plugin marketplace add <복제한 저장소의 절대 경로>
```

```sh
codex plugin marketplace add <복제한 저장소의 절대 경로>
grok plugin marketplace add <복제한 저장소의 절대 경로>
```
