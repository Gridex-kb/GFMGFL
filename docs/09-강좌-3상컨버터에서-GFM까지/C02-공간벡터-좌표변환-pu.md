---
title: C02. 공간벡터, 좌표변환, pu
aliases:
  - 공간벡터와 좌표변환
  - Clarke Park 변환
  - dq 변환
  - pu 기준값
tags:
  - 강좌
  - 공간벡터
  - 좌표변환
  - dq
  - pu
lecture: C02
part: A
status: 초안
prerequisites:
  - "[[C00-부록-선수지식]]"
  - "[[C01-3상-계통의-표현]]"
created: 2026-11-01
updated: 2026-11-01
---

# C02. 공간벡터, 좌표변환, pu

> [!abstract] 이 강의에서 답할 질문
> 3상 신호 세 개를 복소수 하나로 쓰면 무엇이 쉬워지는가? 60 Hz로 도는 좌표에서 보면 왜 정현파가 직류가 되고, 전력은 어떻게 한 줄로 계산되는가?

> [!info] 학습 목표
> - 진폭 불변 Clarke 변환으로 3상 순시값을 공간벡터로 바꾸고, 영상분이 빠지는 이유를 설명할 수 있다.
> - Park(dq) 변환에서 정현파가 직류가 되는 원리를 설명할 수 있다.
> - $P = \mathrm{Re}(v\,i^*)$, $Q = \mathrm{Im}(v\,i^*)$ 와 d축 전압 정렬 시 $P = v_d i_d$, $Q = -v_d i_q$ 를 계산할 수 있다.
> - 강좌의 pu 기준값을 정의하고, 물리 단위 식의 $\tfrac32$ 가 왜 사라지는지 설명할 수 있다.

## 1. 핵심 개념

### 1.1 공간벡터

**공간벡터(space vector)** 는 3상 순시값 세 개를 복소수 하나로 묶은 것이다. 이 강좌는 **진폭 불변(amplitude-invariant)** 형태를 쓴다.

$$
\vec x = \frac23\left(x_a + a\,x_b + a^2 x_c\right) = x_\alpha + j\,x_\beta, \qquad a = e^{j2\pi/3}
$$

- 각 상의 순시값을 그 상의 축 방향(0°, 120°, 240°)을 향한 벡터로 놓고 더한 뒤 $\tfrac23$ 을 곱한 것이다.
- 실수부와 허수부를 **αβ 성분**이라 하고, 이 변환을 **Clarke 변환**이라 부른다.
- 평형 정상분 정현파는 $\vec v = V e^{j(\omega t + \varphi)}$ 가 된다. 반지름 $V$ 의 원을 $\omega$ 로 반시계 방향으로 돈다. 역상분은 시계 방향으로 돈다.
- **진폭 불변**이란 $|\vec v|$ 가 상전압 진폭과 같다는 뜻이다. 그래서 $|\vec v|$ = 1 pu는 정격 상전압 진폭이다.

실수 행렬로 쓰면 다음과 같다.

$$
x_\alpha = \frac23\left(x_a - \frac{x_b}{2} - \frac{x_c}{2}\right), \qquad x_\beta = \frac{1}{\sqrt3}\left(x_b - x_c\right)
$$

역변환은 회전 후 실수부를 취한다: $x_a = \mathrm{Re}(\vec x)$, $x_b = \mathrm{Re}(\vec x\,e^{-j2\pi/3})$, $x_c = \mathrm{Re}(\vec x\,e^{j2\pi/3})$ (영상분은 따로 더한다). 시뮬레이터 `simulation/emt/gfm_gfl_emt.py` 는 상태를 이 복소 αβ 벡터로 들고 있다가 기록할 때 이 식으로 `va, vb, vc` 를 만든다.

> [!important] 페이저와 무엇이 다른가
> 페이저는 **정상상태 정현파**에만 정의된다. 공간벡터는 **순시값**에 정의되므로 과도 상태, 고조파, 불평형, 스위칭 파형에도 그대로 쓸 수 있다. EMT 모델과 제어기가 공간벡터를 쓰는 이유다.

