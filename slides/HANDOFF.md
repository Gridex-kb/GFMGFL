# 강의 슬라이드 작업 이관 문서

새 세션에 아래 **「이관 프롬프트」** 블록을 그대로 붙여 넣으면 이어서 작업할 수 있다. 나머지 절은 그 프롬프트가 가리키는 참고 자료다.

---

## 이관 프롬프트

```text
저장소 Gridex-kb/GFMGFL, 브랜치 claude/gfm-gfl-knowledge-base-u5f770 에서 이어서 작업한다.
(커밋·푸시는 이 브랜치로. PR은 만들지 않는다.)

목표: 한국어 강좌 "3상 컨버터에서 GFM까지"의 강의용 슬라이드 덱(Claude Artifact, Slides 타입)과
실습 Python 파일을 강의별로 만든다. 1~4강은 끝났다. 5강부터 이어서, 최소한 GFM과 GFL 비교 강의
(8~10강)까지 완성해야 한다.

먼저 slides/HANDOFF.md 를 끝까지 읽어라. 거기에 다음이 있다:
- 강의 번호와 교재(docs/09-강좌-3상컨버터에서-GFM까지/C??.md) 대응표와 진행 상황
- 그림·수식 파이프라인(slides/tools: KaTeX + Playwright + figlib.js) 사용법과 주의점
- 슬라이드 HTML 규칙과 레퍼런스 덱(slides/decks/L04 가 가장 최신 기준)
- Artifact 덱 만드는 절차(Slides 타입 URL, GriDeX 디자인 시스템 설치 항목)
- 실습 파일 규칙(practice/)
- 5강 진행 중인 상태와 다음 단계

작업 방식(사용자가 정한 것):
- 표기는 pu만, 실습은 Python만, 3레벨(C03B)은 다루지 않는다. 변조(C04)는 맨 마지막 12강.
- 수식은 LaTeX(KaTeX) 렌더링 이미지, 그림은 figlib(SVG + KaTeX 라벨)로 보기 좋게.
- 한 장에 그림 하나, 질문→답, 목차 반복(섹션 구분 슬라이드), 정리 상자, 칠판 유도 슬라이드,
  예제 문제→풀이, Python 실습 장, 비교표, 마무리(세 가지 + 퀴즈 2 + 다음 강의).
  모든 장에 한국어 발표자 노트(강의 대본).
- 숫자는 교재·시뮬레이션 결과에서만 가져온다. EMT 결과는 실제로 돌려서 확인한다.
- 강의마다: 그림·수식 렌더 → 밀착 인화로 겹침 확인·수정 → 에셋 업로드 → 덱 작성 →
  practice/lecNN_*.py 작성·실행 확인 → slides/decks/LNN 에 소스 보관 → 커밋·푸시.

지금 할 일: 5강(전류 제어, 교재 C07)부터. HANDOFF.md 의 "5강 진행 상황"을 보고 이어서 하라.
```

---

## 1. 강의 대응표와 진행 상황

| 강 | 교재 | 주제 | 상태 | 덱 |
|---|---|---|---|---|
| 1 | C01, C02 | 3상 표현, 공간벡터·dq | 완료 (27장) | https://claude.ai/artifact/CBBYpGPpVqKFqibBtt3gqN |
| 2 | C03 | 2레벨 VSC | 완료 (28장) | https://claude.ai/artifact/XopWStHpdKwfmjyfY9CFuE |
| 3 | C05 | 필터·변압기·측정점 | 완료 (28장) | https://claude.ai/artifact/DX9a9RYjLDDG6ttdoBMWWL |
| 4 | C06 | 디지털 제어와 지연 | 완료 (25장) | https://claude.ai/artifact/93NgxzEDhLFhZjYDUHwGq4 |
| 5 | C07 | 전류 제어 | 완료 (29장) | https://claude.ai/artifact/51RKpHpVQLEsiGdpo3kbC6 |
| 6 | C08 | GFL: PLL로 따라가기 | 완료 (29장) | https://claude.ai/artifact/Wo9iBotEeCnNRCn85mqMUf |
| 7 | C09 | GFM: 위상을 만들기 | 완료 (29장) | https://claude.ai/artifact/XMojcAmfAh8qbCC4zxSXFw |
| 8 | C10 | 약계통과 제어 상호작용 (GFM vs GFL) | **다음** · 필수 | — |
| 9 | C11 | 전류 제한과 고장 (GFM vs GFL) | 예정 · **필수** | — |
| 10 | C12 | 표준 시험으로 비교 (GFM 12/14, GFL 3/14) | 예정 · **필수** | — |
| 11 | C13 | EMT 모델링 실습 | 이후 | — |
| 12 | C04 | 변조 SPWM·SVPWM (맨 마지막) | 이후 | — |

