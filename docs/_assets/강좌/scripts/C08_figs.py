"""C08 그림 생성: PLL 대역폭과 위상 점프, GFL 위상 점프 응답, 약계통 FRT 모드 순환.

저장소 루트에서 실행: python docs/_assets/강좌/scripts/C08_figs.py
평균값 모델(converter="average", dt=10 µs)을 쓴다. CPU 약 40 s.
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


def pll_step(f_pll, dphi_deg=-20.0, zeta=0.707, dw_max=0.1, t_end=0.1, h=1e-5):
    """강한 계통(전압 1 pu)에 대한 SRF-PLL 비선형 응답. 위상 점프는 t = 0."""
    wb = 2 * math.pi * 60
    wn = 2 * math.pi * f_pll
    kp, ki = 2 * zeta * wn / wb, wn * wn / wb
    n = int(t_end / h)
    t = np.arange(n) * h
    e_out, f_out = np.zeros(n), np.zeros(n)
    th_err = math.radians(dphi_deg)   # θ_g - θ_c (점프 직후)
    x = 0.0
    for k in range(n):
        vq = math.sin(th_err)
        dw = min(dw_max, max(-dw_max, kp * vq + x))
        if not ((x >= dw_max and vq > 0) or (x <= -dw_max and vq < 0)):
            x += h * ki * vq
        th_err -= h * wb * dw
        e_out[k], f_out[k] = math.degrees(th_err), 60 * (1 + dw)
    return t, e_out, f_out


def fig_pll(plt):
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
    for fp, c, ls in ((10, AQUA, "--"), (20, ORANGE, "-"), (50, BLUE, "-")):
        t, e, f = pll_step(fp)
        ax[0].plot(t * 1e3, e, color=c, ls=ls, label=f"PLL {fp} Hz")
        ax[1].plot(t * 1e3, f, color=c, ls=ls, label=f"PLL {fp} Hz")
    ax[1].axhline(54, color=GREY, lw=0.8, ls=":")
    ax[1].text(98, 54.2, "주파수 제한 54 Hz (−10 %)", ha="right", va="bottom", color=INK2, fontsize=8)
    ax[0].set_title("위상 오차 θg − θc")
    ax[0].set_ylabel("deg")
    ax[1].set_title("PLL 측정 주파수")
    ax[1].set_ylabel("Hz")
    for a in ax:
        a.set_xlabel("위상 점프(−20°) 후 시간 [ms]")
    ax[0].legend(loc="lower right")
    ax[1].legend(loc="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C08-PLL-대역폭.png"), dpi=150)
    plt.close(fig)


def fig_phase_jump(plt):
    p = Params(converter="average")
    x0 = steady_state("GFL", p, dt=DT)
    t_ev = 0.1
    sc = Scenario(t_end=0.35, grid_phase=lambda t: math.radians(-20) if t >= t_ev else 0.0)
    r = simulate("GFL", p, sc, dt=DT, x0=x0)
    t = (np.asarray(r["t"]) - t_ev) * 1e3
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
    ax[0].plot(t, r["P"], color=ORANGE, label="P")
    ax[0].plot(t, r["Q"], color=AQUA, ls="--", label="Q")
    ax[0].set_title("GFL 출력 전력")
    ax[0].set_ylabel("pu")
    ax[0].legend(loc="center right")
    ax[1].plot(t, r["freq"], color=ORANGE)
    ax[1].axhline(54, color=GREY, lw=0.8, ls=":")
    ax[1].set_title("PLL 측정 주파수 (PLL 대역폭 20 Hz)")
    ax[1].set_ylabel("Hz")
    for a in ax:
        a.set_xlabel("위상 점프(−20°) 후 시간 [ms]")
        a.set_xlim(-30, 250)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C08-위상점프-GFL.png"), dpi=150)
    plt.close(fig)


def fig_frt_cycle(plt):
    t_ev = 0.2
    sc = Scenario(t_end=0.8, scr=lambda t: 5.0 if t < t_ev else 1.5)
    res = {}
    for lab, enter in (("FRT 진입 0.85 pu (기본)", 0.85), ("FRT 진입 0.5 pu", 0.5)):
        p = Params(converter="average", scr=5.0, P_ref=0.8, gfl_frt_enter=enter)
        x0 = steady_state("GFL", p, dt=DT)
        res[lab] = simulate("GFL", p, sc, dt=DT, x0=x0)
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
    for (lab, r), c, ls in zip(res.items(), (ORANGE, AQUA), ("-", "--")):
        t = (np.asarray(r["t"]) - t_ev) * 1e3
        ax[0].plot(t, r["V"], color=c, ls=ls, label=lab)
        ax[1].plot(t, r["freq"], color=c, ls=ls, label=lab)
    ax[0].axhline(0.85, color=GREY, lw=0.8, ls=":")
    ax[0].axhline(0.92, color=GREY, lw=0.8, ls=":")
    ax[0].set_title("PCC 전압 |v|")
    ax[0].set_ylabel("pu")
    ax[1].set_title("PLL 측정 주파수")
    ax[1].set_ylabel("Hz")
    for a in ax:
        a.set_xlabel("SCR 5 → 1.5 전환 후 시간 [ms]")
        a.set_xlim(-50, 600)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(OUT, "C08-FRT-순환.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plt = setup()
    os.makedirs(OUT, exist_ok=True)
    fig_pll(plt)
    fig_phase_jump(plt)
    fig_frt_cycle(plt)
    print("saved C08 figures")
