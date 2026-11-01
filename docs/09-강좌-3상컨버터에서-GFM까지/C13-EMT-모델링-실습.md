---
title: C13. EMT 모델링 실습
aliases:
  - EMT 모델링 실습
  - C13
tags:
  - 강좌
  - EMT
  - 시뮬레이션
  - Python
lecture: C13
part: F
status: 초안
prerequisites:
  - "[[C02-공간벡터-좌표변환-pu]]"
  - "[[C04-변조-SPWM-SVPWM]]"
  - "[[C06-디지털-제어와-지연]]"
created: 2026-11-01
updated: 2026-11-01
---

# C13. EMT 모델링 실습

> [!abstract] 이 강의에서 답할 질문
> 이 강좌의 Python EMT 모델은 회로를 어떻게 푸는가? 평균값 모델과 스위칭 모델은 무엇이 다르고, 해석 간격은 어떻게 골라야 하는가? 결과를 믿으려면 무엇을 확인해야 하는가?

> [!info] 학습 목표
> - 공간벡터 상태방정식과 RK4 고정 스텝으로 회로가 풀리는 과정을 설명할 수 있다.
> - 평균값 모델과 스위칭 모델의 차이, 스위칭 시점 양자화, 기록 간격과 에일리어싱을 설명할 수 있다.
> - 해석 간격을 바꿔 수렴을 확인하고, 스텝에 민감한 지표와 둔감한 지표를 구분할 수 있다.
> - 자신만의 시나리오와 회귀 테스트를 만들 수 있다.

## 1. 핵심 개념

### 1.1 공간벡터 상태방정식

3상 순시값은 복소 αβ 벡터 하나로 다룬다(진폭 불변, $|v| = 1$ pu가 정격 상전압 진폭). → [[C02-공간벡터-좌표변환-pu]] 회로는 인덕터 전류와 커패시터 전압을 상태로 하는 미분방정식이다. pu에서 리액턴스 $X$ 의 인덕터는 $(X/\omega_b)\,di/dt = \Delta v$, 서셉턴스 $B$ 의 커패시터는 $(B/\omega_b)\,dv/dt = \Delta i$ 다.

$$
\begin{aligned}
\frac{L_f}{\omega_b}\frac{di_f}{dt} &= v_{conv} - R_f i_f - v_{term}, &
\frac{C_f}{\omega_b}\frac{dv_c}{dt} &= i_f - i_t, \\
\frac{L_t}{\omega_b}\frac{di_t}{dt} &= v_{term} - R_t i_t - v_{pcc}, &
\frac{X_{th}}{\omega_b}\frac{di_s}{dt} &= v_{pcc} - R_{th} i_s - e_g
\end{aligned}
$$

대수식 두 개가 이를 잇는다. 커패시터 단자 전압은 $v_{term} = v_c + R_d(i_f - i_t)$ 이고, PCC 전압은 $v_{pcc} = (i_t - i_s)/G$ 다. 여기서 $G$ 는 PCC 분로 0.03 pu + 국부 부하 + 고장 컨덕턴스다. 계통 차단기가 열리면 $i_s = 0$ 이 된다. 이 회로 상태 8개(복소 4개)에 PLL·VSM·전류 제어 적분기·측정 필터 등 제어 상태를 더해 상태 벡터는 25개다(`N_STATES`).

정지좌표 αβ에서 풀기 때문에 정상상태에서도 상태가 60 Hz로 회전한다. 대신 고조파·스위칭 리플·좌표 회전을 근사 없이 다룰 수 있다. 이것이 페이저(RMS) 모델과 다른 EMT의 성격이다.

### 1.2 RK4 고정 스텝과 안정 한계

적분은 고전 4차 룽게-쿠타(RK4)를 고정 간격 $\Delta t$ 로 쓴다.

$$
x_{n+1} = x_n + \frac{\Delta t}{6}\,(k_1 + 2k_2 + 2k_3 + k_4)
$$