- 3레벨(C03B)은 사용자 요청으로 제외. 교재 파일은 남아 있다.
- 슬라이드 본문·노트 안의 강의 번호 참조는 위 번호를 따른다(예: "6강 GFL", "7강 GFM", "12강 변조").
- 덱 URL 목록: `slides/decks/artifacts.txt`. 덱은 모두 비공개(공유는 사용자가 Share 메뉴에서).

## 2. 파일 위치

| 경로 | 내용 |
|---|---|
| `slides/tools/` | `figlib.js`·`figlib.css`(그림 라이브러리), `render.mjs`(렌더러), `sheet.py`(밀착 인화), `package.json` |
| `slides/figs-src/LNN/` | 강의별 그림 소스 `*.fig.js`, 공통 함수 `_common.js`, 수식 `eqs.tex`, EMT 데이터 생성 `_data.py`와 그 결과 `*.json` |
| `slides/lecture-figs/LNN/` | 렌더된 PNG(2배 해상도)와 `manifest.json`(슬라이드에 넣을 CSS 크기) |
| `slides/decks/LNN/project/` | 덱 소스(`deck.json`, `slides/*.html`). 에셋 URL(`/_blob/…`)은 그 덱 Artifact 전용 |
| `practice/` | 실습 파일 `lec01~04_*.py`, `common.py`, `README.md` |
| `docs/09-강좌-3상컨버터에서-GFM까지/` | 교재 C00~C13 |
| `docs/_assets/강좌/scripts/CNN_figs.py` | 교재 그림 스크립트. EMT 데이터 뽑는 코드를 여기서 가져온다 |
| `simulation/emt/` | EMT 모델 `gfm_gfl_emt.py`, 결과 `results/`, 표준 시험 `compliance_tests.py` |

## 3. 그림·수식 파이프라인

설치(새 컨테이너에서 한 번):
```bash
cd slides/tools && npm install        # katex@0.16.11, pretendard@1.3.9 (package.json에 있음)
```
렌더:
```bash
cd slides/tools
node render.mjs ../figs-src/L05 ../lecture-figs/L05                 # 전부
ONLY=M03-보드,E02-이득 node render.mjs ../figs-src/L05 ../lecture-figs/L05   # 일부만
python3 sheet.py ../lecture-figs/L05 <scratchpad>/sheet.png "M*.png"   # 밀착 인화 → Read 로 눈으로 확인
```
- 그림 파일 하나 = `NAME.fig.js`. `const F = Fig(w, h)`로 시작해 `F.done()`으로 끝낸다. 같은 이름의 `NAME.json`이 있으면 `window.DATA`로 들어간다. `_common.js`는 모든 그림 앞에 실행된다.
- **그림 크기 = 슬라이드에 넣을 크기**로 설계한다(PNG는 2배). 내용 영역은 1664×824, 제목 한 줄이면 그림 높이는 약 640 이하.
- figlib API 요약:
  - `F.frame([x,y,w,h], xlim, ylim).axes({xticks, yticks, xfmt, yfmt, xlabel, ylabel, tick})` → `A.fn(f)`, `A.plot(xs, ys, style)`, `A.vline/hline`, `A.label(x, y, tex, {anchor, size, color, weight, bg})`, `A.arrow`
  - `F.plane(cx, cy, R)` → `P.vec(z)`, `P.axis(deg, len, label)`, `P.arc`, `P.label`, `P.pol(m, deg)`
  - 도형: `F.line/poly/path/rect/circle/dot/arrow/arc/label`, 회로: `F.wire/node/cap/inductor/resistor/igbt/toggle/source/ground`, 블록선도: `F.block/sum`
  - 색: `FC.navy blue orange green slate muted grid axis light lime teal`, 상 색 `FC.a/b/c` = 파랑/주황/초록
  - 라벨 문자열의 `$...$`는 KaTeX로 조판된다.