> [!note]- 유도: 평형 정현파의 공간벡터는 $Ve^{j\omega t}$
> $\cos\theta = \tfrac12(e^{j\theta} + e^{-j\theta})$ 를 쓴다. $V=1$, $\varphi=0$ 으로 두면
> $$x_a = \tfrac12(e^{j\omega t} + e^{-j\omega t}),\quad a\,x_b = \tfrac12(e^{j\omega t} + a^2e^{-j\omega t}),\quad a^2x_c = \tfrac12(e^{j\omega t} + a\,e^{-j\omega t})$$
> ($x_b = \cos(\omega t - 120°) = \tfrac12(a^{-1}e^{j\omega t} + a\,e^{-j\omega t})$, $a^3 = 1$ 을 썼다.) 셋을 더하면
> $$\tfrac12\left[3e^{j\omega t} + (1 + a + a^2)e^{-j\omega t}\right] = \tfrac32 e^{j\omega t}$$
> $\tfrac23$ 을 곱하면 $e^{j\omega t}$. 역방향으로 도는 성분은 $1 + a + a^2 = 0$ 때문에 사라지고, 진폭은 그대로 1이다. 앞의 $\tfrac23$ 이 "진폭 불변"을 만드는 계수다.

### 1.2 영상분

$$
x_0 = \frac{x_a + x_b + x_c}{3}
$$

**영상분(zero sequence)** 은 세 상에 똑같이 더해진 성분이다. 세 상에 같은 값 $x_0$ 를 더하면 공간벡터에는 $\tfrac23 x_0(1 + a + a^2) = 0$ 이 더해진다. 즉 **공간벡터는 영상분을 보지 못한다**.

- 중성선이 없는 3선식 컨버터에서는 영상분 전류가 흐를 길이 없다. 영상분 전압은 선간전압에도, 상전류에도 영향을 주지 않는다.
- 이 성질 덕분에 SVPWM(min-max 영상분 주입)은 변조파에 영상분을 더해 최대 상전압 진폭을 SPWM의 $V_{dc}/2$ = 1.128 pu에서 $V_{dc}/\sqrt3$ = 1.302 pu로 넓힌다([[C04-변조-SPWM-SVPWM]]).
- 4선식 계통이나 지락 고장 해석에서는 영상분을 따로 다뤄야 한다. 이 강좌의 범위 밖이다.

### 1.3 Park(dq) 변환

**Park 변환**은 같은 공간벡터를 각도 $\theta$ 로 도는 좌표에서 본다.

$$
\vec x_{dq} = x_d + j\,x_q = \vec x\, e^{-j\theta}
$$

$\theta$ 가 신호와 같은 속도로 돌면($\theta = \omega t$) 회전이 상쇄되어 **정현파가 직류가 된다**.

$$
\vec v = V e^{j(\omega t + \varphi)},\ \ \theta = \omega t \quad\Rightarrow\quad \vec v_{dq} = V e^{j\varphi}
$$

정상상태에서 dq 값은 페이저와 같다. 진폭은 $|\vec v_{dq}|$, 위상은 $\angle\vec v_{dq}$ 로 바로 읽힌다. 실수 행렬로는 $v_d = v_\alpha\cos\theta + v_\beta\sin\theta$, $v_q = -v_\alpha\sin\theta + v_\beta\cos\theta$ 이며, [[02-인버터-기본구조-제어계층]]의 식과 같다.

dq 좌표를 쓰는 이유는 세 가지다.

