# GFM 제어기법 — Droop, VSM/VSG, Matching, dVOC, PSC

> 요약: 대표적인 GFM 동기화 제어기법의 원리, 수식, 장단점을 비교한다. 모두 "위상을 전력으로부터 만든다"는 공통점을 가지며, 관성·댐핑·비선형성의 구현 방식이 다르다.
> 최종 갱신: 2026-11-01 · 상태: 초안

## 핵심 요약 (TL;DR)

| 기법 | 핵심 식 (요지) | 관성 | 장점 | 단점 |
|---|---|---|---|---|
| **P–f Droop** | $\omega = \omega_0 + m_p(P^*-P)$ | LPF가 간접 제공 | 단순, 검증됨, 병렬운전 용이 | 관성 명시적 조정 불가 |
| **VSM / VSG** | $J\dot\omega = P^*-P-D(\omega-\omega_0)$ | 명시적 ($J$, $H$) | 동기기와 등가, 계통코드 대응 쉬움 | 과소 댐핑·전력 진동 가능 |
| **Synchronverter** | 동기기 전자기 모델 전체 구현 | 명시적 | 물리적 유사성 높음 | 복잡, 전류 제한 어려움 |
| **Matching control** | DC링크 전압 ↔ 주파수 매칭 | DC 커패시터가 관성 | 하드웨어 상태 활용, 에너지 일관성 | DC 전압 변동 허용 필요 |
| **dVOC (dispatchable VOC)** | 비선형 진동자 동역학 | 암묵적 | 대신호 안정성 증명, 빠른 동기화 | 상대적으로 신규, 상용 사례 적음 |
| **PSC (Power Synchronization Control)** | $\dot\theta = \omega_0 + k_p(P^*-P)$ + 고장 시 PLL 전환 | 작음 | HVDC에서 검증 (ABB/Hitachi) | 정상/고장 모드 전환 필요 |

## 1. P–f / Q–V Droop

$$\omega = \omega_0 + m_p (P^* - P_{f}), \qquad E = E_0 + n_q (Q^* - Q_{f})$$

여기서 $P_f = \dfrac{\omega_c}{s+\omega_c} P$ (LPF). 소신호 해석하면

$$\dot\omega \approx \omega_c\,[\omega_0 + m_p(P^*-P) - \omega]$$

→ 1차 지연이 **등가 관성** $2H_{eq} \approx \dfrac{1}{m_p \omega_c}$, 등가 댐핑 $D_{eq} = 1/m_p$ 처럼 작용한다. 즉 Droop + LPF는 VSM의 특수한 경우다.

- 드룹 계수: 통상 $m_p$ = 2~5 % (정격 출력 변화에 대한 주파수 변화율), $n_q$ = 5~10 %.
- 배전급(X/R 낮음)에서는 P–V, Q–f가 섞이므로 가상 리액턴스로 "유도성"을 만들거나 역드룹/변환 행렬을 사용.
- 마이크로그리드·UPS 병렬운전에서 가장 오래 검증된 방식. 많은 상용 GFM PCS의 기본형.

## 2. VSM / VSG (가상동기기)

스윙 방정식을 그대로 구현:

$$J\frac{d\omega}{dt} = \frac{P^* - P}{\omega_0} - D(\omega - \omega_g), \qquad \theta = \int \omega\,dt$$

- $J$ (또는 $H$) 로 관성, $D$로 댐핑을 **독립적으로** 설정한다. 계통코드가 "관성상수 H = x s 이상"을 요구할 때 직접 대응된다.
- $\omega_g$(계통 주파수) 피드백이 필요한 댐핑 항은 PLL을 쓰기도 하고(순수 GFM 논쟁의 대상), $\omega_0$로 대체하면 드룹과 동일해진다.
- 무효전력 측은 AVR 유사 루프: $E = E_0 + \frac{1}{s K_q}(Q^* - Q) + k_v(V^*-V)$.
- 주의: $H$ 크고 $D$ 작으면 **저주파 전력 진동**(동기기 로터각 진동과 동일)이 생긴다. 가상 PSS·추가 댐핑 루프를 붙이기도 한다.
- 변형 명칭: VISMA(2007, Beck & Hesse), Synchronverter(2011, Zhong), ISE lab VSG(일본), Virtual Synchronous Generator(VSG, 중국·일본 문헌에서 흔함).

