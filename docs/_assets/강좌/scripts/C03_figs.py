"""C03-2레벨-VSC 그림 생성. 저장소 루트에서 실행: python docs/_assets/강좌/scripts/C03_figs.py"""
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
    "lines.linewidth": 1.2, "font.size": 10,
})
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#888888"
OUT = os.path.join("docs", "_assets", "강좌")
VDC = 2.256                     # DC 링크 [pu]
A = np.exp(2j * np.pi / 3)


def ab(sa, sb, sc):
    """스위치 상태(1=상단 ON, 0=하단 ON) → αβ 전압 [pu] (진폭 불변)."""
    va, vb, vc = [(2 * s - 1) * VDC / 2 for s in (sa, sb, sc)]
    return (2 / 3) * (va + vb * A + vc * A ** 2)


# ---- 그림 1: 전압 벡터 육각형 ----
fig, ax = plt.subplots(figsize=(6.2, 5.8))
states = [(sa, sb, sc) for sa in (0, 1) for sb in (0, 1) for sc in (0, 1)]
act = [s for s in states if len(set(s)) > 1]
order = [(1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1), (1, 0, 1)]
hexv = np.array([ab(*s) for s in order + [order[0]]])
ax.plot(hexv.real, hexv.imag, color=BLUE, lw=1.0, label="유효 벡터를 잇는 육각형")
r = VDC / np.sqrt(3)
th = np.linspace(0, 2 * np.pi, 300)
ax.plot(r * np.cos(th), r * np.sin(th), color=AQUA, lw=1.0, ls="--",
        label="내접원 반지름 $V_{dc}/\\sqrt{3}$ ≈ 1.302 pu")
for k, s in enumerate(order):
    v = ab(*s)
    ax.annotate("", xy=(v.real, v.imag), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.0))
    lab = f"V{k+1} ({s[0]}{s[1]}{s[2]})"
    off = v / abs(v) * 0.30
    ax.text(v.real + off.real, v.imag + off.imag, lab, ha="center", va="center", fontsize=9)
ax.plot(0, 0, "o", color=ORANGE, ms=5)
ax.text(0.08, -0.18, "V0 (000)\nV7 (111)", fontsize=9, va="top")
ax.text(1.40, -0.45, f"|V| = 2/3·$V_{{dc}}$\n= {2*VDC/3:.3f} pu", fontsize=9, color=ORANGE)
ax.set_aspect("equal")
ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.0, 2.0)
ax.set_xlabel("α [pu]"); ax.set_ylabel("β [pu]")
ax.axhline(0, color=GRAY, lw=0.5); ax.axvline(0, color=GRAY, lw=0.5)
ax.set_title("2레벨 VSC 스위칭 상태 8개가 만드는 전압 벡터 ($V_{dc}$ = 2.256 pu)", fontsize=10)
ax.legend(loc="lower left", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C03-전압벡터-육각형.png"), dpi=150)
plt.close(fig)

# ---- 그림 2: 6스텝 순서에서 극전압 → 영상분 → 상전압 ----
f0 = 60.0
t = np.linspace(0, 1 / f0, 2401)
seg = np.minimum((t * f0 * 6).astype(int), 5)          # 60° 구간 번호
S = np.array([order[k] for k in seg])                   # 각 구간의 스위칭 상태
vpole = (2 * S - 1) * VDC / 2                           # 극전압 (DC 중점 기준)
v0 = vpole.mean(axis=1)                                 # 영상분 (중성점 전위)
vph = vpole - v0[:, None]                               # 상전압 (부하 중성점 기준)
tm = t * 1e3
fig, axs = plt.subplots(3, 1, figsize=(7.2, 6.4), sharex=True)
for i, (nm, c) in enumerate(zip("abc", (BLUE, ORANGE, AQUA))):
    axs[0].step(tm, vpole[:, i] + 0.04 * (1 - i), where="post", color=c, label=f"{nm}상 극전압 $v_{{{nm}0}}$")
axs[0].set_ylabel("극전압 [pu]")
axs[0].set_yticks([-VDC / 2, 0, VDC / 2])
axs[0].legend(loc="upper right", fontsize=8, ncol=3, frameon=False)
axs[0].set_ylim(-1.6, 1.9)
axs[0].set_title("6스텝 순서(V1→V6)에서 극전압, 영상분, 상전압", fontsize=10)
axs[1].step(tm, v0, where="post", color=GRAY)
axs[1].set_ylabel("영상분 $v_{n0}$ [pu]")
axs[1].set_yticks([-VDC / 6, 0, VDC / 6])
axs[1].set_ylim(-0.6, 0.6)
axs[2].step(tm, vph[:, 0], where="post", color=BLUE, label="a상 상전압 $v_{an}$")
axs[2].plot(tm, 2 / np.pi * VDC * np.cos(2 * np.pi * f0 * t - np.pi / 6), color=ORANGE, lw=0.9, ls="--",
            label=f"기본파 (진폭 {2/np.pi*VDC:.3f} pu)")
axs[2].set_ylabel("상전압 [pu]")
axs[2].set_yticks([-2 * VDC / 3, -VDC / 3, 0, VDC / 3, 2 * VDC / 3])
axs[2].set_ylim(-1.9, 2.1)
axs[2].legend(loc="upper right", fontsize=8, ncol=2, frameon=False)
axs[2].set_xlabel("시간 [ms]")
for a in axs:
    a.grid(alpha=0.25, lw=0.5)
    a.set_yticklabels([f"{v:.3f}" for v in a.get_yticks()])
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C03-극전압-상전압.png"), dpi=150)
plt.close(fig)
print("saved")
