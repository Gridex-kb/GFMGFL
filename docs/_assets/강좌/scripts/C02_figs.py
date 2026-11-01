"""C02 그림 생성 (저장소 루트에서: python docs/_assets/강좌/scripts/C02_figs.py)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[1]
BLUE, ORANGE, AQUA, INK, MUTED, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#222222", "#8a8a86", "#fcfcfb"
plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"], "axes.unicode_minus": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "lines.linewidth": 1.5, "axes.edgecolor": MUTED, "axes.grid": True,
    "grid.color": "#e4e4e0", "grid.linewidth": 0.6, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})
W = 2 * np.pi * 60
A = np.exp(2j * np.pi / 3)


def clarke(xa, xb, xc):
    """진폭 불변 Clarke: x = (2/3)(xa + a·xb + a²·xc)."""
    return (2 / 3) * (xa + A * xb + A**2 * xc)


def fig_rotation():
    """αβ 평면에서 회전하는 공간벡터와 함께 도는 dq 축 (정지 그림 3장)."""
    angles = (0, 50, 130)
    fig, axs = plt.subplots(1, 3, figsize=(11, 4.0))
    for ax, deg in zip(axs, angles):
        th = np.radians(deg)
        va, vb, vc = np.cos(th), np.cos(th - 2 * np.pi / 3), np.cos(th + 2 * np.pi / 3)
        v = clarke(va, vb, vc)
        for k, n in enumerate("abc"):
            ang = 2 * np.pi / 3 * k
            ax.plot([0, 1.3 * np.cos(ang)], [0, 1.3 * np.sin(ang)], color=MUTED, lw=0.8, ls=":")
            ax.text(1.42 * np.cos(ang), 1.42 * np.sin(ang), f"{n}축", ha="center", va="center",
                    fontsize=8.5, color=MUTED)
        circ = np.linspace(0, 2 * np.pi, 200)
        ax.plot(np.cos(circ), np.sin(circ), color="#d8d8d4", lw=0.8)
        ax.plot([0, 1.3 * np.cos(th)], [0, 1.3 * np.sin(th)], color=ORANGE, lw=1.5, label="d축 (θ = ωt)")
        ax.plot([0, 1.3 * np.cos(th + np.pi / 2)], [0, 1.3 * np.sin(th + np.pi / 2)], color=AQUA, lw=1.5,
                label="q축 (θ + 90°)")
        ax.annotate("", xy=(v.real, v.imag), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.2))
        ax.plot([], [], color=BLUE, lw=2.2, label=r"공간벡터 $\vec v$")
        ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_aspect("equal")
        ax.set_xlabel("α [pu]"); ax.set_ylabel("β [pu]")
        vdq = v * np.exp(-1j * th)
        ax.set_title(f"ωt = {deg}°\n$v_a$={va:.2f}, $v_b$={vb:.2f}, $v_c$={vc:.2f}\n"
                     f"$v_d$={vdq.real:.2f}, $v_q$={abs(vdq.imag):.2f}", fontsize=9.5)
    axs[0].legend(loc="lower left", fontsize=8, frameon=True, framealpha=0.9, edgecolor="none")
    fig.tight_layout()
    fig.savefig(OUT / "C02-공간벡터-회전.png", dpi=150)
    plt.close(fig)


def fig_waveforms():
    """abc → αβ → dq. 25 ms에 진폭 1 → 0.7, 50 ms에 위상 +30°."""
    t = np.linspace(0, 0.075, 3000)
    amp = np.where(t < 0.025, 1.0, 0.7)
    ph = np.where(t < 0.05, 0.0, np.radians(30))
    va = amp * np.cos(W * t + ph)
    vb = amp * np.cos(W * t + ph - 2 * np.pi / 3)
    vc = amp * np.cos(W * t + ph + 2 * np.pi / 3)
    v = clarke(va, vb, vc)
    vdq = v * np.exp(-1j * W * t)       # θ = ωt (60 Hz로 도는 기준)
    ms = t * 1e3
    fig, axs = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    for x, c, n in ((va, BLUE, "a"), (vb, ORANGE, "b"), (vc, AQUA, "c")):
        axs[0].plot(ms, x, color=c, label=f"$v_{n}$")
    axs[1].plot(ms, v.real, color=BLUE, label=r"$v_\alpha$")
    axs[1].plot(ms, v.imag, color=ORANGE, label=r"$v_\beta$")
    axs[2].plot(ms, vdq.real, color=BLUE, label=r"$v_d$")
    axs[2].plot(ms, vdq.imag, color=ORANGE, label=r"$v_q$")
    titles = ("① abc: 60 Hz 정현파 세 개",
              "② αβ (Clarke): 정현파 두 개, 서로 90° 차이",
              r"③ dq (Park, θ = ωt): 직류. 진폭은 $|v_{dq}|$, 위상은 $\angle v_{dq}$ 에 나타남")
    for ax, ttl in zip(axs, titles):
        ax.set_title(ttl, fontsize=10, loc="left")
        ax.set_ylabel("전압 [pu]")
        ax.set_ylim(-1.25, 1.25)
        ax.axvline(25, color=MUTED, lw=0.8, ls="--")
        ax.axvline(50, color=MUTED, lw=0.8, ls="--")
        ax.legend(loc="upper right", ncol=3, fontsize=8.5, frameon=True, framealpha=0.9, edgecolor="none")
    axs[2].text(12.5, 0.9, "$v_d$ = 1.0", ha="center", va="top", fontsize=9)
    axs[2].text(37.5, 0.6, "$v_d$ = 0.7", ha="center", va="top", fontsize=9)
    axs[2].text(62.5, 0.66, "$v_d$ = 0.7cos30° = 0.61", ha="center", va="bottom", fontsize=9)
    axs[2].text(62.5, 0.29, "$v_q$ = 0.7sin30° = 0.35", ha="center", va="top", fontsize=9)
    axs[0].text(25.5, -1.18, "진폭 1→0.7", fontsize=8.5, color=INK)
    axs[0].text(50.5, -1.18, "위상 +30°", fontsize=8.5, color=INK)
    axs[2].set_xlabel("시간 [ms]")
    fig.tight_layout()
    fig.savefig(OUT / "C02-abc-ab-dq.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_rotation()
    fig_waveforms()
    print("saved to", OUT)