고정 스텝을 쓰는 이유는 두 가지다. 디지털 제어의 샘플링 시점(10 kHz)을 정확히 스텝 경계에 맞출 수 있고, 스위칭 시점도 스텝 경계에서 처리할 수 있다. 대가로 **가장 빠른 모드**가 스텝 크기를 제한한다. 이 모델에서 가장 빠른 모드는 PCC 모선이다. 작은 분로 컨덕턴스 $G$ 에 두 인덕터($L_t$, $X_{th}$)가 물려 있어 시정수가 수 µs다.

$$
\lambda_{PCC} \approx \frac{\omega_b}{G}\left(\frac{1}{L_t} + \frac{1}{X_{th}}\right), \qquad
\Delta t \lesssim \frac{2.78}{\lambda_{PCC}}
$$

SCR 3, $G = 0.03$ pu이면 $\lambda \approx 1.6\times10^5$ s⁻¹, 한계는 약 17 µs다. 이 강의 실행에서 평균값 모델 정상상태 초기화는 15 µs에서 수렴했고, 18 µs와 20 µs에서는 GFL·GFM 모두 발산했다. **평균값 모델을 10 µs로 쓰는 이유**가 여기에 있다.

> [!note]- 유도: PCC 모드의 고유값과 RK4 한계
> $v_{pcc} = (i_t - i_s)/G$ 를 두 인덕터 식에 넣고 빠른 성분만 남기면
> $$\frac{d}{dt}(i_t - i_s) \approx -\omega_b\left(\frac{1}{L_t} + \frac{1}{X_{th}}\right)\frac{i_t - i_s}{G}$$
> 이다. 따라서 실수 고유값 $\lambda \approx (\omega_b/G)(1/L_t + 1/X_{th})$ 가 나온다. $\omega_b = 377$, $G = 0.03$, $L_t = 0.1$, $X_{th} = 1/3$ 이면 $\lambda \approx 12{,}570 \times 13 \approx 1.63\times10^5$ s⁻¹다. RK4의 안정 영역은 음의 실축에서 $|\lambda\Delta t| \le 2.785$ 이므로 $\Delta t \le 17$ µs다. SCR이 커지면($X_{th}$ 작아짐) 한계는 더 작아진다. SCR 5에서는 약 15 µs다. PCC 분로를 0으로 두면 모델은 변압기와 계통을 직렬 한 지로로 합쳐 이 모드를 없앤다.

### 1.3 평균값 모델 vs 스위칭 모델

| 항목 | 평균값 모델 `converter="average"` | 스위칭 모델 (기본) |
|---|---|---|
| 컨버터 전압 | 지령의 1차 지연: $\dot v_{conv} = (v_{cmd} - v_{conv})/T_d$, $T_d$ = 150 µs | 5 kHz 삼각파 PWM, min-max 영상분 주입(SVPWM 등가), 극전압 $\pm V_{dc}/2$ ($V_{dc}$ = 2.256 pu) |
| 제어기 입력 | 순시값 | 반송파 꼭짓점(10 kHz) 샘플-홀드 |
| 지연 | 1차 지연으로 근사 | 1샘플 계산 지연 + PWM 평균 지연 ≈ 1.5 샘플(자연 발생) |
| 리플 | 없음 | 있음 (Lf 0.2 pu에서 약 0.1 pu 피크-피크) |
| 권장 간격 | 10 µs | 2 µs (100 µs 샘플 주기를 나누어 떨어지는 값) |
| 속도 | 시뮬레이션 1 s에 약 3 s | 2 µs에서 시뮬레이션 1 s에 약 16 s |
| 용도 | 빠른 검토, 회귀 테스트, 실습 | 최종 결과, 리플·샘플링 효과 확인 |

스위칭 모델에서 스위치 상태는 **스텝 시작 시점**에 정해지고 그 스텝 동안 유지된다. 따라서 스위칭 시점은 $\Delta t$ 단위로 **양자화**된다. 2 µs는 반송파 주기 200 µs의 1 %다.

$$
\Delta v_{avg} \lesssim V_{dc}\,\frac{\Delta t}{T_c}
$$

이 식은 에지 하나가 늦을 때 반송파 한 주기 평균 전압이 얼마나 틀어지는지를 보여 준다. 2 µs이면 약 0.023 pu, 10 µs이면 약 0.11 pu다. 이 오차가 에지마다 다르게 나타나므로 결과에는 스텝 크기에 따라 달라지는 작은 "잡음"이 섞인다.

