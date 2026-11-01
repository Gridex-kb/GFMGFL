"""C10 그림 생성: SCR 급변 시 GFL·GFM 응답, 두 가지 진동 유형, GFM 전력 루프 감쇠와 SCR.

저장소 루트에서 실행: python docs/_assets/강좌/scripts/C10_figs.py
평균값 모델(converter="average", dt=10 µs)을 쓴다. 평균값 모델의 불안정 경계는 스위칭 모델과
다르므로(지연 근사가 다름) 경향만 본다. CPU 약 60 s (정상상태 캐시가 없을 때).
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


T_EV = 0.2


def run_scr(mode, f_pll, scr1, t_end=1.0):
    p = Params(converter="average", scr=5.0, P_ref=0.8, f_pll=f_pll, gfl_frt_enter=0.5)
    x0 = steady_state(mode, p, dt=DT)
    sc = Scenario(t_end=t_end, scr=lambda t: 5.0 if t < T_EV else scr1)
    return simulate(mode, p, sc, dt=DT, x0=x0)


def tms(r):
    return (np.asarray(r["t"]) - T_EV) * 1e3


def fig_scr_step(plt):
    cases = [("GFM (VSM)", "GFM", 20, BLUE, "-"), ("GFL · PLL 대역폭 20 Hz", "GFL", 20, ORANGE, "-"),
             ("GFL · PLL 대역폭 50 Hz", "GFL", 50, AQUA, "-")]
    res = [(lab, run_scr(m, fp, 1.5, 0.8), c, ls) for lab, m, fp, c, ls in cases]
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    for lab, r, c, ls in res:
        ax.plot(tms(r), r["P"], color=c, ls=ls, label=lab)
    ax.set_title("유효전력 P (SCR 5 → 1.5, P* = 0.8 pu)")
    ax.set_xlim(-50, 600)
    ax.set_xlabel("SCR 전환 후 시간 [ms]")
    ax.set_ylabel("pu")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C10-SCR-급변.png"), dpi=150)
    plt.close(fig)


def fig_osc_types(plt):
    r1 = run_scr("GFL", 10, 1.3, 0.8)
    r2 = run_scr("GFL", 50, 1.5, 0.8)
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
    ax[0].plot(tms(r1), r1["P"], color=ORANGE)
    ax[0].set_title("① 동기화 상실형: PLL 대역폭 10 Hz, SCR 1.3")
    ax[0].set_xlim(-50, 600)
    ax[1].plot(tms(r2), r2["P"], color=AQUA)
    ax[1].set_title("② 상호작용형: PLL 대역폭 50 Hz, SCR 1.5")
    ax[1].set_xlim(400, 460)
    ax[1].set_ylim(0.72, 0.88)
    for a in ax:
        a.set_xlabel("SCR 전환 후 시간 [ms]")
        a.set_ylabel("P [pu]")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C10-진동-유형.png"), dpi=150)
    plt.close(fig)


def fig_gfm_damping(plt):
    """선형화한 VSM 전력 루프: 2H s² Δδ/ωb + D s Δδ/ωb + Ks Δδ = 0, Ks = EV/(Xv + 1/SCR)."""
    H, D, wb = 4.0, 50.0, 2 * math.pi * 60
    scr = np.linspace(1.0, 20.0, 200)
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
    for xv, c, ls in ((0.30, BLUE, "-"), (0.10, AQUA, "--"), (0.03, INK2, ":")):
        ks = 1.0 / (xv + 1.0 / scr)
        wn = np.sqrt(wb * ks / (2 * H))
        zeta = D / (4 * H * wn)
        ax[0].plot(scr, zeta, color=c, ls=ls, label=f"Xv = {xv:.2f} pu")
        ax[1].plot(scr, wn / (2 * math.pi), color=c, ls=ls, label=f"Xv = {xv:.2f} pu")
    ax[0].set_title("전력 루프 감쇠비 ζ")
    ax[0].set_ylabel("ζ")
    ax[1].set_title("전력 루프 고유주파수")
    ax[1].set_ylabel("Hz")
    for a in ax:
        a.set_xlabel("SCR")
        a.set_xlim(1, 20)
    ax[0].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C10-GFM-감쇠-SCR.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plt = setup()
    os.makedirs(OUT, exist_ok=True)
    fig_gfm_damping(plt)
    fig_scr_step(plt)
    fig_osc_types(plt)
    print("saved C10 figures")
