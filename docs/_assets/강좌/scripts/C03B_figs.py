"""C03B-3레벨-컨버터 그림 생성. 저장소 루트에서 실행: python docs/_assets/강좌/scripts/C03B_figs.py"""
import os
import itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 1.0, "font.size": 10,
})
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#888888"
OUT = os.path.join("docs", "_assets", "강좌")
VDC = 2.256
A = np.exp(2j * np.pi / 3)
NAME = {1: "P", 0: "O", -1: "N"}

# ---- 그림 1: 27개 상태의 전압 벡터도 ----
groups = {}
for s in itertools.product((1, 0, -1), repeat=3):
    v = (2 / 3) * (VDC / 2) * (s[0] + s[1] * A + s[2] * A ** 2)
    key = (round(v.real, 6), round(v.imag, 6))
    groups.setdefault(key, []).append("".join(NAME[k] for k in s))

def cls(v):
    m = abs(v)
    if m < 1e-6: return "zero"
    if abs(m - VDC / 3) < 1e-3: return "small"
    if abs(m - VDC / np.sqrt(3)) < 1e-3: return "medium"
    return "large"

style = {"large": (BLUE, f"대벡터 6개 (|V| = 2/3·$V_{{dc}}$ = {2*VDC/3:.3f} pu)"),
         "medium": (ORANGE, "중벡터 6개 (|V| = $V_{dc}/\\sqrt{3}$ ≈ 1.302 pu)"),
         "small": (AQUA, f"소벡터 6개 × 상태 2개 (|V| = $V_{{dc}}$/3 = {VDC/3:.3f} pu)"),
         "zero": (GRAY, "영벡터 1개 × 상태 3개")}
fig, ax = plt.subplots(figsize=(7.0, 6.6))
# 대벡터 육각형과 내부 삼각형 격자
lg = [k for k in groups if cls(complex(*k)) == "large"]
lg = sorted(lg, key=lambda k: np.angle(complex(*k)))
hexv = np.array([complex(*k) for k in lg + [lg[0]]])
ax.plot(hexv.real, hexv.imag, color=BLUE, lw=0.8)
pts = [complex(*k) for k in groups]
for p1, p2 in itertools.combinations(pts, 2):
    if abs(abs(p1 - p2) - VDC / 3) < 1e-3:
        ax.plot([p1.real, p2.real], [p1.imag, p2.imag], color=GRAY, lw=0.4, alpha=0.6, zorder=0)
seen = set()
for key, names in groups.items():
    v = complex(*key)
    c = cls(v)
    col, lab = style[c]
    ax.plot(v.real, v.imag, "o", color=col, ms=7 if c != "zero" else 8,
            label=lab if c not in seen else None, zorder=3)
    seen.add(c)
    txt = "\n".join(names)
    if c == "zero":
        ax.text(0.10, -0.06, txt, fontsize=7.5, va="top", ha="left")
        continue
    u = v / abs(v)
    d = {"large": 0.30, "medium": 0.30, "small": 0.24}[c]
    rot = np.exp(1j * np.deg2rad(-28)) if c == "small" else 1
    q = v + u * rot * d
    ax.text(q.real, q.imag, txt, fontsize=7.5, ha="center", va="center", color="#222222")
ax.set_aspect("equal")
ax.set_xlim(-2.1, 2.1); ax.set_ylim(-1.95, 2.25)
ax.set_xlabel("α [pu]"); ax.set_ylabel("β [pu]")
ax.axhline(0, color=GRAY, lw=0.4); ax.axvline(0, color=GRAY, lw=0.4)
ax.set_title("3레벨 NPC: 상태 27개 → 서로 다른 전압 벡터 19개 ($V_{dc}$ = 2.256 pu)", fontsize=10)
ax.legend(loc="upper left", fontsize=7.5, frameon=False, ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C03B-전압벡터도.png"), dpi=150)
plt.close(fig)

# ---- 그림 2: 같은 반송파(5 kHz), 같은 지령(1.0 pu)에서 2레벨 vs 3레벨 파형 ----
f0, fsw = 60.0, 5000.0
dt = 1e-6
t = np.arange(0, 1 / f0, dt)
Ts = 1 / (2 * fsw)
tk = np.floor(t / Ts) * Ts                        # 꼭짓점 샘플 시각 (2회 갱신)
vm = 1.0
ref = np.stack([vm * np.cos(2 * np.pi * f0 * tk - k * 2 * np.pi / 3) for k in range(3)], axis=1)
v0 = -0.5 * (ref.max(axis=1) + ref.min(axis=1))   # min-max 영상분 주입
d = np.clip((ref + v0[:, None]) / (VDC / 2), -1, 1)
ph = (t * fsw) % 1.0
car = np.where(ph < 0.5, 4 * ph - 1, 3 - 4 * ph)  # -1..1, t=0 에서 골
s2 = np.where(d > car[:, None], 1, -1)            # 2레벨
cu, cl = (car + 1) / 2, (car - 1) / 2             # 3레벨 PD 반송파 (위·아래)
s3 = (d > cu[:, None]).astype(int) - (d < cl[:, None]).astype(int)
tm = t * 1e3
fig, axs = plt.subplots(2, 2, figsize=(8.6, 5.6), sharex=True)
for j, (s, nm) in enumerate(((s2, "2레벨"), (s3, "3레벨 NPC"))):
    vp = s * VDC / 2
    axs[0, j].plot(tm, vp[:, 0], color=BLUE, lw=0.5, label="a상 극전압")
    axs[0, j].plot(tm, ref[:, 0] + v0, color=ORANGE, lw=1.2, label="변조파 (영상분 포함)")
    axs[0, j].set_title(f"{nm}: 극전압 {len(np.unique(s[:, 0]))}레벨", fontsize=10)
    vab = vp[:, 0] - vp[:, 1]
    axs[1, j].plot(tm, vab, color=BLUE, lw=0.5, label="선간전압 $v_{ab}$")
    axs[1, j].plot(tm, np.sqrt(3) * vm * np.cos(2 * np.pi * f0 * t + np.pi / 6), color=ORANGE, lw=1.2,
                   label="기본파")
    axs[1, j].set_title(f"{nm}: 선간전압 {len(np.unique(vab.round(6)))}레벨", fontsize=10)
    axs[1, j].set_xlabel("시간 [ms]")
    axs[0, j].set_ylim(-1.5, 1.9); axs[1, j].set_ylim(-2.9, 3.4)
    axs[0, j].set_yticks([-VDC / 2, 0, VDC / 2])
    axs[1, j].set_yticks([-VDC, -VDC / 2, 0, VDC / 2, VDC])
    for a in axs[:, j]:
        a.legend(loc="upper right", fontsize=7.5, ncol=2, frameon=False)
        a.set_yticklabels([f"{v:.3f}" for v in a.get_yticks()])
axs[0, 0].set_ylabel("극전압 [pu]"); axs[1, 0].set_ylabel("선간전압 [pu]")
fig.suptitle("같은 반송파(5 kHz)·같은 지령(상전압 진폭 1.0 pu)에서 출력 파형", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "C03B-2레벨-3레벨-파형.png"), dpi=150)
plt.close(fig)
print("saved")