> [!note]- 유도: 스위칭 시점 양자화 오차
> 극전압은 $+V_{dc}/2$ 와 $-V_{dc}/2$ 사이를 오가므로 에지 하나의 전압 변화는 $V_{dc}$ 다. 이상적인 스위칭 시점이 스텝 경계 사이에 있으면 실제 전환은 다음 스텝 경계까지 최대 $\Delta t$ 늦어진다. 그만큼 볼트-초 오차 $V_{dc}\Delta t$ 가 생긴다. 반송파 주기 $T_c$ 로 평균하면 상전압 평균 오차는 최대 $V_{dc}\Delta t/T_c$ 다. $V_{dc} = 2.256$ pu, $T_c = 200$ µs이면 2 µs에서 0.023 pu, 10 µs에서 0.113 pu다. 상승·하강 에지 오차는 서로 상쇄되기도 하므로 이 값은 상한이다.

### 1.4 기록 간격 100 µs와 에일리어싱

결과는 100 µs마다 기록한다. 반송파는 $t = 0$ 에서 골이고 주기가 200 µs이므로, 기록 시점은 항상 **반송파 꼭짓점(골·마루)** 이다. 대칭 삼각파 PWM에서 꼭짓점의 전류는 리플의 가운데를 지난다. 그래서 기록값은 리플 평균값에 가깝다(그림 1 아래). 제어기의 샘플링도 같은 원리로 리플을 피한다. → [[C06-디지털-제어와-지연]]

그래도 완벽하지는 않다. 반송파 배수 주변의 측파대가 10 kHz 기록 간격에서 저주파로 접히고(에일리어싱), 평형 3상 전력에서는 주로 **360 Hz 배수**(기본파의 6배수)에 남는다(그림 2). 처음에는 리플이 큰 Lf 전류와 필터 단자 전압으로 전력을 측정했다. 이때 360·720·1080 Hz 잡음이 커서(표준편차 약 0.010 pu) 안정도 판정을 오염시켰고, 변압기 전류·PCC 전압 측정으로 바꾸자 약 0.004 pu로 줄었다. → [[C05-필터-변압기-측정점]], [[simulation/emt/README|EMT 시뮬레이션]] 1절

### 1.5 정상상태 웜스타트와 캐시

외란 시험은 정상상태에서 시작해야 한다. `steady_state(mode, p, dt)` 는 다음 순서로 동작한다.

- $P^*$ 를 0.3 s 동안 램프로 올리고 2.5 s까지 돌린다. 마지막 상태 벡터를 돌려준다.
- `(mode, 모든 Params 필드, t_init, dt, N_STATES)` 의 해시로 `simulation/emt/.cache/ss_*.pkl` 에 저장한다. 같은 조합이면 다시 계산하지 않는다.
- `simulate(..., x0=상태)` 는 위상각을 정리하고, 스위칭 모델이면 샘플-홀드 값과 전압 지령을 현재 상태로 맞춰 이어서 시작한다.

> [!warning] 캐시의 함정
> 해시에는 **모델 코드**가 들어가지 않는다. `gfm_gfl_emt.py` 의 식을 고쳤다면 `simulation/emt/.cache/` 를 지워야 한다. 그렇지 않으면 이전 모델의 정상상태에서 출발한다. 반대로 `Params` 필드를 하나라도 바꾸면 새 초기화(평균값 모델 약 8 s, 스위칭 2 µs 약 40 s)가 돈다.

### 1.6 수렴 확인: 지표가 스텝에 둔감한가

`convergence.py` 는 같은 시나리오를 10 / 5 / 2 / 1 µs로 돌려 핵심 지표를 표로 만든다(`results/convergence.md`). 지표는 위상 점프 10 ms 내 ΔP, 약계통 P 표준편차, 고장 중 최대 전류·평균 전압·순간 최저 전압이다.

