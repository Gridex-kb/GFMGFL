"""C00 부록 그림 생성 (저장소 루트에서: python docs/_assets/강좌/scripts/C00_figs.py)."""
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


def fig_phasor():
    """페이저도와 시간 파형: V = 1∠0, Z = 0.8 + j0.6 → I = 1∠-36.9°."""
    Z = 0.8 + 0.6j
    V = 1.0 + 0j
    I = V / Z
    phi = np.angle(I)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8), gridspec_kw={"width_ratios": [1, 1.6]})
    # 페이저도
    for z, c, lab in ((V, BLUE, r"$V = 1\angle 0^\circ$"), (I, ORANGE, r"$I = V/Z = 1\angle {-36.9}^\circ$")):
        ax1.annotate("", xy=(z.real, z.imag), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="-|>", color=c, lw=1.8))
        ax1.plot([], [], color=c, label=lab)
    arc = np.linspace(phi, 0, 40)
    ax1.plot(0.35 * np.cos(arc), 0.35 * np.sin(arc), color=MUTED, lw=1)
    ax1.text(0.40, -0.17, r"$\varphi$", color=INK)
    ax1.set_xlim(-0.2, 1.25); ax1.set_ylim(-0.85, 0.6); ax1.set_aspect("equal")
    ax1.axhline(0, color=MUTED, lw=0.8); ax1.axvline(0, color=MUTED, lw=0.8)
    ax1.set_xlabel("실수축 [pu]"); ax1.set_ylabel("허수축 [pu]")
    ax1.set_title("페이저도 (Z = 0.8 + j0.6 pu)")
    ax1.legend(loc="upper left", fontsize=8.5, frameon=False)
    # 시간 파형
    t = np.linspace(0, 1 / 60 * 1.5, 600)
    w = 2 * np.pi * 60
    ax2.plot(t * 1e3, np.abs(V) * np.cos(w * t), color=BLUE, label="v(t)")
    ax2.plot(t * 1e3, np.abs(I) * np.cos(w * t + phi), color=ORANGE, label="i(t)")
    lag_ms = -phi / w * 1e3
    ax2.annotate("", xy=(1e3 / 60 + lag_ms, 1.07), xytext=(1e3 / 60, 1.07),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1))
    ax2.text(1e3 / 60 + lag_ms / 2, 1.13, f"전류가 {lag_ms:.2f} ms 뒤짐", ha="center", fontsize=9)
    ax2.set_ylim(-1.25, 1.3)
    ax2.set_xlabel("시간 [ms]"); ax2.set_ylabel("순시값 [pu]")
    ax2.set_title("같은 신호의 시간 파형 (60 Hz)")
    ax2.legend(loc="lower left", fontsize=8.5, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "C00-페이저-임피던스.png", dpi=150)
    plt.close(fig)


def fig_first_order():
    """1차 지연 계단응답과 크기 응답 (τ = 1 ms)."""
    tau = 1e-3
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.6))
    t = np.linspace(0, 5 * tau, 500)
    y = 1 - np.exp(-t / tau)
    ax1.plot(t * 1e3, y, color=BLUE)
    for n, yy in ((1, 1 - np.exp(-1)), (3, 1 - np.exp(-3))):
        ax1.plot([n, n], [0, yy], color=MUTED, lw=0.8, ls="--")
        ax1.plot([0, n], [yy, yy], color=MUTED, lw=0.8, ls="--")
        ax1.plot(n, yy, "o", color=BLUE, ms=5)
        ax1.text(n + 0.1, yy - 0.08, f"t = {n}τ → {yy*100:.1f} %", fontsize=9)
    ax1.set_xlabel("시간 [ms]"); ax1.set_ylabel("출력 / 입력 계단 크기")
    ax1.set_title(r"계단응답 $1-e^{-t/\tau}$ ($\tau$ = 1 ms)")
    ax1.set_ylim(0, 1.08)
    f = np.logspace(0, 4, 400)
    mag = 20 * np.log10(1 / np.abs(1 + 1j * 2 * np.pi * f * tau))
    fc = 1 / (2 * np.pi * tau)
    ax2.semilogx(f, mag, color=BLUE)
    ax2.plot(fc, -3.01, "o", color=ORANGE, ms=5)
    ax2.text(fc * 1.25, -2.6, f"$f_c = 1/(2\\pi\\tau)$ = {fc:.0f} Hz, -3 dB", fontsize=9)
    ax2.set_xlabel("주파수 [Hz]"); ax2.set_ylabel("크기 [dB]")
    ax2.set_title(r"크기 응답 $|1/(1+j\omega\tau)|$")
    ax2.set_ylim(-40, 3)
    fig.tight_layout()
    fig.savefig(OUT / "C00-1차지연.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_phasor()
    fig_first_order()
    print("saved to", OUT)