- 수식 `eqs.tex`: `%% 이름 [size=40]` 머리줄 다음에 LaTeX 본문. 기본 40px. `\textcolor{#eb6834}{...}`, `\underbrace`, `aligned`, `bmatrix` 사용 가능.
- 자주 난 문제
  - 축 라벨이 위·아래로 잘림 → frame의 y를 60 이상, 캔버스 높이를 여유 있게.
  - 오른쪽 직접 라벨이 잘림 → frame 폭을 줄이고 라벨 x를 안쪽으로.
  - KaTeX `\text{}` 안의 `·`는 오류(`\cdotp`) → 쉼표 등으로.
  - `xfmt`를 안 주면 `fmt`가 x축에도 적용된다.
- EMT 데이터는 `_data.py`에서 뽑아 JSON으로 저장(교재 `CNN_figs.py`의 시뮬레이션 부분을 옮김). 결과 수치가 교재와 맞는지 출력해 확인한다.

## 4. 슬라이드 덱 규칙

**레퍼런스: `slides/decks/L04/project/slides/` 를 템플릿으로 복사해 쓴다.** 장 종류별 파일:

| 종류 | 예시 파일 | 핵심 |
|---|---|---|
| 표지 | `cover.html` | 남색 배경, 교재·실습 파일, 75분·pu |
| 목표 | `goals.html` | 번호 카드 3~4개 |
| 목차 | `outline.html` | 2×2 카드 |
| 질문 / 답 | `q-delay.html`, `a-delay.html` | 질문(주황 머리표) → 답(초록 머리표) |
| 섹션 구분 | `sec1.html` | 큰 숫자 + 목차, 현재 항목만 흰색 강조 |
| 그림+설명 | `sync.html`, `phase.html` | 왼쪽 그림(흰 배경, 테두리), 오른쪽 카드 |
| 칠판 유도 | `zoh.html`, `derive.html` | ①②③ 단계 수식 이미지, 노트에 판서 순서 |
| 한 문장 | `msg.html` | 파랑 배경 강조 장 |
| 정리 | `sum1.html` | 2부 끝마다 굵은 테두리 상자 |
| 사례 | `case.html` | EMT 그림 + 증상/해결/교훈 카드 |
| 예제 | `ex1q.html` → `ex1a.html` | 문제(시간 알약) → 풀이(수식 + 표) |
| 실습 | `code.html` | 코드(JetBrains Mono, 들여쓰기는 `&#160;`), 출력, 실습 파일 경로 |
| 비교 | `compare.html` | 표 |
| 마무리 | `wrap.html` | 세 가지 + 퀴즈 2(답은 노트) + 다음 강의 |

- 캔버스 1920×1080, 여백 `padding:128px 128px 160px`, 위쪽 12px 그라데이션 띠, 바닥 줄에 강의명과 `n / N`.
- 글자 크기: 제목 56, 본문 26~34, 머리표 24, 최소 24. 제목은 한 줄(한글 약 26자 이하)로.
- 세로 예산 824px: 제목 한 줄 ≈ 150px + gap. 표 한 줄 ≈ 2.1 × 글자 크기.
- 쓰지 말 것: `<sub>`, `<sup>`, `margin`, 중첩 `<b>`. 아래 첨자는 `i<b>d</b>` 또는 `<span style="color">`로.
- 색: 남색 `#013364`, 파랑 `#2463c8`, 초록 `#8bc22c`/`#3aa150`, 연두 `#b9f179`, 청록 `#037673`, 주황 `#eb6834`, 본문 `#45546b`, 회색 `#7d8ca2`, 연한 배경 `#e9f0f6`, 페이지 배경 `#fbfcfd`, 어두운 카드 `#0f233f`.
- 수식은 반드시 KaTeX 이미지로 넣는다(`img`, `object-fit:contain`, manifest 크기 그대로 또는 비례 축소).

## 5. Artifact 덱 절차