1. **직류는 PI로 오차 없이 따라간다**([[C00-부록-선수지식]]). 전류 제어가 dq에서 이뤄지는 이유다([[C07-전류-제어]]).
2. **크기와 위상이 분리된다.** 전압 크기 제어와 위상(전력) 제어를 나눠 설계할 수 있다.
3. **주파수 차이가 회전으로 보인다.** $\theta$ 가 60 Hz로 도는데 계통이 60.5 Hz면 $\vec v_{dq}$ 가 0.5 Hz로 천천히 돈다. PLL은 이 회전을 없애도록 $\theta$ 의 속도를 고친다($v_q \to 0$, [[C08-GFL-PLL로-따라가기]]).

회전 좌표에서는 미분에 회전 항이 붙는다. pu 인덕터 식은 다음이 된다($\omega_{pu} = \dot\theta/\omega_b$).

$$
\frac{L}{\omega_b}\frac{d\vec i_{dq}}{dt} = \vec v_{dq} - R\,\vec i_{dq} - j\,\omega_{pu} L\,\vec i_{dq}
$$

마지막 항이 d축과 q축을 엮는 **교차결합(cross-coupling)** 이다. 전류 제어의 디커플링 항이 이것을 지운다([[C07-전류-제어]]).

> [!note]- 유도: 회전 좌표의 인덕터 식
> $\vec i = \vec i_{dq}e^{j\theta}$ 를 정지 좌표 식 $(L/\omega_b)\,d\vec i/dt = \vec v - R\vec i$ 에 넣는다. 곱의 미분으로
> $$\frac{d\vec i}{dt} = \left(\frac{d\vec i_{dq}}{dt} + j\dot\theta\,\vec i_{dq}\right)e^{j\theta}$$
> 양변에서 $e^{j\theta}$ 를 지우고 $\dot\theta = \omega_{pu}\omega_b$ 를 쓰면
> $$\frac{L}{\omega_b}\frac{d\vec i_{dq}}{dt} + j\,\omega_{pu}L\,\vec i_{dq} = \vec v_{dq} - R\,\vec i_{dq}$$
> 정상상태($d/dt = 0$)에서는 $\vec v_{dq} = (R + j\omega_{pu}L)\,\vec i_{dq}$, 즉 페이저 임피던스 식으로 돌아온다.

### 1.4 공간벡터로 쓴 전력

$$
P = \mathrm{Re}\left(\vec v\,\vec i^{\,*}\right), \qquad Q = \mathrm{Im}\left(\vec v\,\vec i^{\,*}\right) \quad [\text{pu}]
$$

- 순시값에도 성립한다. 영상분 전류가 없으면 $\mathrm{Re}(\vec v\,\vec i^{\,*}) = \tfrac23(v_a i_a + v_b i_b + v_c i_c)$ 로, [[C01-3상-계통의-표현]]의 3상 순시전력과 같다. $\mathrm{Im}$ 쪽은 C01의 순시 무효전력 $\tfrac23 q$ 와 같다.
- dq에서도 같은 식이다. $\vec v\,\vec i^{\,*} = \vec v_{dq}e^{j\theta}\,\vec i_{dq}^{\,*}e^{-j\theta} = \vec v_{dq}\,\vec i_{dq}^{\,*}$ 이므로

$$
P = v_d i_d + v_q i_q, \qquad Q = v_q i_d - v_d i_q
$$

**d축을 전압에 정렬**하면($v_q = 0$) 식이 갈라진다.

$$
P = v_d\,i_d, \qquad Q = -v_d\,i_q
$$

$i_d$ 로 유효전력을, $i_q$ 로 무효전력을 따로 제어할 수 있다. 무효전력을 **공급**($Q > 0$)하려면 $i_q < 0$ 이어야 한다. 전류가 전압보다 뒤지는 방향이다.

> [!caution] 문헌마다 관례가 다르다
> q축을 전압에 정렬하거나, Park 변환을 sin 기준으로 정의하는 문헌도 있다. 그러면 $Q = +v_d i_q$ 처럼 부호가 바뀐다. 다른 자료를 읽을 때는 정렬 축과 Q 부호 관례부터 확인한다.

