"""C01 그림 생성 (저장소 루트에서: python docs/_assets/강좌/scripts/C01_figs.py)."""
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
SHIFT = (0.0, -2 * np.pi / 3, 2 * np.pi / 3)   # a, b, c (정상 상순 abc)
COLORS = (BLUE, ORANGE, AQUA)


def fig_power():
    """3상 파형과 상별 순시전력, 그 합 (V = I = 1 pu 진폭, 역률 0.8 지상)."""
    phi = np.arccos(0.8)
    t = np.linspace(0, 2 / 60, 1000)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True)
    total = np.zeros_like(t)
    for k, (s, c, n) in enumerate(zip(SHIFT, COLORS, "abc")):
        v = np.cos(W * t + s)
        i = np.cos(W * t + s - phi)
        ax1.plot(t * 1e3, v, color=c, label=f"$v_{n}$")
        ax2.plot(t * 1e3, v * i, color=c, label=f"$v_{n} i_{n}$")
        total += v * i
    ax2.plot(t * 1e3, total, color=INK, label=r"합 $p(t)$")
    ax2.text(33.6, 1.32, r"합 = $\frac{3}{2}\cos\varphi$ = 1.2 (일정)" "\n" r"$P = \frac{2}{3}\,p$ = 0.8 pu",
             ha="right", va="bottom", fontsize=9.5)
    ax1.set_ylabel("상전압 [pu]")
    ax1.set_title("평형 3상 상전압 (진폭 1 pu, 상순 a→b→c)")
    ax1.legend(loc="upper right", ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(1, 1.02))
    ax1.set_ylim(-1.2, 1.35)
    ax2.set_ylabel("상별 순시전력 (진폭 곱)")
    ax2.set_xlabel("시간 [ms]")
    ax2.set_title("상별 순시전력은 120 Hz로 맥동하지만 합은 일정 (전류 진폭 1 pu, 역률 0.8 지상)")
    ax2.legend(loc="lower right", ncol=4, fontsize=9, frameon=False)
    ax2.set_ylim(-0.75, 1.75)
    fig.tight_layout()
    fig.savefig(OUT / "C01-3상-순시전력.png", dpi=150)
    plt.close(fig)


def fig_line_voltage():
    """상전압·선간전압 페이저도와 va, vab 파형."""
    Va, Vb, Vc = (np.exp(1j * s) for s in SHIFT)
    Vab = Va - Vb
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [1, 1.4]})
    def arrow(z0, z1, c, ls="-", lw=1.8):
        ax1.annotate("", xy=(z1.real, z1.imag), xytext=(z0.real, z0.imag),
                     arrowprops=dict(arrowstyle="-|>", color=c, lw=lw, ls=ls))
    for z, c, n in ((Va, BLUE, "a"), (Vb, ORANGE, "b"), (Vc, AQUA, "c")):
        arrow(0, z, c)
    arrow(Va, Va - Vb, MUTED, ls="--", lw=1.2)   # -Vb 를 Va 끝에 붙임
    arrow(0, Vab, INK)
    ax1.text(1.05, -0.12, r"$V_a$", color=INK)
    ax1.text(-0.62, -0.98, r"$V_b$", color=INK)
    ax1.text(-0.62, 0.92, r"$V_c$", color=INK)
    ax1.text(1.35, 0.42, r"$-V_b$", color=MUTED, fontsize=9)
    ax1.text(1.2, 1.03, r"$V_{ab}=V_a-V_b=\sqrt{3}\angle 30^\circ$", color=INK, fontsize=9, ha="center")
    arc = np.linspace(0, np.pi / 6, 30)
    ax1.plot(0.55 * np.cos(arc), 0.55 * np.sin(arc), color=MUTED, lw=1)
    ax1.text(0.6, 0.11, "30°", fontsize=9)
    ax1.set_xlim(-1.0, 1.9); ax1.set_ylim(-1.15, 1.15); ax1.set_aspect("equal")
    ax1.axhline(0, color=MUTED, lw=0.6); ax1.axvline(0, color=MUTED, lw=0.6)
    ax1.set_title("페이저도 (진폭 기준, pu)")
    ax1.set_xlabel("실수축 [pu]"); ax1.set_ylabel("허수축 [pu]")
    t = np.linspace(0, 1.25 / 60, 600)
    va = np.cos(W * t)
    vab = va - np.cos(W * t + SHIFT[1])
    ax2.plot(t * 1e3, va, color=BLUE, label=r"$v_a$ (진폭 1)")
    ax2.plot(t * 1e3, vab, color=INK, label=r"$v_{ab}$ (진폭 $\sqrt{3}$ = 1.732)")
    tpk = (1 / 60 - 1 / 720) * 1e3   # vab 최대 시점 (va 최대보다 30° = 1.39 ms 앞섬)
    ax2.annotate("", xy=(tpk, 1.86), xytext=(1e3 / 60, 1.86),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1))
    ax2.text((tpk + 1e3 / 60) / 2, 1.97, "30° (1.39 ms) 앞섬", fontsize=9, ha="center")
    ax2.axhline(1 / np.sqrt(2), color=BLUE, lw=0.9, ls=":")
    ax2.text(3.0, 1 / np.sqrt(2) + 0.06, r"$v_a$ 실효값 $1/\sqrt{2}$ = 0.707", fontsize=8.5, ha="left", color=INK)
    ax2.set_ylim(-2.0, 2.25)
    ax2.set_xlabel("시간 [ms]"); ax2.set_ylabel("전압 [pu]")
    ax2.set_title("상전압과 선간전압 파형")
    ax2.legend(loc="lower right", fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "C01-상전압-선간전압.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_power()
    fig_line_voltage()
    print("saved to", OUT)
