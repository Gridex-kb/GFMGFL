"""C05-필터-변압기-측정점 그림 생성. 저장소 루트에서 실행: python docs/_assets/강좌/scripts/C05_figs.py

그림 1은 해석식, 그림 2·3은 EMT 모델(스위칭, 0.2 s)을 쓴다. CPU 약 10 s.
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
f0 = p0.f0

# ---- 그림 1: L / LCL 주파수 응답 (컨버터 전압 → 변압기 전류, 강한 계통) ----
f = np.logspace(1, 4, 3000)
h = f / f0
Zf = p0.Rf + 1j * h * p0.Lf
Zg = p0.Rt + 1j * h * p0.Lt


def lcl(Rd):
    Zc = Rd + 1.0 / (1j * h * p0.Cf)
    i_f = 1.0 / (Zf + Zc * Zg / (Zc + Zg))
    return i_f * Zc / (Zc + Zg)


L_only = 1.0 / (p0.Rf + p0.Rt + 1j * h * (p0.Lf + p0.Lt))
f_res = f0 * np.sqrt((p0.Lf + p0.Lt) / (p0.Lf * p0.Lt * p0.Cf))
db = lambda z: 20 * np.log10(np.abs(z))
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.semilogx(f, db(L_only), color=GRAY, ls="--", label="L 필터 (Lf + Lt = 0.3 pu)")
ax.semilogx(f, db(lcl(0.0)), color=ORANGE, label="LCL, 댐핑 없음 (Rd = 0)")
ax.semilogx(f, db(lcl(p0.Rd)), color=BLUE, label=f"LCL, Rd = {p0.Rd:g} pu (모델)")
ax.axvline(f_res, color=GRAY, lw=0.7, ls=":")
ax.axvline(p0.f_sw, color=GRAY, lw=0.7, ls=":")
ax.text(f_res * 1.04, 35, f"공진 {f_res:.0f} Hz", fontsize=8, color=GRAY)
ax.text(p0.f_sw * 0.62, 35, "스위칭 5 kHz", fontsize=8, color=GRAY)
ax.set_ylim(-80, 45)
ax.set_xlim(10, 1e4)
ax.set_xlabel("주파수 [Hz]")
ax.set_ylabel("|변압기 전류 / 컨버터 전압| [dB, pu/pu]")
ax.set_title("LCL은 공진 위에서 -60 dB/dec로 꺾이고, Rd가 공진 봉우리를 누른다", fontsize=10)
ax.grid(alpha=0.25, lw=0.5, which="both")
ax.legend(loc="lower left", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C05-LCL-주파수응답.png"), dpi=150)
plt.close(fig)

# ---- EMT: 강계통 GFM, 스위칭 모델. 2 µs 파형과 샘플 시점 측정을 함께 기록 ----
fine = {"t": [], "if": [], "it": []}
samp = {"t": [], "P_pcc": [], "P_lf": []}


class Logged(emt.Inverter):
    def sample(self, t, x):
        v_term, v_pcc, i_t = self.network(t, x)[:3]
        i_f = complex(x[emt.IF_RE], x[emt.IF_IM])
        samp["t"].append(t)
        samp["P_pcc"].append((v_pcc * i_t.conjugate()).real)   # 변압기 전류 × PCC 전압
        samp["P_lf"].append((v_term * i_f.conjugate()).real)   # Lf 전류 × 필터 단자 전압
        super().sample(t, x)

    def pcc_voltage(self, t, x):  # hires 구간에서만 호출됨: 이때 x 는 스텝 시작 상태
        fine["t"].append(t)
        fine["if"].append(x[emt.IF_RE])
        fine["it"].append(x[emt.IG_RE])
        return super().pcc_voltage(t, x)


emt.Inverter = Logged
pa = Params(converter="average", scr=10.0)
x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
r = simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.2), x0=x0, hires=(0.15, 0.2))

# ---- 그림 2: Lf 전류 vs 변압기 전류 (a상) ----
tf = np.array(fine["t"])
i_f = np.array(fine["if"])
i_t = np.array(fine["it"])
k = 100  # 반송파 한 주기 = 200 µs = 2 µs × 100
sm = np.convolve(i_f, np.ones(k) / k, mode="same")
rip = (i_f - sm)[k:-k]
rip_pp = rip.max() - rip.min()
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.6))
m1 = (tf >= 0.15) & (tf <= 0.15 + 1 / f0)
axs[0].plot((tf[m1] - 0.15) * 1e3, i_f[m1], color=ORANGE, lw=0.6, label="컨버터측 전류 (Lf)")
axs[0].plot((tf[m1] - 0.15) * 1e3, i_t[m1], color=BLUE, lw=1.2, label="변압기 전류")
axs[0].set_ylabel("a상 전류 [pu]")
axs[0].set_title(f"한 주기: Lf 전류에는 리플이 얹혀 있다 (리플 약 {rip_pp:.2f} pu p-p)", fontsize=10)
t0z = 0.15 + 0.25 / f0 - 0.0005
m2 = (tf >= t0z) & (tf <= t0z + 0.001)
axs[1].plot((tf[m2] - t0z) * 1e3, i_f[m2], color=ORANGE, lw=0.9, label="컨버터측 전류 (Lf)")
axs[1].plot((tf[m2] - t0z) * 1e3, i_t[m2], color=BLUE, lw=1.2, label="변압기 전류")
axs[1].set_ylabel("a상 전류 [pu]")
axs[1].set_xlabel("시간 [ms]")
axs[1].set_title("1 ms 확대: 5 kHz 리플은 Cf로 빠지고 변압기 전류는 매끈하다", fontsize=10)
for a, loc in zip(axs, ("lower left", "upper right")):
    a.grid(alpha=0.25, lw=0.5)
    a.legend(loc=loc, fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C05-리플-파형.png"), dpi=150)
plt.close(fig)

# ---- 그림 3: 측정점에 따른 전력 측정 잡음 (샘플 시점, 10 kHz) ----
ts = np.array(samp["t"])
Pp = np.array(samp["P_pcc"])
Pl = np.array(samp["P_lf"])
m = ts >= 0.1
s_p, s_l = Pp[m].std(), Pl[m].std()
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.6))
axs[0].plot((ts[m] - 0.1) * 1e3, Pl[m], color=ORANGE, lw=0.7, label=f"Lf 전류 × 필터 단자 전압 (σ = {s_l:.4f} pu)")
axs[0].plot((ts[m] - 0.1) * 1e3, Pp[m], color=BLUE, lw=0.9, label=f"변압기 전류 × PCC 전압 (σ = {s_p:.4f} pu)")
axs[0].set_ylabel("샘플 시점 P [pu]")
axs[0].set_xlabel("시간 [ms]")
axs[0].set_title("같은 운전점, 같은 샘플 시점인데 측정점만 다르다 (GFM, SCR 10)", fontsize=10)
axs[0].legend(loc="upper right", fontsize=8, frameon=False)


def spec(x):
    x = x - x.mean()
    F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) * 4.0 / len(x)
    return np.fft.rfftfreq(len(x), 1e-4), F


fs_, Fl = spec(Pl[m])
_, Fp = spec(Pp[m])
axs[1].plot(fs_, Fl * 1e3, color=ORANGE, lw=0.8, label="Lf 전류 × 필터 단자 전압")
axs[1].plot(fs_, Fp * 1e3, color=BLUE, lw=0.9, label="변압기 전류 × PCC 전압")
for fk in (360, 720, 1080, 1440):
    axs[1].axvline(fk, color=GRAY, lw=0.6, ls=":")
axs[1].set_xlim(0, 2000)
axs[1].set_xlabel("주파수 [Hz] (점선: 360 Hz 배수)")
axs[1].set_ylabel("진폭 [10⁻³ pu]")
axs[1].set_title("Lf 측정은 고주파 잡음이 전반적으로 크고, 360 Hz 배수에 봉우리가 선다", fontsize=10)
axs[1].legend(loc="upper right", fontsize=8, frameon=False)
for a in axs:
    a.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C05-측정점-잡음.png"), dpi=150)
plt.close(fig)

print(f"f_res = {f_res:.0f} Hz, ripple p-p = {rip_pp:.3f} pu, sigma(Lf) = {s_l:.4f}, sigma(PCC) = {s_p:.4f}")