> [!note]- 유도: $\mathrm{Re}(\vec v\,\vec i^{\,*}) = \tfrac23\sum v_k i_k$
> $\vec v = \tfrac23\sum_k v_k a^k$, $\vec i^{\,*} = \tfrac23\sum_m i_m a^{-m}$ ($k, m$ = 0, 1, 2) 이므로
> $$\mathrm{Re}(\vec v\,\vec i^{\,*}) = \frac49\sum_k\sum_m v_k i_m\cos\big(120°(k-m)\big)$$
> $k = m$ 이면 $\cos 0 = 1$, $k \ne m$ 이면 $\cos(\pm120°) = -\tfrac12$ 다. $\sum_{k\ne m}v_k i_m = (\sum v)(\sum i) - \sum v_k i_k$ 를 쓰면
> $$\mathrm{Re}(\vec v\,\vec i^{\,*}) = \frac49\left[\frac32\sum_k v_k i_k - \frac12\Big(\sum v\Big)\Big(\sum i\Big)\right] = \frac23\sum_k v_k i_k - 2\,v_0 i_0$$
> 3선식에서는 $i_0 = 0$ 이므로 $\tfrac23\sum v_k i_k$ 와 정확히 같다. 영상분 전압 $v_0$ 가 있어도 전력에 기여하지 않는다.

### 1.5 pu 기준값

| 기준 | 정의 |
|---|---|
| 전력 $S_b$ | 인버터 정격 피상전력 = 1 pu |
| 전압 $V_b$ | 정격 **상전압 진폭** = 1 pu |
| 전류 $I_b$ | $S_b = \tfrac32 V_b I_b$ 를 만족하는 값 = 정격 상전류 진폭 |
| 임피던스 $Z_b$ | $V_b / I_b$ |
| 각주파수 $\omega_b$ | $2\pi\cdot 60$ rad/s (한국 60 Hz) |
| 인덕턴스, 커패시턴스 | $L_b = Z_b/\omega_b$, $C_b = 1/(Z_b\,\omega_b)$ |
| 시간 | 초 그대로 |

- **$\tfrac32$ 는 어디로 갔나.** 진폭 불변 변환에서 물리 전력은 $\tfrac32\,\mathrm{Re}(\vec v\,\vec i^{\,*})$ 다. 기준 전력을 $S_b = \tfrac32 V_b I_b$ 로 잡으면 pu 식에서는 이 계수가 사라진다. [[02-인버터-기본구조-제어계층]]의 $P = \tfrac32 v_d i_d$ 는 물리 단위 식이고, pu로는 $P = v_d i_d$ 다. 둘 다 맞다.
- **실효값 기준과 같은 숫자.** 실효값 기준을 쓰면 $S_b = 3V_{b,rms}I_{b,rms}$ 인데, $V_{b,rms} = V_b/\sqrt2$, $I_{b,rms} = I_b/\sqrt2$ 이므로 같은 $S_b$, 같은 $Z_b$ 다. 어느 쪽으로 정의해도 pu 값은 같다.
- **DC 링크도 같은 $V_b$ 로 나눈다.** $V_{dc}$ = 2.256 pu 이면 SPWM 최대 상전압 진폭은 $V_{dc}/2$ = 1.128 pu, SVPWM은 $V_{dc}/\sqrt3$ = 1.302 pu다. 1 pu를 넘는 0.3 pu가 무효전력 공급, 필터 전압 강하, 과도 응답에 쓸 수 있는 여유다([[C04-변조-SPWM-SVPWM]]).
- **설비 크기와 무관하다.** 강좌 기준 설비($L_f$ 0.2 pu, $C_f$ 0.05 pu, 변압기 0.1 pu, 전류 한계 1.2 pu)는 정격 용량을 정하지 않았다. 이 pu 값이 맞는 설비라면 크기와 관계없이 같은 거동을 보인다.

### 1.6 dq 정렬 관례와 GFL·GFM

