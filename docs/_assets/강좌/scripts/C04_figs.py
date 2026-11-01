"""C04-변조-SPWM-SVPWM 그림 생성. 저장소 루트에서 실행: python docs/_assets/강좌/scripts/C04_figs.py"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 1.1, "font.size": 10,
})
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#888888"
OUT = os.path.join("docs", "_assets", "강좌")
VDC = 2.256
H = VDC / 2
f0, fsw = 60.0, 5000.0


def minmax(ref):
    return -0.5 * (ref.max(axis=1) + ref.min(axis=1))


# ---- 그림 1: 영상분 주입 변조파 (상전압 지령 진폭 1.302 pu) ----
t = np.linspace(0, 1 / f0, 2001)
vm = VDC / np.sqrt(3)
ref = np.stack([vm * np.cos(2 * np.pi * f0 * t - k * 2 * np.pi / 3) for k in range(3)], axis=1)
v0 = minmax(ref)
tm = t * 1e3
fig, axs = plt.subplots(3, 1, figsize=(7.2, 6.6), sharex=True)
for k, (nm, c) in enumerate(zip("abc", (BLUE, ORANGE, AQUA))):
    axs[0].plot(tm, ref[:, k], color=c, label=f"{nm}상 지령")
axs[0].set_ylabel("상전압 지령 [pu]")
axs[0].set_title("지령 진폭 1.302 pu: 사인 그대로는 ±1.128 pu(= ±$V_{dc}$/2)를 넘는다", fontsize=10)
axs[1].plot(tm, v0, color=GRAY, label="$v_0 = -(\\max+\\min)/2$")
axs[1].set_ylabel("영상분 [pu]")
axs[1].set_title("min-max 영상분 (3배 주파수 삼각파 모양)", fontsize=10)
axs[2].plot(tm, ref[:, 0] + v0, color=BLUE, label="a상 변조파 $v_a + v_0$")
axs[2].plot(tm, ref[:, 0], color=BLUE, lw=0.7, ls=":", label="a상 사인 지령 $v_a$")
axs[2].set_ylabel("변조파 [pu]")
axs[2].set_title("주입 후 변조파의 최댓값이 정확히 ±1.128 pu에 닿는다", fontsize=10)
axs[2].set_xlabel("시간 [ms]")
for a in axs:
    a.axhline(H, color=ORANGE, lw=0.8, ls="--")
    a.axhline(-H, color=ORANGE, lw=0.8, ls="--")
    a.set_ylim(-1.6, 1.75)
    a.set_yticks([-H, 0, H])
    a.set_yticklabels(["-1.128", "0", "1.128"])
    a.grid(alpha=0.25, lw=0.5)
    a.legend(loc="upper right", fontsize=8, ncol=3, frameon=False)
for a in (axs[0], axs[2]):
    a.annotate("-1.302", xy=(8.33, -1.302), xytext=(9.6, -1.52), fontsize=8, color=BLUE,
               arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6))
axs[1].set_ylim(-0.5, 0.6); axs[1].set_yticks([-0.2, 0, 0.2]); axs[1].set_yticklabels(["-0.2", "0", "0.2"])
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C04-영상분주입-변조파.png"), dpi=150)
plt.close(fig)

# ---- 그림 2: 반송파 비교와 꼭짓점 동기 2회 갱신 ----
dt = 0.2e-6
t = np.arange(0, 3 / fsw, dt)
Ts = 1 / (2 * fsw)
ph = (t * fsw) % 1.0
car = np.where(ph < 0.5, 4 * ph - 1, 3 - 4 * ph)
tk = np.floor(t / Ts + 1e-9) * Ts
duty_cont = 0.25 + 0.5 * np.sin(2 * np.pi * 1500 * t)      # 보기 쉽게 과장한 느린 지령 변화
duty = 0.25 + 0.5 * np.sin(2 * np.pi * 1500 * tk)
s = np.where(duty > car, 1, -1)
tu = t * 1e6
fig, axs = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
axs[0].plot(tu, car, color=GRAY, lw=0.9, label="삼각파 반송파 (5 kHz)")
axs[0].plot(tu, duty_cont, color=ORANGE, lw=0.7, ls=":", label="연속 지령")
axs[0].plot(tu, duty, color=BLUE, lw=1.3, label="샘플-홀드된 듀티")
ks = np.arange(0, 7) * Ts * 1e6
axs[0].plot(ks, 0.25 + 0.5 * np.sin(2 * np.pi * 1500 * ks * 1e-6), "o", color=BLUE, ms=4)
for x in ks:
    axs[0].axvline(x, color=AQUA, lw=0.6, ls="--")
axs[0].text(ks[1] + 3, -1.25, "샘플 시점 = 반송파 골·꼭짓점 (100 µs마다, 10 kHz)", color=AQUA, fontsize=8)
axs[0].set_ylabel("정규화 듀티")
axs[0].set_ylim(-1.35, 1.6)
axs[0].legend(loc="upper right", fontsize=8, ncol=3, frameon=False)
axs[1].step(tu, s * H, where="post", color=BLUE, lw=1.0)
axs[1].set_ylabel("극전압 [pu]")
axs[1].set_yticks([-H, H]); axs[1].set_yticklabels(["-1.128", "1.128"])
axs[1].set_ylim(-1.5, 1.5)
axs[1].set_xlabel("시간 [µs]")
for x in ks:
    axs[1].axvline(x, color=AQUA, lw=0.6, ls="--")
axs[0].set_title("반송파 비교 PWM: 골·꼭짓점에서 듀티를 갱신(2회 갱신)", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C04-반송파-2회갱신.png"), dpi=150)
plt.close(fig)

# ---- 그림 3: 스위칭 고조파 스펙트럼 (극전압 vs 상전압) ----
dt = 0.5e-6
T = 0.25                                         # 60 Hz 15주기, 반송파 1250주기 → 누설 없음
t = np.arange(0, T, dt)
tk = np.floor(t / Ts) * Ts
vm = 1.0
ref = np.stack([vm * np.cos(2 * np.pi * f0 * tk - k * 2 * np.pi / 3) for k in range(3)], axis=1)
d = np.clip((ref + minmax(ref)[:, None]) / H, -1, 1)
ph = (t * fsw) % 1.0
car = np.where(ph < 0.5, 4 * ph - 1, 3 - 4 * ph)
vp = np.where(d > car[:, None], H, -H)
van = vp[:, 0] - vp.mean(axis=1)
f = np.fft.rfftfreq(len(t), dt)
amp = lambda x: 2 * np.abs(np.fft.rfft(x)) / len(x)
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True)
for a, x, nm in ((axs[0], vp[:, 0], "a상 극전압 $v_{a0}$ (DC 중점 기준)"),
                 (axs[1], van, "a상 상전압 $v_{an}$ (부하 중성점 기준)")):
    A_ = amp(x)
    m = (f <= 16000) & (A_ > 1e-3)
    a.vlines(f[m] / 1e3, 1e-3, A_[m], color=BLUE, lw=0.8)
    a.set_yscale("log"); a.set_ylim(1e-3, 2)
    a.set_yticks([1e-3, 1e-2, 1e-1, 1]); a.set_yticklabels(["0.001", "0.01", "0.1", "1"])
    a.minorticks_off()
    a.set_ylabel("진폭 [pu]")
    a.set_title(nm, fontsize=10)
    a.grid(alpha=0.25, lw=0.5, which="major")
    for fc, lab in ((5, "$f_{sw}$"), (10, "$2f_{sw}$"), (15, "$3f_{sw}$")):
        a.axvline(fc, color=ORANGE, lw=0.6, ls="--")
        a.text(fc + 0.1, 1.1, lab, color=ORANGE, fontsize=8)
axs[0].text(0.35, 0.25, "기본파 60 Hz\n+ 영상분(3·9·… 차)", fontsize=8)
axs[1].text(0.35, 0.25, "기본파 60 Hz\n(영상분 사라짐)", fontsize=8)
axs[1].set_xlabel("주파수 [kHz]")
axs[1].set_xlim(0, 16)
fig.suptitle("SVPWM 등가 변조(지령 1.0 pu, 5 kHz)의 전압 스펙트럼", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C04-스위칭-스펙트럼.png"), dpi=150)
plt.close(fig)
print("saved")
