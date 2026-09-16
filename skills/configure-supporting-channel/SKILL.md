---
name: configure-supporting-channel
description: "vox.ai 채팅·위젯을 구성하거나 음성 업무를 보조 채널로 확장하고 실제 대화·설정 결과를 확인할 때 사용한다."
metadata:
  product: vox.ai
  layer: architect
  status: authoring-draft-not-runtime-verified
---

# configure-supporting-channel

제품 호출에는 [공통 실행 계약](../../references/execution-contract.md)을 적용한다. 내장/외부의 질문·음성·파일 차이는 [호스트 연결](../../references/host-adapters.md)을 따른다. 도구명은 출시 설계이며 연결된 서버의 실제 도구·스키마 확인 후 사용한다.

## 재사용 범위
업무 지식·수집 항목은 재사용할 수 있지만 음성의 무응답·끼어들기·전화 전환·종료 계약을 채팅에 그대로 적용하지 않는다. agent/Manual의 채널 지원은 실제 제품 계약에서 확인한다. 자동 고객 식별·음성→채팅 맥락 인계는 이번 출시의 완성 기능으로 가정하지 않는다.

## 실행
기존 widget/chat/agent를 읽고 필요한 설정만 저장한다. `save_widget`와 `publish_widget`는 다른 동작이다. 테스트 채팅은 지원되는 create/message/get/end 계약으로 수행하고 필요 횟수·범위를 제한한다. 이미 진행 중인 사용자 대화를 임의로 종료하지 않는다.

## 완료와 예외
위젯 설정 저장, 게시, 실제 페이지 접근, 실제 대화 성공을 구분한다. 음성 테스트 성공이 채팅 성공을 보장하지 않는다. 채팅 결과 저장은 해당 채널의 실제 지원 의미를 따르며 postCall을 모든 채널의 공통 계약으로 강제하지 않는다.

설정/게시 후 재조회하고 사용자에게 접속 위치·시험 질문·확인할 결과를 전달한다. 미지원 mode나 embed 계약이면 정확한 부족한 조건을 알리고 SDK·REST로 조용히 우회하지 않는다.
