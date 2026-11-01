"""C07-전류-제어 그림 생성. 저장소 루트에서 실행: python docs/_assets/강좌/scripts/C07_figs.py

그림 1은 독립 dq 전류루프 모의(numpy), 그림 2는 EMT 모델(스위칭, 0.2 s × 3), 그림 3은 기하 그림. CPU 약 30 s.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join("simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state, replace

plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 1.1, "font.size": 10,
})
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#888888"
OUT = os.path.join("docs", "_assets", "강좌")
p0 = Params()
wb = p0.wb
Ts = 1.0 / (2 * p0.f_sw)
wcc = 2 * np.pi * p0.f_cc
Kp = wcc * p0.Lf / wb
Ki = Kp * wcc / 5


def current_loop(i_ref_fn, t_end=0.01, decouple=True, delay=True, dt=2e-6):
    """dq 전류루프 독립 모의. 플랜트: (Lf/ωb) di/dt = v - Rf·i - jωLf·i - v_g (Cf 무시, v_g = 1 pu 고정).
    제어: 10 kHz 샘플, 1샘플 계산 지연 + 영차 홀드(PWM 평균) → 실효 지연 약 1.5 Ts."""
    n = int(round(t_end / dt))
    per = int(round(Ts / dt))
    i = 0j
    x = 1.0 + 0j          # 적분기: 정상상태에서 계통 전압 1 pu 를 떠맡고 있음
    v_now = v_next = 1.0 + 0j
    T, I = np.empty(n), np.empty(n, complex)
    for k in range(n):
        t = k * dt
        if k % per == 0:
            e = i_ref_fn(t) - i
            v = Kp * e + x + (1j * p0.Lf * i if decouple else 0)
            if abs(v) > p0.V_conv_max:
                v *= p0.V_conv_max / abs(v)
            else:
                x += Ki * Ts * e
            if delay:
                v_now, v_next = v_next, v
            else:
                v_now = v
        di = (v_now - p0.Rf * i - 1j * p0.Lf * i - 1.0) * (wb / p0.Lf)
        i += di * dt
        T[k], I[k] = t, i
    return T, I


# ---- 그림 1: 소신호 계단 응답 (i_d 지령 0 → 0.1 pu) ----
step = lambda t: 0.1 + 0j if t >= 0.001 else 0j
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
T, I1 = current_loop(step, decouple=True)
_, I2 = current_loop(step, decouple=False)
_, I3 = current_loop(step, decouple=True, delay=False)
ms = (T - 0.001) * 1e3
axs[0].plot(ms, np.where(T >= 0.001, 0.1, 0.0), color=GRAY, lw=0.8, ls="--", label="지령")
axs[0].plot(ms, I3.real, color=AQUA, lw=1.0, label="지연 없음 (이상)")
axs[0].plot(ms, I1.real, color=BLUE, label="지연 1.5 Ts + 디커플링 (모델)")
axs[0].plot(ms, I2.real, color=ORANGE, label="지연 1.5 Ts, 디커플링 없음")
os_ = (I1.real.max() - 0.1) / 0.1 * 100
os0 = (I3.real.max() - 0.1) / 0.1 * 100
axs[0].set_ylabel("i_d [pu]")
axs[0].set_title(f"800 Hz 설계, 0.1 pu 계단: 오버슈트 지연 1.5 Ts에서 약 {os_:.0f} %, 지연 없으면 약 {os0:.0f} %", fontsize=10)
axs[0].legend(loc="lower right", fontsize=8, frameon=False)
axs[1].plot(ms, I3.imag, color=AQUA, lw=1.0, label="지연 없음 (이상)")
axs[1].plot(ms, I1.imag, color=BLUE, label="디커플링 있음")
axs[1].plot(ms, I2.imag, color=ORANGE, label="디커플링 없음")
axs[1].set_ylabel("i_q [pu]")
axs[1].set_xlabel("계단 이후 시간 [ms]")
axs[1].set_title("교차결합 jωLf·i: 디커플링이 없으면 i_d 변화가 i_q 를 흔든다", fontsize=10)
axs[1].legend(loc="lower right", fontsize=8, frameon=False)
for a in axs:
    a.grid(alpha=0.25, lw=0.5)
    a.set_xlim(-0.5, 6)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C07-전류-계단응답.png"), dpi=150)
plt.close(fig)

# ---- 그림 2: PCC 전압 순시 피드포워드와 약계통 (GFM, SCR 2, 스위칭 모델) ----
cases = [("피드포워드 없음 (모델 기본)", 0.0, 100.0, BLUE),
         ("순시 피드포워드 (ff_gain = 1)", 1.0, 0.0, ORANGE),
         ("100 Hz 저역통과 피드포워드", 1.0, 100.0, AQUA)]
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.6))
stats = {}
for lab, ff, fv, c in cases:
    pa = Params(converter="average", scr=2.0, ff_gain=ff, f_vff=fv)
    x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)   # 평균값 모델로 초기화 (이 모델에선 안정)
    r = simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.2), x0=x0)
    t, P = np.array(r["t"]), np.array(r["P"])
    stats[lab] = P[t > 0.1].std()
    axs[0].plot(t * 1e3, P, color=c, lw=0.8 if ff and not fv else 1.0, label=lab)
    m = (t >= 0.15) & (t <= 0.17)
    axs[1].plot(t[m] * 1e3, P[m], color=c, lw=1.0, label=f"{lab} (σ = {stats[lab]:.3f} pu)")
axs[0].set_ylabel("P [pu]")
axs[0].set_xlabel("시간 [ms]")
axs[0].set_title("GFM, SCR 2: 순시 피드포워드만 진동이 자라 지속된다", fontsize=10)
axs[0].legend(loc="upper right", fontsize=8, frameon=False)
axs[1].set_ylabel("P [pu]")
axs[1].set_xlabel("시간 [ms] (20 ms 확대)")
axs[1].set_title("확대: 진동 주기 약 1.8 ms (약 560 Hz)", fontsize=10)
axs[1].legend(loc="upper right", fontsize=8, frameon=False)
axs[0].set_ylim(0.0, 1.2)
axs[1].set_ylim(0.0, 1.2)
for a in axs:
    a.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C07-피드포워드-불안정.png"), dpi=150)
plt.close(fig)

# ---- 그림 3: 원형 전류 제한과 우선순위 ----
Imax = p0.I_max
fig, ax = plt.subplots(figsize=(6.4, 6.0))
th = np.linspace(0, 2 * np.pi, 400)
ax.plot(Imax * np.cos(th), Imax * np.sin(th), color=GRAY, lw=1.0)
ax.text(0.86, -0.97, "|i| = 1.2 pu", color=GRAY, fontsize=8)
# (a) GFL 정상: 유효전류 우선
req_a = np.array([1.1, 0.8])
lim_a = np.array([1.1, np.sqrt(Imax ** 2 - 1.1 ** 2)])
# (b) GFL FRT: 무효전류 우선 (i_r = 0.95·Imax 고정)
ir = 0.95 * Imax
req_b = np.array([0.7, ir])
lim_b = np.array([np.sqrt(Imax ** 2 - ir ** 2), ir])
# (c) GFM: 방향 유지 원형 축소
req_c = np.array([1.3, -0.6])
lim_c = req_c * Imax / np.hypot(*req_c)
for req, lim, c, lab in ((req_a, lim_a, BLUE, "GFL 정상: 유효 우선 (i_d 유지, i_r 축소)"),
                         (req_b, lim_b, ORANGE, "GFL FRT: 무효 우선 (i_r 고정, i_d 축소)"),
                         (req_c, lim_c, AQUA, "GFM: 방향 유지, 크기만 1.2 pu로")):
    ax.plot(*req, "o", mfc="none", mec=c, ms=8)
    ax.plot(*lim, "o", color=c, ms=7, label=lab)
    ax.annotate("", xy=lim, xytext=req, arrowprops=dict(arrowstyle="->", color=c, lw=1.2))
ax.axhline(0, color="k", lw=0.5)
ax.axvline(0, color="k", lw=0.5)
ax.text(1.32, 0.04, "i_d (유효, P)", fontsize=8)
ax.text(0.04, 1.4, "i_r = -i_q (무효, +Q)", fontsize=8)
ax.text(-1.45, -1.42, "빈 원: 외부 루프가 요구한 지령\n찬 원: 제한 후 지령", fontsize=8, color=GRAY)
ax.set_xlim(-1.5, 1.7)
ax.set_ylim(-1.5, 1.6)
ax.set_aspect("equal")
ax.set_xlabel("유효전류 [pu]")
ax.set_ylabel("무효전류 [pu]")
ax.set_title("원형 전류 제한: 누구를 먼저 깎을 것인가", fontsize=10)
ax.legend(loc="upper left", fontsize=8, frameon=False)
ax.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C07-전류제한-우선순위.png"), dpi=150)
plt.close(fig)

print(f"Kp = {Kp:.3f}, Ki = {Ki:.0f}, overshoot = {os_:.1f} % (no delay {os0:.1f} %)", {k: round(float(v), 4) for k, v in stats.items()})
