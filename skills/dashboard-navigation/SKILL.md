---
name: dashboard-navigation
description: "vox.ai 대시보드 사용법·설정 위치·통화 재생·제품 링크를 안내할 때 적용한다. 제품 업무 실행을 브라우저 조작으로 일괄 우회하지 않는다."
metadata:
  product: vox.ai
  layer: general
  status: authoring-draft-not-runtime-verified
---

# dashboard-navigation

## 필요한 화면으로 연결
질문이 화면 사용법이면 목적에 맞는 페이지와 현재 지원되는 동작을 설명한다. 제품 상태는 연결된 MCP로 확인하고, 화면 경로·딥링크는 현재 제품이나 공식 문서로 검증한다. 조직 ID·agent ID·call ID를 이름이나 다른 조직의 URL에서 추측하지 않는다.

현재 공개 제품 기본 경로는 `https://www.tryvox.co/dashboard/{organizationId}`다. 경로 구조나 쿼리 인자는 바뀔 수 있으므로 검증한 링크만 제공한다. 정적 링크를 제공한 것과 사용자가 로그인해 실제 화면을 열 수 있는 것을 구분한다.

## 호스트에 따른 동작
- 내장 코파일럿은 앱이 제공한 화면 전환·음성 진입 동작을 사용한다. 현재 페이지는 탐색 힌트이며 권한·최신 상태의 근거는 아니다.
- 외부 호스트에서는 제품 링크와 짧은 조작 안내로 완결할 수 있다. 사용 가능한 브라우저 도구가 있고 실제 조작을 요청한 경우에만 화면에서 확인한 요소를 사용한다. 특정 브라우저 확장 설치를 필수로 요구하지 않는다.
- 일반 제품 저장·번호 신청·발신 등은 공개 MCP 계약을 따른다. 구 플러그인의 ‘번호 구매는 UI 전용’ 같은 제한을 새 도구에 그대로 적용하지 않는다.

## 확인과 완료
통화 재생은 권한 있는 실제 call과 연결한다. 음성 시험 링크는 [prepare-voice-test](../prepare-voice-test/SKILL.md)의 대상·버전·결과 확인을 따른다. 링크 제공만으로 시험·발신·구매를 완료했다고 말하지 않는다. 문서가 오래되었거나 기능이 보이지 않으면 관찰한 상태와 확인되지 않은 동작을 구분한다.

세부 위치가 필요하면 [product-documentation](../product-documentation/SKILL.md), 내장/외부 차이는 [host-adapters](../../references/host-adapters.md)를 읽는다.