## 3. Synchronverter

Zhong의 제안. 동기기의 전기·기계 방정식($\dot\theta$, 역기전력 $e = M_f i_f \omega \sin\theta$, 토크 $T_e$)을 전부 구현하고 PWM 전압으로 직접 출력. 전류 루프 없이도 동작하나, 전류 제한이 어려워 상용 제품에서는 전류 루프를 더한 변형을 쓴다.

## 4. Matching Control

물리적 유추: 동기기의 **회전자 각속도 ↔ 인버터의 DC링크 전압**.

$$\dot\theta = k_\theta\, v_{dc}$$

- DC링크 커패시터의 에너지 $\frac{1}{2}C v_{dc}^2$가 회전자 운동에너지 역할을 하여 "진짜" 에너지 기반 관성을 준다.
- DC 전압이 변동해야 하므로 DC측 전원(배터리 DC/DC 등)의 제어와 묶어 설계. 학술적으로 깔끔하나 상용화 사례는 제한적.

## 5. dVOC (dispatchable Virtual Oscillator Control)

비선형 진동자(Van der Pol/Andronov–Hopf 계열)가 정현파를 자발적으로 만들고, 전류 되먹임으로 다른 진동자와 동기화되는 성질을 이용. 디스패치 가능하게 확장한 것이 dVOC (Colombino, Groß, Dörfler 2019):

$$\dot{\mathbf v} = \omega_0 \mathbf J \mathbf v + \eta\,[\,\mathbf K(\mathbf v) - \mathbf R(\kappa)\, \mathbf i\,] + \eta\alpha\,(V^{*2} - \|\mathbf v\|^2)\mathbf v$$

- 평형점 근방에서는 Droop과 동일하게 수렴하지만, **대신호(큰 외란) 안정성**을 수학적으로 보장하며 동기화 속도가 매우 빠르다.
- 미국 NREL/UNIFI 컨소시엄에서 적극 연구·실증(하와이, 마이크로그리드). 상용 채택 초기 단계.

## 6. PSC (Power Synchronization Control)

Zhang & Harnefors(2010)가 VSC-HVDC 약계통 연계용으로 제안.

$$\dot\theta = \omega_0 + k_p (P^* - P)$$

- 사실상 LPF 없는 Droop. 전류 루프 대신 전압 직접 출력 + 고조파 억제 필터.
- 고장 시(과전류) PLL 기반 전류제어로 **모드 전환**. ABB(현 Hitachi Energy) HVDC Light에 적용된 것으로 알려진 초기 상용 GFM 계열.

## 7. 기타·보조 기법

- **Virtual impedance / Virtual admittance**: 모든 기법에 결합 가능. 전류 제한·디커플링·댐핑.
- **Enhanced/Generalized Droop, Washout filter droop**: 정상상태 주파수 편차 없이 동적 드룹 제공.
- **Grid-forming with PLL assistance**: 정상 시 GFM, 과도 시 PLL 보조. 상용 제품에서 흔함.
- **Multi-loop vs single-loop**: 전압 루프 유무에 따른 대역폭·안정성 트레이드오프.
- **Frequency-droop + inertia emulation on GFL** (합성관성)은 GFM이 **아님** — 측정 기반.

## 8. 기법 선택 가이드

| 상황 | 권장 |
|---|---|
| 계통코드가 관성상수 H를 명시 | VSM/VSG |
| 마이크로그리드 다수 병렬, 통신 없음 | Droop (+가상 임피던스) 또는 dVOC |
| 약계통 HVDC/STATCOM | PSC 계열, VSM |
| 매우 큰 외란·블랙스타트 반복 | dVOC, 가상 임피던스 기반 전류 제한 강화 |
| 상용 PCS 조달 | 제조사 구현(대개 Droop/VSM 변형) + 계통코드 시험 성적 확인 |

## 관련 문서

- [GFM 제어 구조](01-GFM-제어구조.md)
- [전류 제한과 고장 대응](03-전류제한-고장대응.md)
- [참고문헌](../08-부록/02-참고문헌.md) — Dörfler, Zhong, Harnefors, D'Arco 등 원논문