dq 변환 자체는 GFL과 GFM이 똑같이 쓴다. 다른 것은 **$\theta$ 를 어디서 얻느냐** 하나다.

- **GFL**: $\theta$ 는 PLL이 측정 전압에서 추정한다. d축이 PCC 전압에 정렬되어 $v_q \approx 0$ 이고, $P = v_d i_d$, $Q = -v_d i_q$ 를 그대로 쓴다([[01-GFL-제어구조]]).
- **GFM**: $\theta$ 는 제어기가 스윙 방정식 등을 적분해 스스로 만든다([[01-GFM-제어구조]]). 측정한 PCC 전압이 d축에 정확히 놓인다는 보장이 없으므로 $P = v_d i_d + v_q i_q$ 의 일반식을 쓴다.

이 갈림길은 [[C08-GFL-PLL로-따라가기]]와 [[C09-GFM-위상을-만들기]]에서 본격적으로 다룬다.

## 2. 그림으로 보기

![[C02-공간벡터-회전.png]]

*세 순간의 αβ 평면. 상 순시값은 계속 바뀌지만 공간벡터의 길이는 1로 일정하고, 함께 도는 d축 위에 머문다. 그래서 $v_d$ = 1, $v_q$ = 0 이 유지된다.*

![[C02-abc-ab-dq.png]]

*같은 신호를 세 좌표로 본 것. 25 ms에 진폭 1 → 0.7, 50 ms에 위상 +30°. abc와 αβ에서는 정현파지만, dq(θ = ωt)에서는 계단 모양의 직류가 되어 진폭과 위상 변화가 바로 읽힌다.*

그림 재생성: `python docs/_assets/강좌/scripts/C02_figs.py`

## 3. Python 실습

### 3.1 Clarke, Park, 전력을 numpy로

```python
# 저장소 루트에서 실행 (numpy만 사용)
import numpy as np

a = np.exp(2j * np.pi / 3)

def clarke(xa, xb, xc):
    """진폭 불변 Clarke: abc → 복소 공간벡터 x = xα + j·xβ, 그리고 영상분 x0."""
    return (2 / 3) * (xa + a * xb + a**2 * xc), (xa + xb + xc) / 3

def park(x_ab, theta):
    """Park: 정지 αβ → θ로 도는 dq. x_dq = x_αβ · e^{-jθ}."""
    return x_ab * np.exp(-1j * theta)

w = 2 * np.pi * 60
t = np.linspace(0, 1 / 60, 400, endpoint=False)
sh = np.array([0, -2 * np.pi / 3, 2 * np.pi / 3])[:, None]
V, I = 1.0, 0.8                             # 진폭 [pu]. 전류가 30° 앞섬 (진상)
v_abc = V * np.cos(w * t + sh) + 0.2        # 세 상에 같은 0.2 pu를 더함 (영상분)
i_abc = I * np.cos(w * t + sh + np.radians(30))

v, v0 = clarke(*v_abc)
i, _ = clarke(*i_abc)
print("|v| 범위:", abs(v).min().round(4), "~", abs(v).max().round(4), " 영상분 v0 =", v0.mean().round(3))

# 1) θ = ωt 로 돌리면 직류. 임의의 고정 오프셋 θ0를 더해도 직류(값만 바뀜)
for th0 in (0.0, np.radians(40)):
    vdq = park(v, w * t + th0)
    print(f"θ0 = {np.degrees(th0):4.0f}°: v_d = {vdq.real.mean():.3f}, v_q = {vdq.imag.mean():.3f}, 맥동 {np.ptp(vdq.real):.1e}")

# 2) 전력: Re(v·i*) 는 (2/3)·Σ v·i 와 같다 (전류 합이 0이라 영상분 전압은 전력에 기여하지 않음)
S = v * np.conj(i)
p3 = (v_abc * i_abc).sum(axis=0)
print(f"P = Re(v·i*) = {S.real.mean():.4f},  (2/3)Σv·i = {(2/3*p3).mean():.4f}")
print(f"Q = Im(v·i*) = {S.imag.mean():.4f}  (진상 전류 → Q < 0: 무효전력 흡수)")

# 3) d축을 전압에 정렬 (θ = ∠v): v_q = 0, P = v_d·i_d, Q = −v_d·i_q
th = np.angle(v)
vdq, idq = park(v, th), park(i, th)
print(f"정렬 후 v_q = {abs(vdq.imag).max():.1e},  v_d·i_d = {(vdq.real*idq.real).mean():.4f},"
      f"  −v_d·i_q = {(-vdq.real*idq.imag).mean():.4f}")
```