교훈은 **지표 자체가 스텝에 민감할 수 있다**는 것이다. 프로젝트에서는 GFL 고장 중 순간 최저 PCC 전압이 해석 간격에 따라 0.14~0.22 pu로 흔들렸다. 그래서 고장 지표를 **구간 평균**으로 바꿨다. 순간 최저값은 고장 진입 직후의 아주 짧은 골 하나가 정한다. 그 골의 깊이는 스위칭 에지와 샘플 시점이 그 순간 어디에 떨어지느냐에 달려 있다. 구간 평균은 이런 국소 잡음을 평균해 지운다. 그림 3이 같은 현상을 보여 준다(이 강의용 짧은 실행).

평균값 모델에서는 10 µs와 5 µs의 고장 지표가 소수 셋째 자리까지 같았다(이 강의 실행). 스위칭 모델의 민감도가 **스위칭 시점 양자화와 샘플 타이밍**에서 온다는 증거다.

### 1.7 잡음에 강한 판정 기준

"안정한가"를 사람 눈 대신 코드로 판정하려면 스위칭 잡음과 진짜 진동을 구분해야 한다. `oscillation_check(t, P, a, b)` 는 외란 후 구간 $[a, b]$ 를 앞뒤 절반으로 나눠 두 가지를 **따로** 본다.

- **제어 상호작용 진동(5~300 Hz)**: 해닝 창 FFT의 대역 최대 진폭을 구한다. 이때 360 Hz 배수 ±6 Hz(스위칭 에일리어싱)는 뺀다. 뒤 절반이 0.005 pu 미만이거나 앞 절반의 70 % 미만이면 통과다.
- **저주파 스윙**: 20 ms 이동평균한 P의 표준편차를 구한다. 뒤 절반이 0.01 pu 미만이거나 앞 절반의 70 % 미만이면 통과다.

"작거나, 줄어들고 있으면" 통과라는 구조 덕분에 관성 모드처럼 느리게 감쇠하는 스윙을 불안정으로 오판하지 않는다. 주파수 판정도 같은 이유로 20 ms 이동평균한 값을 쓴다(표준 시험의 주파수 범위 판정).

### 1.8 회귀 테스트

`test_emt.py` 는 **물리적으로 반드시 성립해야 하는 성질**만 검사한다. 평균값 모델(10 µs) 5종과 스위칭 모델(2 µs) 1종이다.

- 정상상태 지령 추종.
- 정상상태 위상차가 $P = V^2/X\sin\delta$ 와 2° 이내로 일치.
- GFM 위상점프 전력은 즉시 나오고 GFL은 거의 없음.
- 단독운전 시 GFM 드룹 주파수가 이론값과 일치.
- 고장 중 GFM 전류 제한과 고장 후 동기 유지.
- 스위칭 모델의 정상상태 추종, 리플 크기(0.03~0.3 pu), 변조 한계 1.302 pu.

좋은 회귀 테스트는 정확한 숫자 대신 **이론과의 관계나 넉넉한 범위**를 검사한다. 그래야 튜닝을 조금 바꿔도 깨지지 않고, 모델이 물리를 어길 때만 깨진다.

## 2. 그림으로 보기

![[C13-스위칭-평균값-파형.png]]

*그림 1. 위: 계통 위상 −20° 점프 전후 GFM a상 전류. 스위칭 모델(2 µs)에는 5 kHz 리플이 실리고, 평균값 모델(10 µs)은 그 가운데를 지난다. 아래: 100 µs 기록점은 반송파 꼭짓점에 있어 리플의 가운데에 찍힌다.*

![[C13-스펙트럼-에일리어싱.png]]

*그림 2. 정상상태 유효전력의 스펙트럼. 스위칭 모델에는 360·720·1080 Hz 에일리어싱 성분이 보인다. `oscillation_check` 는 5~300 Hz 대역만 보고 360 Hz 배수 ±6 Hz를 뺀다. 평균값 모델은 이 잡음이 없다(표준편차 0.0003 vs 0.0040 pu, 이 강의 실행).*

![[C13-해석간격-지표민감도.png]]

