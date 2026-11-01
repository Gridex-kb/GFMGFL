"""C09 그림 생성: P–δ 곡선과 위상 점프 전력, 위상 점프 −20°에서 GFM과 GFL 비교.

저장소 루트에서 실행: python docs/_assets/강좌/scripts/C09_figs.py
평균값 모델(converter="average", dt=10 µs)을 쓴다. CPU 약 25 s (정상상태 캐시가 없을 때).
"""
import math
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state  # noqa: E402

OUT = os.path.join(ROOT, "docs", "_assets", "강좌")
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#898781"
SURF, INK, INK2, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
DT = 10e-6


def setup():
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"], "axes.unicode_minus": False,
        "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.grid": True,
        "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
        "axes.spines.right": False, "axes.labelcolor": INK2, "xtick.color": INK2,
        "ytick.color": INK2, "text.color": INK, "axes.titlesize": 10.5,
        "axes.titleweight": "bold", "axes.titlelocation": "left", "font.size": 9,
        "lines.linewidth": 1.2, "legend.frameon": False, "legend.fontsize": 8.5,
    })
    return plt



def fig_p_delta(plt):
    E = V = 1.0
    X = 0.30 + 1.0 / 3.0          # 가상 리액턴스 Xv + 계통 1/SCR (SCR 3)
    d = np.linspace(0, 180, 361)
    P = E * V / X * np.sin(np.radians(d))
    d0 = math.degrees(math.asin(0.5 * X / (E * V)))
    d1 = d0 + 20.0
    P1 = E * V / X * math.sin(math.radians(d1))
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.plot(d, P, color=BLUE, label="P = (EV/X)·sin δ  (X = 0.633 pu)")
    ax.axhline(0.5, color=GREY, lw=0.8, ls=":")
    ax.plot([d0], [0.5], "o", color=BLUE, ms=5)
    ax.plot([d1], [P1], "o", color=ORANGE, ms=5)
    ax.annotate("", xy=(d1, 0.5), xytext=(d0, 0.5), arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
    ax.annotate("", xy=(d1, P1), xytext=(d1, 0.5), arrowprops=dict(arrowstyle="->", color=ORANGE, lw=0.8))
    ax.text(d0 + 2, 0.34, f"운전점 δ₀ = {d0:.1f}°", ha="left", va="top", color=BLUE, fontsize=8)
    ax.text(d0 + 2, 0.46, "계통 위상 −20° → δ +20°", ha="left", va="top", color=INK2, fontsize=8)
    ax.text(d1 + 3, (0.5 + P1) / 2, f"ΔP ≈ {P1 - 0.5:.2f} pu\n(측정 없이 즉시)", ha="left", va="center",
            color=ORANGE, fontsize=8)
    ax.text(90, E * V / X + 0.03, "Pmax = EV/X", ha="center", va="bottom", color=INK2, fontsize=8)
    ax.set_xlabel("δ = θc − θg [deg]")
    ax.set_ylabel("pu")
    ax.set_title("전력–위상차 곡선 (E = V = 1 pu, SCR 3)")
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.85)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C09-P-델타-곡선.png"), dpi=150)
    plt.close(fig)


def fig_phase_jump(plt):
    p = Params(converter="average")
    t_ev = 0.1
    sc = Scenario(t_end=0.9, grid_phase=lambda t: math.radians(-20) if t >= t_ev else 0.0)
    res = {}
    for mode in ("GFM", "GFL"):
        x0 = steady_state(mode, p, dt=DT)
        res[mode] = simulate(mode, p, sc, dt=DT, x0=x0)
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
    for mode, c in (("GFM", BLUE), ("GFL", ORANGE)):
        r = res[mode]
        t = (np.asarray(r["t"]) - t_ev) * 1e3
        lab = "GFM (VSM)" if mode == "GFM" else "GFL (PLL 20 Hz)"
        ax[0].plot(t, r["P"], color=c, label=lab)
        ax[1].plot(t, r["freq"], color=c, label=lab)
    ax[0].axvspan(0, 10, color=GRID, alpha=0.6, lw=0)
    ax[0].text(16, 0.44, "← 음영: 처음 10 ms", color=INK2, fontsize=8, va="top")
    ax[0].set_title("유효전력 P")
    ax[0].set_ylabel("pu")
    ax[1].set_title("제어기 내부 주파수 (VSM ω / PLL 측정)")
    ax[1].set_ylabel("Hz")
    for a in ax:
        a.set_xlabel("위상 점프(−20°) 후 시간 [ms]")
        a.set_xlim(-50, 800)
    ax[0].legend(loc="upper right")
    ax[1].legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C09-위상점프-GFM-GFL.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plt = setup()
    os.makedirs(OUT, exist_ok=True)
    fig_p_delta(plt)
    fig_phase_jump(plt)
    print("saved C09 figures")