실행 결과:

```text
|v| 범위: 1.0 ~ 1.0  영상분 v0 = 0.2
θ0 =    0°: v_d = 1.000, v_q = -0.000, 맥동 7.8e-16
θ0 =   40°: v_d = 0.766, v_q = -0.643, 맥동 1.0e-15
P = Re(v·i*) = 0.6928,  (2/3)Σv·i = 0.6928
Q = Im(v·i*) = -0.4000  (진상 전류 → Q < 0: 무효전력 흡수)
정렬 후 v_q = 3.0e-16,  v_d·i_d = 0.6928,  −v_d·i_q = -0.4000
```

0.2 pu 영상분을 더했지만 $|\vec v|$ 는 1 그대로다. 기준각을 40° 틀어도 dq 값은 여전히 직류이고 값만 회전한다. **어느 θ로 보든 전력은 같다.** 정렬은 식을 단순하게 만들 뿐이다.

### 3.2 시뮬레이터 기록값을 공간벡터로

```python
# 저장소 루트에서 실행 (평균값 모델, 첫 실행 약 10 s, 이후 캐시 사용)
import sys; sys.path.insert(0, "simulation/emt")
import numpy as np
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

p = Params(converter="average")
x0 = steady_state("GFL", p, dt=10e-6)
r = simulate("GFL", p, Scenario(t_end=0.05), dt=10e-6, x0=x0)
va, vb, vc, V = (np.asarray(r[k]) for k in ("va", "vb", "vc", "V"))

a = np.exp(2j * np.pi / 3)
v = (2 / 3) * (va + a * vb + a**2 * vc)          # 기록된 상전압 → 공간벡터
print("max | |v| - V | =", np.max(np.abs(np.abs(v) - V)))   # 모델의 V는 |v_pcc|

t = np.asarray(r["t"])
th = 2 * np.pi * 60 * t                          # 60 Hz로 도는 임의의 기준각
vdq = v * np.exp(-1j * th)
print(f"v_d = {vdq.real.mean():.4f} ± {vdq.real.std():.1e},  v_q = {vdq.imag.mean():.4f} ± {vdq.imag.std():.1e}")
print(f"PCC 전압 위상 (기준각 대비) = {np.degrees(np.angle(vdq.mean())):.2f}°")
```

실행 결과:

```text
max | |v| - V | = 4.440892098500626e-16
v_d = 0.9877 ± 1.4e-12,  v_q = 0.1562 ± 1.6e-12
PCC 전압 위상 (기준각 대비) = 8.98°
```

기록된 상전압으로 만든 공간벡터의 크기가 모델의 `V`(= $|\vec v_{pcc}|$)와 수치 오차 범위에서 같다. 60 Hz로 도는 기준각으로 보면 $v_d$, $v_q$ 는 상수다. 위상값(8.98°) 자체는 기준각을 어디서 시작했느냐에 따라 달라지는 임의의 값이고, **일정하다는 것**이 핵심이다.

