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


# ---------------------------------------------------------------- 벡터 그림 공통
def vec_axes(figsize=(8, 8), lim=1.35):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, z, color, lw=5, z0=0j, label=None, loff=(0.06, 0.06), fs=28):
    ax.annotate("", xy=(z.real, z.imag), xytext=(z0.real, z0.imag),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=34))
    if label:
        ax.text(z.real + loff[0], z.imag + loff[1], label, color=color, fontsize=fs, fontweight="bold")


a = np.exp(1j * 2 * np.pi / 3)

# 5. 페이저도: va, vb, vc 와 선간전압 vab
fig, ax = vec_axes(figsize=(9, 8), lim=1.95)
for k, (p, z) in enumerate([("a", 1), ("b", a ** 2), ("c", a)]):
    arrow(ax, z, PH[p], label=f"V{p}", loff=(0.08, 0.02) if p == "a" else (-0.25, 0.08) if p == "c" else (-0.25, -0.18))
vab = 1 - a ** 2
arrow(ax, vab, NAVY, lw=6, label="Vab = √3 ∠30°", loff=(-0.75, 0.2), fs=26)
ax.plot([1, vab.real], [0, vab.imag], color="#7d8ca2", ls="--", lw=2.5)
ax.add_patch(plt.Circle((0, 0), 1, fill=False, ls=":", lw=2, color="#c2ccd6"))
th = np.linspace(0, np.pi / 6, 40)
ax.plot(0.55 * np.cos(th), 0.55 * np.sin(th), color=SLATE, lw=2.5)
ax.text(0.6, 0.12, "30°", fontsize=24, color=SLATE)
fig.tight_layout(); save(fig, "L01-페이저-선간.png")

# 6. 공간벡터 합성: ωt=0 에서 (2/3)(va·â + vb·b̂ + vc·ĉ)
def sv_construct(wt_deg, fname, show_terms=True):
    fig, ax = vec_axes(figsize=(8.5, 8.5), lim=1.45)
    for p, z in [("a", 1), ("b", a), ("c", a ** 2)]:
        ax.plot([-1.3 * z.real, 1.3 * z.real], [-1.3 * z.imag, 1.3 * z.imag], color="#c2ccd6", lw=2.5)
        ax.text(1.36 * z.real - 0.05, 1.36 * z.imag - 0.05, f"{p}축", fontsize=24, color=PH[p], fontweight="bold")
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, ls=":", lw=2.5, color="#7d8ca2"))
    wt = np.deg2rad(wt_deg)
    vals = {"a": np.cos(wt), "b": np.cos(wt - 2 * np.pi / 3), "c": np.cos(wt + 2 * np.pi / 3)}
    v = np.exp(1j * wt)
    ax.plot([0, v.real], [0, v.imag], color=NAVY, lw=16, alpha=0.18, solid_capstyle="round")
    ax.text(v.real + 0.06, v.imag + 0.04, "v", color=NAVY, fontsize=32, fontweight="bold")
    if show_terms:
        acc = 0j
        for p, z in [("a", 1), ("b", a), ("c", a ** 2)]:
            term = 2 / 3 * vals[p] * z
            arrow(ax, acc + term, PH[p], lw=5, z0=acc)
            acc += term
    ax.text(-1.4, -1.42, f"ωt = {wt_deg}°", fontsize=30, color=NAVY, fontweight="bold")
    fig.tight_layout(); save(fig, fname)


sv_construct(0, "L01-공간벡터-합성.png")
for d in (0, 60, 120):
    sv_construct(d, f"L01-회전-{d:03d}.png")