*그림 3. GFL 3상 고장(계통 전압 0.3 pu, SCR 3, $P_0$ 0.8 pu) 중 PCC 전압, 스위칭 모델, 이 강의용 짧은 실행. 고장 진입 약 3 ms 뒤의 날카로운 골이 순간 최저값을 정하며, 그 깊이는 해석 간격에 따라 0.14~0.18 pu로 달라진다. 구간 평균은 0.71 pu로 거의 같다.*

## 3. Python 실습

모든 코드는 저장소 루트에서 실행한다. 평균값 모델은 경우당 수 초, 처음 쓰는 파라미터 조합은 정상상태 초기화로 약 8 s가 더 든다.

### 과제 1. 나만의 시나리오 만들기

`Scenario` 의 필드는 모두 시간 함수다(`grid_f`, `grid_phase`, `grid_v`, `scr`, `breaker_closed`, `p_ref`, `pcc_fault_g`). 외란을 조합해 보자.

```python
# 저장소 루트에서 실행: 나만의 시나리오 — 계통 주파수 −0.2 Hz 계단 + 0.3 s 뒤 유효전력 지령 0.5 → 0.8 pu
import sys; sys.path.insert(0, "simulation/emt")
import numpy as np
from gfm_gfl_emt import Params, Scenario, simulate, steady_state, oscillation_check

T, DT = 0.2, 10e-6
sc = Scenario(
    name="f-step+p-step", t_end=1.6,
    grid_f=lambda t: 1.0 - 0.2 / 60 if t >= T else 1.0,        # 계통 주파수 [pu]
    p_ref=lambda t: 0.8 if t >= T + 0.3 else 0.5,              # 유효전력 지령 [pu]
)
for mode in ("GFL", "GFM"):
    p = Params(converter="average", P_ref=0.5, scr=3.0, gfl_droop=True)   # GFL 도 드룹 2 % 를 켠다
    r = simulate(mode, p, sc, dt=DT, x0=steady_state(mode, p, dt=DT))
    t, P, f = (np.asarray(r[k]) for k in ("t", "P", "freq"))
    ok, info = oscillation_check(t, P, a=T + 0.4)                          # 지령 변경 0.1 s 뒤부터 판정
    print(f"{mode}: 주파수 계단 0.25 s 뒤 P {np.interp(T + 0.25, t, P):.3f} pu, "
          f"끝 P {P[t > 1.4].mean():.3f} pu, f {f[t > 1.4].mean():.2f} Hz, 안정 {ok}")
```

드룹 2 %에서 −0.2 Hz는 $\Delta P = (0.2/60)/0.02 \approx 0.167$ pu다. 최종 P가 0.8 + 0.167 pu 근처인지 확인하자. 계단 직후 0.25 s 시점에는 GFM(관성)과 GFL(측정 필터 2 Hz)의 응답 차이가 보인다.

### 과제 2. 해석 간격을 바꿔 지표 비교

```python
# 저장소 루트에서 실행: 해석 간격을 바꿔 같은 지표를 비교 (평균값 모델, 5 µs 는 초기화 포함 약 25초)
import sys; sys.path.insert(0, "simulation/emt")
import numpy as np
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

T = 0.2
sc = Scenario(t_end=0.6, grid_v=lambda t: 0.3 if T <= t < T + 0.15 else 1.0)
p = Params(converter="average", P_ref=0.8, scr=3.0)
for dt in (10e-6, 5e-6):              # 20e-6 은 초기화부터 발산한다 (1.2절)
    r = simulate("GFL", p, sc, dt=dt, x0=steady_state("GFL", p, dt=dt))
    t, V, I = (np.asarray(r[k]) for k in ("t", "V", "I"))
    m = (t >= T) & (t < T + 0.15)
    print(f"dt {dt*1e6:4.0f} µs: 고장 중 V 순간 최저 {V[m].min():.3f}, 구간 평균 {V[m].mean():.3f}, |i| 최대 {I[m].max():.3f} pu")
```

평균값 모델에서는 두 간격의 결과가 같다. 이제 `converter="average"` 를 지우고(스위칭 모델) `dt` 를 `(10e-6, 5e-6, 2e-6)` 로 바꿔 보자. 스위칭 모델은 초기화에 간격별로 수십 초가 걸린다. 순간 최저값과 구간 평균 중 어느 쪽이 흔들리는지 확인하자(그림 3). 스위칭 모델의 `dt` 는 100 µs를 나누어 떨어지는 값만 쓴다.

