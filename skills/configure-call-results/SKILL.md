---
name: configure-call-results
description: "vox.ai 통화 후 추출·내부 결과 저장을 새로 연결하거나 수정·검증할 때 사용한다. 외부 CRM 작업의 성공과 구분한다."
metadata:
  product: vox.ai
  layer: architect
  status: authoring-draft-not-runtime-verified
---

# configure-call-results

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구명은 출시 설계이며 연결된 서버의 실제 도구·스키마 확인 후 사용한다.

## 설계와 기존 설정
[결과 설계](../post-call-result-design/SKILL.md)에 따라 필요한 필드와 완료 판정을 정한다. `get_agent`의 기존 postCall 설정과 연결 대상을 읽고 변경하지 않을 항목을 보존한다. 현재 지원하는 저장 대상과 필드 스키마를 확인한다.

## 저장
`save_agent`에 지원되는 postCall payload를 전달한다. 설정 그룹의 교체 의미에 따라 기존 필드를 포함한다. 고객·시트가 필요한 경우 현재 리소스를 먼저 조회하고 실제 지원되는 연결만 사용한다. 존재하지 않는 저장 대상이나 임의의 필드 타입을 만들지 않는다.

## 확인
설정 재조회와 실제 통화 결과 확인은 별도다. 시험 뒤 `get_call`의 실제 추출/분석 상태와 필요한 내부 저장 대상을 읽는다. 분석 대기, 정보 미수집, 저장 실패, 외부 전달 실패를 나눈다. 과거 콜을 현재 필드 설정으로 평가하지 말고 당시 버전/근거부터 확인한다.

합성 시험에는 값 정정, 제공 거절, 조기 종료를 포함한다. ‘설정 저장’, ‘실제 추출 확인’, ‘저장 대상 반영 확인’ 중 증명한 지점만 보고한다. 자동 후처리 재실행이나 과거 콜 재분석 도구를 가정하지 않는다.