> [!tip] 해볼 것
> - 3.1에서 기준각 주파수를 59 Hz로 바꾼다(`w * t` 대신 `2*np.pi*59*t`). $v_d$, $v_q$ 가 1 Hz로 회전하는 것을 확인한다. PLL이 없애려는 것이 이 회전이다.
> - 3.1에서 b상과 c상을 바꿔 역상분을 만든다. 공간벡터가 시계 방향으로 돌고, 60 Hz 정상분 dq 좌표에서는 120 Hz 진동으로 보인다.
> - 3.2에서 `np.angle(v)` 를 θ로 써서 d축을 PCC 전압에 정렬하고, 기록값 `ia, ib, ic` 로 $v_d i_d$ 와 $-v_d i_q$ 를 계산해 본다. 기록 전류는 컨버터측 전류라 모델의 `P`, `Q` 와 조금 다르다([[C01-3상-계통의-표현]] 3.2절).

## 4. 흔한 오해

> [!warning] 오해: dq 변환은 GFM/GFL 전용 기법이다
> dq 변환은 3상 제어 전반의 공통 도구다. 동기기 해석(Park 변환의 기원), 전동기 벡터 제어, STATCOM, 능동 필터가 모두 같은 변환을 쓴다. GFL과 GFM은 같은 dq 전류 제어기를 공유하고, **기준각 $\theta$ 를 측정하느냐(PLL) 만드느냐(스윙 방정식)** 만 다르다.

> [!warning] 오해: 공간벡터는 페이저의 다른 이름이다
> 페이저는 정상상태 정현파에만 정의된다. 공간벡터는 매 순간의 3상 값에서 정의되므로 과도와 고조파를 담는다. 정상상태에서 $\theta = \omega t$ 인 dq 값이 페이저와 일치할 뿐이다.

> [!warning] 오해: $P = \tfrac32 v_d i_d$ 가 맞고 $P = v_d i_d$ 는 틀렸다
> 앞은 진폭 불변 변환의 물리 단위 식, 뒤는 $S_b = \tfrac32 V_b I_b$ 로 정한 pu 식이다. 단위계만 다르다. 한 계산 안에서 섞지 않으면 된다.

## 5. 확인 문제

1. 세 상 순시값이 $(v_a, v_b, v_c) = (1.3,\,-0.2,\,-0.2)$ pu 일 때 공간벡터와 영상분은?

> [!success]- 답
> 영상분 $v_0 = (1.3 - 0.2 - 0.2)/3 = 0.3$ pu. 이를 빼면 $(1, -0.5, -0.5)$ 이고, $\vec v = \tfrac23\big(1 - 0.5(a + a^2)\big) = \tfrac23(1 + 0.5) = 1 + j0$ pu. 영상분은 공간벡터에 나타나지 않는다.

2. d축을 PCC 전압에 정렬했더니 $v_d$ = 1.0, $i_d$ = 0.6, $i_q$ = −0.3 pu 였다. $P$, $Q$, 전류 크기는? 무효전력은 공급인가 흡수인가?

> [!success]- 답
> $P = v_d i_d = 0.6$ pu, $Q = -v_d i_q = 0.3$ pu(공급). $|i| = \sqrt{0.6^2 + 0.3^2} \approx 0.671$ pu 이고, 전압이 1 pu이므로 $S$ 도 0.671 pu다.

3. dq 기준각을 60 Hz로 돌리는데 실제 계통 주파수가 60.5 Hz다. $\vec v_{dq}$ 는 어떻게 보이는가?

> [!success]- 답
> 크기는 일정하고 0.5 Hz로 반시계 방향으로 천천히 회전한다. 즉 $v_d$, $v_q$ 가 0.5 Hz 정현파가 된다. PLL은 $v_q$ 를 0으로 만들도록 기준각의 속도를 60.5 Hz로 맞춰 이 회전을 없앤다.

## 연결

- 이전: [[C01-3상-계통의-표현]] · 다음: [[C03-2레벨-VSC]]
- 더 보기: [[02-인버터-기본구조-제어계층]] · [[01-GFL-제어구조]] · [[01-GFM-제어구조]] · [[simulation/emt/README|EMT 시뮬레이션]] · [[01-용어집]] · [[00-강좌-목차]]
