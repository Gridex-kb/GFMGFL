# GFM / GFL 지식창고 (Grid-Forming & Grid-Following Knowledge Base)

> **GFM(Grid-Forming, 계통형성)** 과 **GFL(Grid-Following, 계통추종)** 인버터 기술에 대한 한국어 지식창고입니다.
> 재생에너지·ESS 등 인버터 기반 자원(IBR, Inverter-Based Resource)이 전력계통을 지배하는 시대에
> 계통 안정성을 유지하기 위한 핵심 기술인 GFM/GFL의 **이론, 제어기법, 표준·계통코드, 실증 사례, 시험·검증 방법**을 정리합니다.

- 기준일: 2026-11-01 (이후 문서마다 `최종 갱신` 날짜 표기)
- 언어: 한국어 (기술용어는 영문 병기)
- 형식: Markdown (GitHub에서 바로 열람, Obsidian/VS Code 등에서도 사용 가능)

---

## 빠른 시작

| 관심사 | 먼저 읽을 문서 |
|---|---|
| GFM/GFL이 무엇인지 5분 안에 알고 싶다 | [00-개요/01-GFM-GFL이란](docs/00-개요/01-GFM-GFL이란.md) |
| 왜 지금 GFM이 중요한가 (IBR 전환, 관성 저하) | [00-개요/02-왜-GFM이-필요한가](docs/00-개요/02-왜-GFM이-필요한가.md) |
| 제어 블록도 수준으로 이해하고 싶다 | [02-GFL/01-GFL-제어구조](docs/02-GFL/01-GFL-제어구조.md) → [03-GFM/01-GFM-제어구조](docs/03-GFM/01-GFM-제어구조.md) |
| Droop / VSM / dVOC 등 GFM 제어기법 비교 | [03-GFM/02-GFM-제어기법](docs/03-GFM/02-GFM-제어기법.md) |
| 한 장짜리 GFM vs GFL 비교표 | [04-비교/01-GFM-vs-GFL-비교표](docs/04-비교/01-GFM-vs-GFL-비교표.md) |
| 2027년 국내 BESS GFM 요건, 해외 계통코드 | [05-표준-계통코드](docs/05-표준-계통코드/) |
| 실제 어디에 설치돼 있고 성과는 어땠나 | [06-실증-사례](docs/06-실증-사례/) |
| 시험·검증은 어떻게 하나 | [07-시험-검증/01-시험-검증-방법](docs/07-시험-검증/01-시험-검증-방법.md) |
| 용어가 헷갈린다 | [08-부록/01-용어집](docs/08-부록/01-용어집.md) |
| 3상 컨버터부터 차근차근 배우고 싶다 | [plans/3상컨버터부터-GFM-GFL-설명계획](plans/3상컨버터부터-GFM-GFL-설명계획.md) (Obsidian으로 열기 권장) |
| 발표용으로 한 번에 보고 싶다 | [slides/gfm-gfl-slides.html](slides/gfm-gfl-slides.html) (브라우저로 열기) |
| GFM과 GFL이 실제로 어떻게 다르게 움직이는지 보고 싶다 | [simulation/emt](simulation/emt/README.md) EMT 시뮬레이션 |

---

## 목차

### 00. 개요
- [01. GFM / GFL이란](docs/00-개요/01-GFM-GFL이란.md)
- [02. 왜 GFM이 필요한가 — IBR 전환과 계통 안정성](docs/00-개요/02-왜-GFM이-필요한가.md)

### 01. 기초 이론
- [01. 동기발전기, 관성, 계통강도(SCR)](docs/01-기초이론/01-동기기-관성-계통강도.md)
- [02. 계통연계 인버터의 기본 구조와 제어 계층](docs/01-기초이론/02-인버터-기본구조-제어계층.md)

### 02. GFL (Grid-Following, 계통추종)
- [01. GFL 제어 구조 — PLL, dq 전류제어](docs/02-GFL/01-GFL-제어구조.md)
- [02. GFL의 한계 — 약계통, PLL 불안정, 상호작용](docs/02-GFL/02-GFL-한계-약계통.md)

### 03. GFM (Grid-Forming, 계통형성)
- [01. GFM 제어 구조 — 전압원 동작의 원리](docs/03-GFM/01-GFM-제어구조.md)
- [02. GFM 제어기법 — Droop, VSM/VSG, Matching, dVOC, PSC](docs/03-GFM/02-GFM-제어기법.md)
- [03. 전류 제한과 고장 대응 (Fault Ride-Through)](docs/03-GFM/03-전류제한-고장대응.md)
- [04. GFM 핵심 기능 — 관성, 위상 점프 응답, 블랙스타트, 단독운전](docs/03-GFM/04-GFM-핵심기능.md)

### 04. 비교
- [01. GFM vs GFL 비교표](docs/04-비교/01-GFM-vs-GFL-비교표.md)
- [02. 하이브리드·모드 전환·혼합 계통](docs/04-비교/02-하이브리드-혼합계통.md)

### 05. 표준 · 계통코드
- [01. 국제 표준 및 해외 계통코드](docs/05-표준-계통코드/01-국제표준-해외계통코드.md)
- [02. 한국 — 2027년 BESS GFM 요건과 국내 제도](docs/05-표준-계통코드/02-한국-제도-요건.md)

### 06. 실증 · 사례
- [01. 해외 프로젝트](docs/06-실증-사례/01-해외-프로젝트.md)
- [02. 국내 동향](docs/06-실증-사례/02-국내-동향.md)
- [03. 제조사·제품 현황](docs/06-실증-사례/03-제조사-제품-현황.md)
- [04. 교훈과 운영 이슈](docs/06-실증-사례/04-교훈-운영이슈.md)

### 07. 시험 · 검증
- [01. 시험·검증 방법 — 모델링, HIL, 성능시험](docs/07-시험-검증/01-시험-검증-방법.md)

### 09. EMT 시뮬레이션
- [GFM vs GFL 평균값 EMT 시뮬레이션](simulation/emt/README.md) — 위상 점프, RoCoF, 약계통 안정도 맵, 3상 고장, 단독운전
- [결과 요약](simulation/emt/results/summary.md)

### 11. 계획
- [3상 컨버터부터 GFM·GFL까지 설명 계획](plans/3상컨버터부터-GFM-GFL-설명계획.md) — Obsidian 노트, 강의 13편 구성·체크리스트

### 10. 발표 자료
- [HTML 슬라이드 (17장)](slides/gfm-gfl-slides.html) — 개념·표준·국내 요건·실증·EMT 결과. 사용법은 [slides/README.md](slides/README.md)

### 08. 부록
- [01. 용어집](docs/08-부록/01-용어집.md)
- [02. 참고문헌 · 링크 모음](docs/08-부록/02-참고문헌.md)
- [03. FAQ](docs/08-부록/03-FAQ.md)

---

## 문서 작성 규칙

- 새 문서는 [templates/문서-템플릿.md](templates/문서-템플릿.md)를 복사해 작성합니다.
- 수치·연도·요건은 반드시 출처(URL 또는 문서번호)를 함께 적습니다. 출처가 없는 내용은 `(확인 필요)`로 표시합니다.
- 자세한 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 라이선스

내부 지식 공유 목적. 외부 공개 시 각 참고문헌의 저작권을 확인하세요.
