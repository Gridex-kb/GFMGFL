"""C06-디지털-제어와-지연 그림 생성. 저장소 루트에서 실행: python docs/_assets/강좌/scripts/C06_figs.py

그림 1 아래 패널과 그림 3 아래 패널은 EMT 모델(스위칭)을 쓴다. CPU 약 20 s.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join("simulation", "emt"))
import gfm_gfl_emt as emt
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
Ts = 1.0 / (2 * p0.f_sw)          # 100 µs
Tc = 1.0 / p0.f_sw                # 200 µs
wb = p0.wb
Orig = emt.Inverter

# ---- 그림 1: 샘플링·갱신 타이밍 ----
t = np.linspace(0, 4 * Ts, 4001)
ph = (t / Tc) % 1.0
carrier = np.where(ph < 0.5, 4 * ph - 1, 3 - 4 * ph)
d_old, d_new = -0.3, 0.5
duty = np.where(t < 2 * Ts, d_old, d_new)          # 샘플 1(100 µs)에서 계산 → 샘플 2(200 µs)부터 적용
gate = np.where(duty > carrier, 1.0, -1.0)
cmd_ideal = np.where(t < 1 * Ts, d_old, d_new)     # 지연이 없다면: 샘플 1 순간 바로 바뀜
# 반송파 반주기마다의 평균 극전압 (= 그 구간의 듀티)
avg = np.array([gate[(t >= k * Ts) & (t < (k + 1) * Ts)].mean() for k in range(4)])

# 실제 모델: Lf 전류 리플과 샘플 시점
fine = {"t": [], "if": []}
samp = {"t": [], "if": []}


class LoggedA(Orig):
    def sample(self, t_, x):
        samp["t"].append(t_)
        samp["if"].append(x[emt.IF_RE])
        super().sample(t_, x)

    def pcc_voltage(self, t_, x):
        fine["t"].append(t_)
        fine["if"].append(x[emt.IF_RE])
        return super().pcc_voltage(t_, x)


emt.Inverter = LoggedA
pa = Params(converter="average", scr=3.0)
x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.06), x0=x0, hires=(0.05, 0.06))
emt.Inverter = Orig

fig, axs = plt.subplots(3, 1, figsize=(7.2, 7.4), sharex=False)
us = t * 1e6
axs[0].plot(us, carrier, color=GRAY, lw=0.9, label="반송파 (5 kHz)")
axs[0].plot(us, duty, color=BLUE, lw=1.4, label="적용된 듀티 (변조파)")
axs[0].plot(us, cmd_ideal, color=ORANGE, lw=1.0, ls="--", label="지연이 없을 때")
ks = np.arange(5) * Ts * 1e6
axs[0].plot(ks, [-1, 1, -1, 1, -1], "o", color=AQUA, ms=5, label="샘플 시점 (꼭짓점)")
axs[0].annotate("", xy=(200, 0.82), xytext=(100, 0.82), arrowprops=dict(arrowstyle="->", color="k", lw=0.8))
axs[0].text(150, 0.88, "계산 1 Ts", ha="center", fontsize=8)
axs[0].set_ylim(-1.3, 2.0)
axs[0].set_ylabel("정규화 [-1, 1]")
axs[0].set_title("샘플 1(100 µs)에서 잰 값으로 계산한 지령은 샘플 2(200 µs)부터 적용된다", fontsize=10)
axs[0].legend(loc="upper left", fontsize=7.5, ncol=4, frameon=False)

axs[1].plot(us, gate, color=GRAY, lw=0.8, label="상 극전압 (스위치 상태)")
for k in range(4):
    axs[1].plot([k * 100, (k + 1) * 100], [avg[k]] * 2, color=BLUE, lw=2.0, label="Ts 구간 평균" if k == 0 else None)
axs[1].axvline(100, color=AQUA, lw=0.8, ls=":")
axs[1].axvline(250, color=ORANGE, lw=0.8, ls=":")
axs[1].annotate("", xy=(250, -1.15), xytext=(100, -1.15), arrowprops=dict(arrowstyle="->", color="k", lw=0.8))
axs[1].text(175, -1.32, "평균 지연 ≈ 1.5 Ts = 150 µs", ha="center", fontsize=8)
axs[1].set_ylim(-1.45, 1.9)
axs[1].set_ylabel("극전압 [V_dc/2 단위]")
axs[1].set_xlabel("시간 [µs]")
axs[1].set_title("적용 구간(200~300 µs)의 무게중심은 샘플 1보다 1.5 Ts 뒤", fontsize=10)
axs[1].legend(loc="upper left", fontsize=8, ncol=2, frameon=False)

tf, i_f = np.array(fine["t"]), np.array(fine["if"])
st, si = np.array(samp["t"]), np.array(samp["if"])
t0 = 0.0532
mf = (tf >= t0) & (tf <= t0 + 0.0006)
ms_ = (st >= t0 - 1e-9) & (st <= t0 + 0.0006)
axs[2].plot((tf[mf] - t0) * 1e6, i_f[mf], color=ORANGE, lw=0.9, label="Lf 전류 a상 (2 µs)")
axs[2].plot((st[ms_] - t0) * 1e6, si[ms_], "o", color=BLUE, ms=5, label="꼭짓점 샘플 (10 kHz)")
axs[2].set_xlabel("시간 [µs]")
axs[2].set_ylabel("전류 [pu]")
axs[2].set_title("EMT 모델: 꼭짓점 샘플은 리플의 가운데(평균값)를 잡는다", fontsize=10)
axs[2].legend(loc="upper right", fontsize=8, frameon=False)
for a in axs:
    a.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C06-샘플링-타이밍.png"), dpi=150)
plt.close(fig)

# ---- 그림 2: 순수 지연 vs 1차 지연 근사 ----
Td = 1.5 * Ts
f = np.logspace(1, np.log10(5000), 800)
w = 2 * np.pi * f
ph_delay = -np.degrees(w * Td)
H1 = 1.0 / (1.0 + 1j * w * Td)
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
axs[0].semilogx(f, ph_delay, color=BLUE, label="순수 지연 e^{-sTd}")
axs[0].semilogx(f, np.degrees(np.angle(H1)), color=ORANGE, ls="--", label="1차 지연 근사 1/(1+sTd)")
axs[0].axvline(p0.f_cc, color=GRAY, lw=0.7, ls=":")
axs[0].text(p0.f_cc * 1.05, -250, f"800 Hz: {-ph_delay[np.argmin(abs(f-800))]:.0f}° vs {-np.degrees(np.angle(1/(1+1j*2*np.pi*800*Td))):.0f}°",
            fontsize=8, color="k")
axs[0].set_ylabel("위상 [°]")
axs[0].set_title("Td = 150 µs: 지연 위상 ωTd 는 주파수에 비례해 끝없이 커진다", fontsize=10)
axs[0].legend(loc="lower left", fontsize=8, frameon=False)
axs[1].semilogx(f, np.zeros_like(f), color=BLUE, label="순수 지연 (크기 1)")
axs[1].semilogx(f, 20 * np.log10(np.abs(H1)), color=ORANGE, ls="--", label="1차 지연 근사")
axs[1].axvline(p0.f_cc, color=GRAY, lw=0.7, ls=":")
axs[1].set_ylabel("크기 [dB]")
axs[1].set_xlabel("주파수 [Hz]")
axs[1].set_title("1차 근사는 크기를 깎고 위상은 90°에서 멈춘다 (고주파에서 낙관적)", fontsize=10)
axs[1].legend(loc="lower left", fontsize=8, frameon=False)
for a in axs:
    a.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C06-지연-위상.png"), dpi=150)
plt.close(fig)


# ---- 그림 3: 연속 θ로 변환하면 생기는 톱니와 PLL 주파수 오프셋 ----
class ContTheta(Orig):
    """잘못된 각도 처리 재현: 샘플-홀드된 측정을 연속 회전하는 θ 로 dq 변환."""
    def deriv(self, t_, x):
        self.th_hold = x[emt.TH_C]
        return super().deriv(t_, x)


pg = Params(converter="average", scr=5.0, f_pll=50.0)
xg = steady_state("GFL", pg, t_init=1.5, dt=1e-5)
res = {}
for name, cls in (("hold", Orig), ("cont", ContTheta)):
    emt.Inverter = cls
    r = simulate("GFL", replace(pg, converter="switching"), Scenario(t_end=0.15), x0=xg)
    res[name] = (np.array(r["t"]), np.array(r["freq"]))
emt.Inverter = Orig

kp = 2 * pg.pll_zeta * 2 * np.pi * pg.f_pll / wb
off_hz = kp * wb * Ts / 2 * pg.f0
tt = np.linspace(0, 5 * Ts, 2001)
tk = np.floor(tt / Ts) * Ts
vq_cont = -np.sin(wb * (tt - tk))
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.8))
axs[0].plot(tt * 1e6, vq_cont, color=ORANGE, label="연속 θ로 변환")
axs[0].plot(tt * 1e6, np.zeros_like(tt), color=BLUE, label="샘플 시점 θ로 변환")
axs[0].axhline(-wb * Ts / 2, color=GRAY, lw=0.7, ls=":")
axs[0].text(108, -wb * Ts / 2 + 0.0015, f"평균 -ωTs/2 = {-wb*Ts/2:.4f}", fontsize=8, color=GRAY)
axs[0].set_ylabel("v_q [pu]")
axs[0].set_xlabel("시간 [µs]")
axs[0].set_ylim(-0.05, 0.012)
axs[0].set_title("홀드된 전압(|v| = 1 pu)을 계속 도는 θ로 보면 v_q 가 샘플마다 톱니로 흐른다", fontsize=10)
axs[0].legend(loc="lower right", fontsize=8, frameon=False)
for name, c, lab in (("cont", ORANGE, "연속 θ"), ("hold", BLUE, "샘플 시점 θ + 지연 보상")):
    tr, fr = res[name]
    m = tr >= 0.05
    k = 50  # 5 ms 이동평균 (샘플 잡음 제거, 보기용)
    fs = np.convolve(fr, np.ones(k) / k, mode="same")
    m &= tr <= tr[-1] - k * 1e-4  # 이동평균 끝단 제외
    axs[1].plot((tr[m] - 0.05) * 1e3, fs[m], color=c, label=f"{lab} (평균 {fr[tr >= 0.05].mean():.2f} Hz)")
axs[1].axhline(60.0, color=GRAY, lw=0.7, ls=":")
axs[1].set_ylabel("PLL 측정 주파수 [Hz]")
axs[1].set_xlabel("시간 [ms] (5 ms 이동평균)")
axs[1].set_ylim(59.5, 62.0)
axs[1].set_title(f"EMT 모델, PLL 50 Hz: 오프셋 ≈ kp·ω·Ts/2 = {off_hz:.2f} Hz (계통은 60 Hz)", fontsize=10)
axs[1].legend(loc="upper right", fontsize=8, frameon=False)
for a in axs:
    a.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C06-연속각-오차.png"), dpi=150)
plt.close(fig)

print("kp_pll =", round(kp, 3), "offset Hz =", round(off_hz, 3),
      {n: round(float(v[1][v[0] >= 0.05].mean()), 3) for n, v in res.items()})
