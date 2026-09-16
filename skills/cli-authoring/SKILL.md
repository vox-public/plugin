---
name: cli-authoring
description: "사용자가 vox.ai 리소스를 저장소 파일·git·CI로 관리하거나 vox CLI 사용을 명시했을 때 적용한다. 일반적인 MCP 구축·수정을 CLI로 전환하지 않는다."
metadata:
  product: vox.ai
  layer: general
  status: authoring-draft-not-runtime-verified
---

# cli-authoring

## 적용 경로
사용자가 파일 기반 관리나 CLI를 선택했으면 기존 CLI를 활용한다. ‘저장’, ‘수정’, ‘개발 환경’이라는 단어만으로 CLI를 강제하지 않는다. MCP만으로 요청을 완결할 수 있는 기본 경로는 유지한다. hosted sandbox의 분석 파일을 만들었다는 이유로 CLI 배포 경로로 바꾸지 않는다.

## 작업 절차
1. 설치된 `vox --version`, `vox guide coding-agent --json`과 해당 하위 명령의 도움말을 읽어 실제 버전의 계약을 확인한다. 미설치면 사용자가 선택한 환경에 맞는 설치 방법을 공식 문서에서 확인한다.
2. 기존 저장소의 설정·수정 사항·대상 리소스 매핑을 읽는다. `vox auth whoami --json` 등 지원되는 조회로 프로필과 조직을 확인한다. 사용자가 정한 환경/조직을 모든 후속 명령에서 유지하며 출력에 credential을 포함하지 않는다.
3. 새로 가져오거나 덮어쓸 파일이 있으면 기존 변경을 보존한다. 설치 버전의 pull/import → 편집 → validate/status/diff → 요청 범위의 push 순서를 사용한다. 명령 이름·인자를 추측하지 않는다.
4. push는 실제 제품 변경이다. 검증과 diff만 요청했으면 push하지 않는다. 저장된 대상 ID와 실제 원격 상태로 반영을 확인한다. 로컬 검사 통과는 음성 시험 성공이 아니다.

## MCP와 함께 사용할 때
CLI 파일과 원격 제품을 동시에 독립 수정하지 않는다. MCP 변경 뒤 같은 파일을 push하면 무엇을 덮어쓰는지 먼저 diff로 확인한다. 자동 충돌 해결·롤백을 약속하지 않는다. 현행 CLI와 새 MCP의 리소스 표현이 다르면 지원되는 경로로 범위를 좁히고 차이를 설명한다.

설계 판단은 [voice-agent-design](../voice-agent-design/SKILL.md), 최신 CLI/설치 문서는 [product-documentation](../product-documentation/SKILL.md)을 참조한다. API 키를 공개 코드·스킬·sandbox 공용 파일에 기록하지 않는다.
