"""1강(3상 표현·공간벡터·dq) 강의 슬라이드용 그림. 한 그림에 한 가지, 큰 글자.
실행: python slides/lecture-figs/scripts/L01_figs.py  (저장소 루트)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NAVY, BLUE, GREEN, ORANGE, SLATE, GRID = "#013364", "#2463c8", "#3aa150", "#eb6834", "#45546b", "#dae3ec"
PH = {"a": BLUE, "b": ORANGE, "c": GREEN}
plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"], "axes.unicode_minus": False,
    "font.size": 24, "axes.labelsize": 24, "xtick.labelsize": 22, "ytick.labelsize": 22,
    "legend.fontsize": 24, "lines.linewidth": 3.5, "axes.linewidth": 1.2,
    "axes.edgecolor": "#c2ccd6", "axes.labelcolor": SLATE, "xtick.color": SLATE, "ytick.color": SLATE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff", "savefig.facecolor": "#ffffff",
    "legend.frameon": False,
})
f0, w = 60.0, 2 * np.pi * 60.0
t = np.linspace(0, 2 / f0, 2000)
ms = t * 1000


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=100)
    plt.close(fig)


# 1. 평형 3상 상전압
fig, ax = plt.subplots(figsize=(15, 6.4))
for k, (p, sh) in enumerate([("a", 0), ("b", -2 * np.pi / 3), ("c", 2 * np.pi / 3)]):
    ax.plot(ms, np.cos(w * t + sh), color=PH[p], label=f"v{p}")
ax.set_xlabel("시간 [ms]"); ax.set_ylabel("상전압 [pu]"); ax.set_ylim(-1.25, 1.25); ax.set_xlim(0, 33.3)
ax.legend(loc="upper right", ncol=3, bbox_to_anchor=(1.0, 1.12))
ax.annotate("120° = 5.56 ms", xy=(5.56, 1.0), xytext=(8.5, 1.12), fontsize=22, color=SLATE,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=2))
fig.tight_layout(); save(fig, "L01-3상-상전압.png")

# 2. 상별 순시전력과 합 (전류 진폭 1, 역률 0.8)
phi = np.arccos(0.8)
fig, ax = plt.subplots(figsize=(15, 6.4))
tot = 0
for p, sh in [("a", 0), ("b", -2 * np.pi / 3), ("c", 2 * np.pi / 3)]:
    pp = np.cos(w * t + sh) * np.cos(w * t + sh - phi)
    tot = tot + pp
    ax.plot(ms, pp, color=PH[p], label=f"v{p}·i{p}", lw=3)
ax.plot(ms, tot, color=NAVY, lw=5, label="합")
ax.set_xlabel("시간 [ms]"); ax.set_ylabel("순시전력 [pu²]"); ax.set_ylim(-0.4, 1.5); ax.set_xlim(0, 33.3)
ax.legend(loc="upper right", ncol=4, bbox_to_anchor=(1.0, 1.13))
ax.text(1, 1.27, "합 = 1.5·cosφ = 1.2  (일정)", fontsize=24, color=NAVY, fontweight="bold")
fig.tight_layout(); save(fig, "L01-순시전력-합.png")

# 3. αβ 성분 (Clarke 결과)
fig, ax = plt.subplots(figsize=(15, 6.0))
ax.plot(ms, np.cos(w * t), color=BLUE, label="vα")
ax.plot(ms, np.sin(w * t), color=ORANGE, label="vβ")
ax.set_xlabel("시간 [ms]"); ax.set_ylabel("[pu]"); ax.set_ylim(-1.25, 1.25); ax.set_xlim(0, 33.3)
ax.legend(loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.13))
fig.tight_layout(); save(fig, "L01-알파베타.png")

# 4. 예제: 진폭 1→0.7(25 ms), 위상 +30°(50 ms) 일 때 vd, vq
T = np.linspace(0, 0.075, 4000)
amp = np.where(T < 0.025, 1.0, 0.7)
ph = np.where(T < 0.05, 0.0, np.pi / 6)
vd, vq = amp * np.cos(ph), amp * np.sin(ph)
fig, ax = plt.subplots(figsize=(15, 6.0))
ax.plot(T * 1000, vd, color=BLUE, label="vd")
ax.plot(T * 1000, vq, color=ORANGE, label="vq")
for x in (25, 50):
    ax.axvline(x, color="#7d8ca2", ls="--", lw=2)
ax.text(2, 1.05, "vd = 1.0", fontsize=24, color=BLUE)
ax.text(28, 0.76, "vd = 0.7", fontsize=24, color=BLUE)
ax.text(53, 0.68, "vd = 0.61", fontsize=24, color=BLUE)
ax.text(53, 0.42, "vq = 0.35", fontsize=24, color=ORANGE)
ax.text(25.8, -0.33, "진폭 1→0.7", fontsize=22, color=SLATE)
ax.text(50.8, -0.33, "위상 +30°", fontsize=22, color=SLATE)
ax.set_xlabel("시간 [ms]"); ax.set_ylabel("[pu]"); ax.set_ylim(-0.45, 1.25); ax.set_xlim(0, 75)
ax.legend(loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.13))
fig.tight_layout(); save(fig, "L01-dq-예제.png")
print("ok")