### 과제 3. 평균값 vs 스위칭 파형 (짧게)

```python
# 저장소 루트에서 실행: 평균값 vs 스위칭 파형 (스위칭 정상상태 초기화는 처음 한 번 약 40초, 이후 캐시)
import sys; sys.path.insert(0, "simulation/emt")
import numpy as np
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

sc = Scenario(t_end=0.05)                                   # 외란 없이 50 ms
win = (0.02, 0.04)                                          # 순시 파형을 저장할 구간 [s]
for conv, dt in (("average", 10e-6), ("switching", 2e-6)):
    p = Params(converter=conv, P_ref=0.5, scr=3.0)
    r = simulate("GFM", p, sc, dt=dt, x0=steady_state("GFM", p, dt=dt), hires=win)
    th, ia = np.asarray(r["hires"]["t"]), np.asarray(r["hires"]["ia"])
    A = np.column_stack([np.cos(2 * np.pi * 60 * th), np.sin(2 * np.pi * 60 * th)])
    c, *_ = np.linalg.lstsq(A, ia, rcond=None)               # 60 Hz 기본파 맞춤
    ripple = np.ptp(ia - A @ c)
    P = np.asarray(r["P"])
    print(f"{conv:9}: 기본파 진폭 {np.hypot(*c):.3f} pu, 리플(피크-피크) {ripple:.3f} pu, 기록 P 표준편차 {P.std():.4f} pu")
```

`hires=(t0, t1)` 를 주면 그 구간의 순시 상전류·상전압을 해석 간격마다 `r["hires"]` 에 저장한다. 이 강의 실행에서 스위칭 모델의 리플은 약 0.11 pu 피크-피크였고, 평균값 모델은 0이었다.

### 과제 4. 회귀 테스트 작성

```python
# 저장소 루트에서 실행 (pytest 로 돌려도 된다): 내가 만든 회귀 테스트
import sys; sys.path.insert(0, "simulation/emt")
import numpy as np
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

T, DT = 0.2, 10e-6

def test_fault_current_follows_rating():
    """PCC 지락 중 GFM 전류의 구간 평균이 I_max 를 따른다 (순간 피크가 아니라 평균으로 판정)."""
    for imax in (1.2, 2.0):
        p = Params(converter="average", P_ref=0.8, scr=3.0, I_max=imax)
        sc = Scenario(t_end=0.5, pcc_fault_g=lambda t: 20.0 if T <= t < T + 0.2 else 0.0)
        r = simulate("GFM", p, sc, dt=DT, x0=steady_state("GFM", p, dt=DT))
        t, I = np.asarray(r["t"]) - T, np.asarray(r["I"])
        m = (t > 0.02) & (t < 0.2)                       # 진입 과도 20 ms 제외
        assert abs(I[m].mean() - imax) < 0.03 * imax, (imax, I[m].mean())

if __name__ == "__main__":
    test_fault_current_follows_rating()
    print("PASS")
```

> [!tip] 해볼 것
> - 과제 4에 "GFL은 계통 분리 후 주파수가 1 Hz 넘게 벗어난다" 같은 **실패해야 하는 성질**도 테스트로 넣어 보자. 모델이 고쳐지거나 망가지면 알려 준다.
> - 과제 1의 시나리오에 `scr=lambda t: 3.0 if t < 0.5 else 1.5` 를 더해 약계통에서 같은 외란을 주고, `oscillation_check` 의 `info` 에서 `osc_amp`, `osc_f`, `swing_std` 를 읽어 보자.
> - `Params(G_bus=0.1)` 로 PCC 분로를 키우면 1.2절의 안정 한계가 어떻게 바뀌는지 식으로 먼저 계산하고(약 57 µs), 20 µs에서 초기화가 되는지 확인하자. 분로가 소비하는 전력도 바뀌므로 지표를 기본 설정과 직접 비교하지는 말자.

## 4. 흔한 오해