1. 생성: Artifact publish, `type_url` = `https://claude.ai/artifact/8jTsAFQMFDb2oA8MsPJ2eL`(Slides 타입), `title` = "N강 · 주제", `auto_open: "after_first_write"`.
2. 에셋 업로드: `action: publish, url: <새 덱>, asset: true, file_paths: [...]`(한 번에 25개까지). 돌려받은 `/_blob/<id>`를 `img src`에 그대로.
3. scratchpad의 한 폴더(`<root>`)에 `project/deck.json`을 먼저 쓴다(L04의 deck.json을 복사해 title/order/sections/createdOnFiles 수정). `designSystems` 기록은 그대로:
   `{"title":"GriDeX 디자인 베이스","namespace":"gridex","artifact":"https://claude.ai/artifact/DHKyReZeUdghmptteJUFVb","version":null,"copiedAt":"<지금>"}`
   글꼴: `pretendard-variable` → `src: project/ds/gridex/fonts/PretendardVariable.woff2`, `jetbrains-mono` → Google Fonts href.
4. 첫 publish: `file_path`=deck.json, `root`=<root>, `files`에 표지와 디자인 시스템 설치 항목:
   ```json
   {"project/slides/cover.html": "project/slides/cover.html",
    "project/ds/gridex/tokens.json": {"artifact": "https://claude.ai/artifact/DHKyReZeUdghmptteJUFVb", "path": "project/tokens.json"},
    "project/ds/gridex/fonts/PretendardVariable.woff2": {"artifact": "https://claude.ai/artifact/DHKyReZeUdghmptteJUFVb", "path": "project/fonts/PretendardVariable.woff2"}}
   ```
5. 이후 세 장씩 Write → publish(같은 url·root).
6. 끝나면 `slides/decks/LNN/project`로 복사, `artifacts.txt`에 URL 추가, 커밋·푸시.
- **기존 덱(1~4강) 수정**은 새 세션에서 먼저 `action: read`로 해당 파일을 읽고 고친다(읽지 않은 덱에 publish하면 거절된다). 로컬 원본은 `slides/decks/LNN/project`.

## 6. 실습 파일 규칙 (`practice/`)

- 파일명 `lecNN_<영문주제>.py`, `from common import header, check, parse, plt_ready, savefig, ...`
- 구성: 모듈 docstring(실행법·실습 목록) → `practice_1..n(args)` → `try_a/try_b`(해보기, `바꿔 보기` 주석, `--answers`면 답) → `__main__`.
- 옵션: `--plot`(그림 `practice/out/`), `--emt`(EMT 실습), `--answers`. 기대값은 `check(name, value, expected, tol)`로 `[OK]` 표시.
- 작성 후 `python practice/lecNN_*.py --plot --emt --answers`로 실제 실행해 모든 `[OK]`를 확인. `practice/README.md` 표에 한 줄 추가. 덱 code 장에 파일 경로를 적는다.

## 7. 5강(전류 제어, C07) 완료 메모

- 그림 `slides/figs-src/L05/M01~M07`(블록선도, 계단응답, 보드, 피드포워드 EMT, 되먹임 루프, 전류 제한 3패널, anti-windup), 수식 `E01~E12`. 공통 `_common.js`에 개루프 `openLoop()`/`crossover()`가 있어 보드 그림이 수치를 직접 계산한다.
- EMT 결과(`_data.py` 실행, 약 40 s): σ(P) 0.004 / 0.117 / 0.004 pu, 순시 피드포워드 진동 560 Hz — 교재와 일치.
- 덱 29장. 실습 `practice/lec05_current_control.py` 전부 `[OK]`.
- **Windows에서 작업할 때 주의**
  - `render.mjs`는 `fileURLToPath`로 고쳤다(이전 `URL.pathname`은 `C:\C:\…` 오류). `slides/tools/package.json`에 playwright를 넣었으니 `npm install && npx playwright install chromium`.
  - Artifact 에셋 업로드가 저장소 안의 PNG를 "hard link"라며 거절하면(Downloads 폴더 등), scratchpad로 `cp`한 뒤 그 경로로 올린다.
  - `practice/common.py`가 stdout을 UTF-8로 재설정하므로 cp949 콘솔에서도 `−`, `ω`가 깨지지 않는다.
  - bash heredoc으로 Korean 파일명을 여러 개 쓰면 따옴표 오류가 나기 쉽다. 파일은 Write 도구로 하나씩 쓴다.

