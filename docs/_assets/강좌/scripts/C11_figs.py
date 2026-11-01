"""C11 전류 제한과 고장 — 그림 생성 (저장소 루트에서 실행: python docs/_assets/강좌/scripts/C11_figs.py)

평균값 모델(converter="average"), dt = 10 µs. 프로젝트의 2 µs 스위칭 결과와 수치가 다를 수 있다.
"""
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state  # noqa: E402

import logging  # noqa: E402
import matplotlib  # noqa: E402
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.path.join(ROOT, "docs", "_assets", "강좌")
SURF, INK, INK2, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, VIOLET, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#898781"
plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"], "axes.unicode_minus": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "font.size": 9, "lines.linewidth": 1.3, "legend.frameon": False, "legend.fontsize": 8.5,
})
T, DT = 0.2, 10e-6


def run(mode, sc, **kw):
    p = Params(converter="average", P_ref=0.8, scr=3.0, **kw)
    x0 = steady_state(mode, p, dt=DT)
    r = simulate(mode, p, sc, dt=DT, x0=x0)
    d = {k: np.asarray(v) for k, v in r.items() if isinstance(v, list)}
    d["t"] = d["t"] - T
    return d


def fig1():
    """그리드 고장 0.3 pu × 150 ms: GFM(보정) / GFM(보정 없음) / GFL."""
    sc = Scenario(t_end=1.5, grid_v=lambda t: 0.3 if T <= t < T + 0.15 else 1.0)
    cases = [("GFM (보정: gfm_limit_freeze=True)", "GFM", {}, BLUE, "-"),
             ("GFM (보정 없음: False)", "GFM", dict(gfm_limit_freeze=False), VIOLET, "--"),
             ("GFL (FRT 고정 무효전류)", "GFL", {}, ORANGE, "-")]
    R = [(lab, run(m, sc, **kw), c, ls) for lab, m, kw, c, ls in cases]
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 6.6), sharex=True)
    for lab, r, c, ls in R:
        ax[0].plot(r["t"], r["I"], color=c, ls=ls, label=lab)
        ax[1].plot(r["t"], r["P"], color=c, ls=ls, label=lab)
        if lab.startswith("GFM"):
            d = r["delta_deg"]
            d0 = d[(r["t"] > -0.05) & (r["t"] < 0)].mean()
            ax[2].plot(r["t"], d - d0, color=c, ls=ls, label=lab)
    for a in ax:
        a.axvspan(0, 0.15, color=GREY, alpha=0.12, lw=0)
        a.set_xlim(-0.05, 1.3)
    ax[0].axhline(1.2, color=GREY, lw=0.8, ls=":")
    ax[0].text(1.28, 1.22, "I_max 1.2 pu", ha="right", va="bottom", color=INK2, fontsize=8)
    ax[0].set_title("컨버터측 전류 |i| [pu]")
    ax[1].set_title("유효전력 P [pu]")
    ax[2].set_title("GFM 내부 위상의 계통 대비 변화 Δδ [°]")
    ax[2].set_xlabel("고장 시작 후 시간 [s]  (회색: 계통 전압 0.3 pu 구간)")
    ax[1].legend(loc="lower right")
    ax[2].legend(loc="upper right")
    fig.text(0.99, 0.995, "평균값 모델, dt 10 µs · SCR 3, P₀ 0.8 pu", ha="right", va="top", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(os.path.join(OUT, "C11-보정-유무-고장응답.png"), dpi=150)
    plt.close(fig)


def fig2():
    """PCC 3상 지락 × 200 ms: 전류 정격 1.2 / 2.0 pu."""
    sc = Scenario(t_end=0.6, pcc_fault_g=lambda t: 20.0 if T <= t < T + 0.2 else 0.0)
    cases = [("GFM, I_max 1.2", "GFM", {}, BLUE, "-"), ("GFL, I_max 1.2", "GFL", {}, ORANGE, "-"),
             ("GFM, I_max 2.0", "GFM", dict(I_max=2.0), AQUA, "--"), ("GFL, I_max 2.0", "GFL", dict(I_max=2.0), VIOLET, "--")]
    R = [(lab, run(m, sc, **kw), c, ls) for lab, m, kw, c, ls in cases]
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True)
    for lab, r, c, ls in R:
        ax[0].plot(r["t"] * 1e3, r["I"], color=c, ls=ls, label=lab)
        ax[1].plot(r["t"] * 1e3, r["V"], color=c, ls=ls, label=lab)
    for a in ax:
        a.axvspan(0, 200, color=GREY, alpha=0.12, lw=0)
        a.set_xlim(-30, 400)
    ax[0].axhline(2.0, color=GREY, lw=0.8, ls=":")
    ax[0].annotate("", xy=(140, 2.45), xytext=(0, 2.45), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8))
    ax[0].text(70, 2.5, "연계기준안: 2.0 pu 이상 140 ms", ha="center", va="bottom", fontsize=8, color=INK2)
    ax[0].set_ylim(0, 2.75)
    ax[0].set_title("컨버터측 전류 |i| [pu]")
    ax[1].set_title("PCC 전압 [pu]")
    ax[1].set_xlabel("고장 시작 후 시간 [ms]  (회색: PCC 지락, 고장 컨덕턴스 20 pu)")
    ax[1].set_ylim(0, 1.5)
    ax[1].annotate("제거 순간 스파이크\n(모델 특성, 축 밖)", xy=(200, 1.48), xytext=(120, 1.1), fontsize=7.5,
                   color=INK2, ha="center", arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7))
    ax[1].legend(loc="lower right", ncol=2)
    fig.text(0.99, 0.995, "평균값 모델, dt 10 µs · SCR 3, P₀ 0.8 pu", ha="right", va="top", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(os.path.join(OUT, "C11-전류정격-PCC지락.png"), dpi=150)
    plt.close(fig)


def fig3():
    """개념: dq 평면 원형 포화와 제한 중 전력 상한."""
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw=dict(width_ratios=[1, 1.35]))
    a = ax[0]
    th = np.linspace(0, 2 * np.pi, 300)
    a.plot(1.2 * np.cos(th), 1.2 * np.sin(th), color=GREY, lw=1.0)
    i_req = np.array([1.6, -2.2])
    i_lim = i_req / np.linalg.norm(i_req) * 1.2
    a.annotate("", xy=i_req, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.2, ls="--"))
    a.annotate("", xy=i_lim, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    a.text(i_req[0] + 0.05, i_req[1], "요구 전류 i*\n(고장 시 수 pu)", color=ORANGE, fontsize=8, va="center")
    a.text(i_lim[0] + 0.12, i_lim[1] + 0.25, "제한 후\n(각도 유지)", color=BLUE, fontsize=8)
    a.text(-1.15, 1.32, "|i| = I_max", color=INK2, fontsize=8)
    a.set_xlim(-1.6, 2.6)
    a.set_ylim(-2.5, 1.7)
    a.set_aspect("equal")
    a.set_xlabel("d축 전류 [pu]")
    a.set_ylabel("q축 전류 [pu]")
    a.set_title("원형 포화")
    b = ax[1]
    d = np.linspace(0, 180, 361)
    X = 0.3 + 0.1 + 1 / 3.0   # Xv + Lt + 계통 (개념용 합성 리액턴스)
    for V, c, lab in ((1.0, BLUE, "계통 전압 1.0 pu"), (0.3, ORANGE, "계통 전압 0.3 pu (고장)")):
        b.plot(d, 1.0 * V / X * np.sin(np.radians(d)), color=c, label=lab)
    b.axhline(0.8, color=INK2, lw=0.9, ls="--")
    b.text(178, 0.84, "P* = 0.8 pu", ha="right", fontsize=8, color=INK2)
    b.set_xlim(0, 180)
    b.set_xlabel("내부 기전력과 계통의 위상차 δ [°]")
    b.set_title("전달 가능 전력 P(δ) [pu]  (개념)")
    b.legend(loc="upper left")
    b.text(90, 0.56, "고장 중에는 어떤 δ에서도\nP < P* → 평형점 없음, δ 가속", fontsize=8, color=ORANGE, ha="center")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C11-원형포화-전력상한.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig3()
    fig1()
    fig2()
    print("saved to", OUT)