> [!warning] 오해: 해석 간격을 줄이면 무조건 더 정확하다
> 간격을 줄여도 **지표**가 스텝에 민감하면 숫자는 계속 흔들린다(순간 최저값). 먼저 지표를 구간 평균처럼 둔감한 형태로 정하고, 그다음 간격을 바꿔 수렴을 확인한다. 1 µs 결과는 2 µs보다 2배 느리지만, 지표가 수렴했다면 얻는 것이 없다.

> [!warning] 오해: 평균값 모델은 스위칭 모델의 "덜 정확한 버전"일 뿐이다
> 평균값 모델은 리플과 샘플링 잡음이 없어 제어 거동을 깨끗하게 보여 주고, 수십 배 빠르다. 수렴도 쉽다(10 µs와 5 µs가 같음). 다만 스위칭 리플, 샘플-홀드, 에일리어싱처럼 **이산적인 효과**는 볼 수 없다. 측정점 설계나 판정 기준의 잡음 내성은 스위칭 모델로 확인해야 한다.

> [!warning] 오해: 기록값에 리플이 안 보이면 리플이 없는 것이다
> 100 µs 기록은 반송파 꼭짓점과 동기라서 리플의 가운데만 찍는다(그림 1). 리플을 보려면 `hires` 로 해석 간격마다 저장해야 한다. 반대로 꼭짓점 동기 덕분에 기록값은 평균값에 가깝다. 그래도 남는 에일리어싱이 360 Hz 배수에 나타난다(그림 2).

## 5. 확인 문제

1. 이 모델의 평균값 모델을 20 µs로 돌리면 초기화부터 발산한다. 어느 모드 때문이며, 대략적인 한계는 얼마인가?

> [!success]- 답
> PCC 모선 모드다. 작은 분로 컨덕턴스 $G = 0.03$ pu에 변압기와 계통 인덕터가 물려 고유값 $\lambda \approx (\omega_b/G)(1/L_t + 1/X_{th}) \approx 1.6\times10^5$ s⁻¹(SCR 3)가 된다. RK4의 실축 안정 한계 $|\lambda\Delta t| \le 2.78$ 에서 $\Delta t \lesssim 17$ µs다. 이 강의 실행에서는 15 µs 수렴, 18 µs 발산이었다.

2. 스위칭 모델에서 해석 간격 2 µs가 반송파 주기의 몇 %이며, 에지 하나의 양자화가 만드는 반송파 주기 평균 전압 오차의 상한은 몇 pu인가?

> [!success]- 답
> 반송파 주기 200 µs의 1 %다. 상한은 $V_{dc}\Delta t/T_c = 2.256 \times 0.01 \approx 0.023$ pu다. 10 µs이면 약 0.11 pu로 커진다. 이것이 스위칭 모델 지표가 해석 간격에 따라 흔들리는 주요 원인이다.

3. `oscillation_check` 가 5~300 Hz 대역에서 360 Hz 배수를 빼고, 저주파 스윙은 20 ms 이동평균으로 따로 보는 이유는?

> [!success]- 답
> 360 Hz 배수는 스위칭 측파대가 100 µs 기록에서 접힌 에일리어싱 잡음이다. 제어 불안정이 아니므로 판정에서 빼야 한다. 5~300 Hz는 PLL·전류 루프·LCL이 만드는 제어 상호작용 진동 대역이다. VSM 관성 모드 같은 1 Hz 안팎의 스윙은 크기와 시간 규모가 전혀 달라 한 지표로 묶으면 서로를 가린다. 그래서 20 ms 이동평균으로 고주파를 지운 뒤 표준편차로 따로 본다. 두 지표 모두 "작거나 줄어들고 있으면" 통과라서 느리게 감쇠하는 스윙을 불안정으로 오판하지 않는다.

## 연결

- 이전: [[C12-표준-시험으로-비교]] · 처음으로: [[00-강좌-목차]]
- 더 보기: [[simulation/emt/README|EMT 시뮬레이션]] · [[01-시험-검증-방법]] · [[C06-디지털-제어와-지연]] · [[C05-필터-변압기-측정점]] · [[C04-변조-SPWM-SVPWM]]