## 7b. 6강(GFL, C08) 완료 메모

- 그림 `slides/figs-src/L06/N01~N07`(GFL 구조, PLL 블록, PLL 대역폭 numpy, 위상 점프 EMT, FRT 순환 EMT, 전류원 벡터, FRT 상태도), 수식 `E01~E12`. 데이터 `_data.py`(평균값 모델, 약 60 s).
- 확인한 수치: 점프 직후 Δf0 −4.8/−9.7/−24.2 Hz, 20 Hz PLL 54.00 Hz·정착 47 ms, ΔP +0.007 pu; FRT 0.85 → |v| 0.37~1.28, 54~66 Hz; 진입 0.5 → 최저 0.74, 1.00 pu 유지. 교재와 일치.
- 덱 29장, 실습 `practice/lec06_gfl_pll.py` 전부 `[OK]`.
- figlib 라벨 문자열은 JS 문자열이므로 `\,`, `\approx`처럼 역슬래시를 두 번 쓴다(한 번 쓰면 KaTeX 오류·공백).

## 7c. 7강(GFM, C09) 완료 메모

- 그림 `slides/figs-src/L07/G01~G07`(GFM 구조, P–δ, VSM 블록, 위상 점프 GFM/GFL EMT, 등가 회로, 주파수 계단 H 1/4/8, 동기화 루프), 수식 `E01~E12`, `_common.js`에 P–δ·Ks 계산. 데이터 `_data.py`(평균값, 약 90 s).
- 확인한 수치: 위상 점프 GFM +0.636(10 ms)/+0.498(10~30 ms 평균), 페이저 0.482, GFL +0.007; 주파수 계단 정상상태 +0.169(드룹 0.167), 최대 0.184/0.287/0.397 (H 1/4/8). 교재와 일치.
- 덱 29장, 실습 `practice/lec07_gfm_vsm.py` 전부 `[OK]`.

## 8. 6강 이후 메모

- 6강 C08 GFL: SRF-PLL(Kp = 2ζωn/ωb, Ki = ωn²/ωb, ±10 % 제한), PLL 대역폭, P/Q 제어, FRT(0.85 진입, 0.92·30 ms 복귀, iq = 0.95·Imax). 교재 그림: PLL 대역폭, FRT 순환, 위상점프 GFL.
- 7강 C09 GFM: VSM 2H·dΔω/dt = P* − P − DΔω (H 4 s, D 50 = 2 % 드룹), 동적 가상 인덕턴스 Xv 0.3, Rv 0.05, P–δ 곡선. 위상 점프 GFM +0.64 pu vs GFL +0.01 pu.
- 8강 C10 약계통: SCR 급변 안정도 맵(GFL PLL 10/35 Hz는 SCR 1.3부터, 50 Hz는 1.5부터 불안정, GFM은 1.2까지 안정), 진동 유형 두 가지, GFM 감쇠 ζ 30.7 % @ 1.27 Hz.
- 9강 C11 전류 제한·고장: 제한 중 가속 정지 보정(회복 0.95 → 0.48 s), 60° 위상점프에서 제한 고착(T09), 고장 중 평균 PCC 전압 GFL 0.71 vs GFM 0.63 pu, 2.0 pu·140 ms.
- 10강 C12 표준 시험: T01~T13(14건) GFM 12/14, GFL 3/14. 보고서 `reports/gfm-gfl-test-report.html`, 원자료 `simulation/emt/.cache/compliance_raw_2us.pkl`(캐시라 없으면 `compliance_tests.py`로 재생성), 요약 `simulation/emt/results/compliance.json`.
- 숫자는 반드시 교재와 `simulation/emt/README.md`, `results/`에서 확인하고 쓴다.

## 9. 다운로드

- 덱: 각 덱 페이지의 Share › Export에서 PPTX 또는 PDF로 받을 수 있다.
- 실습·그림 소스: GitHub 브랜치 `claude/gfm-gfl-knowledge-base-u5f770`의 `practice/`, `slides/`. 브랜치 전체 zip:
  `https://github.com/Gridex-kb/GFMGFL/archive/refs/heads/claude/gfm-gfl-knowledge-base-u5f770.zip`