# 7. dq 좌표: αβ 위에서 θ 만큼 돌아간 d, q 축과 벡터 v
fig, ax = vec_axes(figsize=(9, 8.5), lim=1.45)
ax.plot([-1.3, 1.3], [0, 0], color="#c2ccd6", lw=2.5); ax.plot([0, 0], [-1.3, 1.3], color="#c2ccd6", lw=2.5)
ax.text(1.32, -0.12, "α", fontsize=30, color=SLATE); ax.text(0.05, 1.32, "β", fontsize=30, color=SLATE)
th0 = np.deg2rad(35)
dax, qax = np.exp(1j * th0), np.exp(1j * (th0 + np.pi / 2))
arrow(ax, 1.3 * dax, BLUE, lw=3.5, label="d", loff=(0.04, 0.0), fs=32)
arrow(ax, 1.3 * qax, ORANGE, lw=3.5, label="q", loff=(-0.12, 0.04), fs=32)
v = 1.0 * np.exp(1j * np.deg2rad(60))
arrow(ax, v, NAVY, lw=7, label="v", loff=(0.04, 0.05), fs=32)
proj = (v * np.conj(dax)).real * dax
ax.plot([v.real, proj.real], [v.imag, proj.imag], color="#7d8ca2", ls="--", lw=2.5)
ax.plot([0, proj.real], [0, proj.imag], color=BLUE, lw=9, alpha=0.35)
ax.text(proj.real * 0.78 + 0.08, proj.imag * 0.78 - 0.2, "vd", fontsize=28, color=BLUE, fontweight="bold")
th = np.linspace(0, th0, 40)
ax.plot(0.42 * np.cos(th), 0.42 * np.sin(th), color=SLATE, lw=2.5)
ax.text(0.47, 0.1, "θ", fontsize=28, color=SLATE)
fig.tight_layout(); save(fig, "L01-dq-좌표.png")

# 8. 질문용: PI 로 60 Hz 지령 추종 (대역폭 100 Hz) → 위상·크기 오차
fb = 100.0
Lf_s = 0.2 / (2 * np.pi * 60)
wc = 2 * np.pi * fb
kp, ki = wc * Lf_s, wc * Lf_s * wc / 5
s = 1j * w
G = (kp + ki / s) / (Lf_s * s)
T = G / (1 + G)
ref = np.cos(w * t)
out = abs(T) * np.cos(w * t + np.angle(T))
fig, ax = plt.subplots(figsize=(15, 6.2))
ax.plot(ms, ref, color=NAVY, label="지령 i*", lw=4)
ax.plot(ms, out, color=ORANGE, label="실제 i (PI, 정상상태)", lw=4, ls="--")
ax.fill_between(ms, ref, out, color=ORANGE, alpha=0.15)
ax.set_xlabel("시간 [ms]"); ax.set_ylabel("[pu]"); ax.set_ylim(-1.3, 1.3); ax.set_xlim(0, 33.3)
ax.legend(loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.14))
fig.tight_layout(); save(fig, "L01-PI-추종오차.png")
print("PI |T| = %.3f, angle = %.1f deg" % (abs(T), np.degrees(np.angle(T))))

# 9. 예제 결과: i = cos(ωt − 30°) → abc / αβ / dq
ph = -np.pi / 6
fig, axs = plt.subplots(3, 1, figsize=(15, 9.6), sharex=True)
for p, sh in [("a", 0), ("b", -2 * np.pi / 3), ("c", 2 * np.pi / 3)]:
    axs[0].plot(ms, np.cos(w * t + sh + ph), color=PH[p], label=f"i{p}")
axs[1].plot(ms, np.cos(w * t + ph), color=BLUE, label="iα"); axs[1].plot(ms, np.sin(w * t + ph), color=ORANGE, label="iβ")
axs[2].plot(ms, np.full_like(t, np.cos(ph)), color=BLUE, label="id = 0.866")
axs[2].plot(ms, np.full_like(t, np.sin(ph)), color=ORANGE, label="iq = −0.5")
for ax_, lab in zip(axs, ["abc", "αβ", "dq (θ = ωt)"]):
    ax_.set_ylim(-1.3, 1.3); ax_.set_ylabel(lab, fontsize=24)
    ax_.legend(loc="upper right", ncol=3, bbox_to_anchor=(1.0, 1.28), fontsize=22)
axs[2].set_xlabel("시간 [ms]"); axs[2].set_xlim(0, 33.3)
fig.tight_layout(); save(fig, "L01-예제-3단.png")
print("done")
