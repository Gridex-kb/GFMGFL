"""C13 EMT 모델링 실습 — 그림 생성 (저장소 루트에서 실행: python docs/_assets/강좌/scripts/C13_figs.py)

스위칭 모델(기본, 5 kHz PWM)과 평균값 모델을 짧게 돌린다. 정상상태는 simulation/emt/.cache 를 재사용하며,
캐시가 없으면 dt 별 초기화(2.5 s)에 각각 수십 초가 더 걸린다.
"""
import logging
import math
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state  # noqa: E402

import matplotlib  # noqa: E402
import matplotlib.ticker  # noqa: E402
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.path.join(ROOT, "docs", "_assets", "강좌")
SURF, INK, INK2, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, VIOLET, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#898781"
plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"], "axes.unicode_minus": False, "mathtext.fontset": "dejavusans",
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "font.size": 9, "lines.linewidth": 1.2, "legend.frameon": False, "legend.fontsize": 8.5,
})
T = 0.2


def fig1():
    """위상 점프 −20° 직후 a상 전류: 스위칭(2 µs) vs 평균값(10 µs), 그리고 100 µs 기록점."""
    jump = lambda t: math.radians(-20) if t >= T else 0.0  # noqa: E731
    p_sw = Params(P_ref=0.5, scr=3.0)
    p_av = Params(P_ref=0.5, scr=3.0, converter="average")
    sc = Scenario(t_end=T + 0.025, grid_phase=jump)
    r_sw = simulate("GFM", p_sw, sc, dt=2e-6, x0=steady_state("GFM", p_sw, dt=2e-6), hires=(T - 0.008, T + 0.025))
    r_av = simulate("GFM", p_av, sc, dt=10e-6, x0=steady_state("GFM", p_av, dt=10e-6), hires=(T - 0.008, T + 0.025))
    hs, ha = r_sw["hires"], r_av["hires"]
    ts, ta = (np.asarray(hs["t"]) - T) * 1e3, (np.asarray(ha["t"]) - T) * 1e3
    tr, ir = (np.asarray(r_sw["t"]) - T) * 1e3, np.asarray(r_sw["ia"])

    fig, ax = plt.subplots(2, 1, figsize=(7.2, 5.4))
    a = ax[0]
    a.plot(ts, hs["ia"], color=BLUE, lw=0.6, label="스위칭 모델 (5 kHz PWM, dt 2 µs)")
    a.plot(ta, ha["ia"], color=ORANGE, lw=1.4, ls="--", label="평균값 모델 (dt 10 µs)")
    a.axvline(0, color=GREY, lw=0.8, ls=":")
    a.set_xlim(-8, 25)
    a.set_ylim(-1.3, 1.35)
    a.set_title("GFM a상 전류, 계통 위상 −20° 점프 전후 [pu]")
    a.set_xlabel("점프 후 시간 [ms]")
    a.legend(loc="upper left")
    b = ax[1]
    m = (ts >= -6.0) & (ts <= -4.0)
    b.plot(ts[m], np.asarray(hs["ia"])[m], color=BLUE, lw=0.8, label="스위칭 모델 순시값 (2 µs)")
    mr = (tr >= -6.0) & (tr <= -4.0)
    b.plot(tr[mr], ir[mr], "o", ms=3.5, color=VIOLET, label="100 µs 기록점 (반송파 꼭짓점)")
    b.set_title("확대: 점프 전 2 ms, 기록점은 리플의 가운데를 지난다 [pu]")
    b.set_xlabel("점프 후 시간 [ms]")
    b.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C13-스위칭-평균값-파형.png"), dpi=150)
    plt.close(fig)


def fig2():
    """정상상태 유효전력 P 스펙트럼: 스위칭 모델의 360 Hz 배수 에일리어싱과 판정 대역."""
    out = {}
    for conv, dt, lab in (("switching", 2e-6, "스위칭 모델 (dt 2 µs)"), ("average", 10e-6, "평균값 모델 (dt 10 µs)")):
        p = Params(P_ref=0.5, scr=3.0, converter=conv)
        r = simulate("GFM", p, Scenario(t_end=0.5), dt=dt, x0=steady_state("GFM", p, dt=dt))
        t, P = np.asarray(r["t"]), np.asarray(r["P"])
        x = P - P.mean()
        F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) * 4.0 / len(x)
        f = np.fft.rfftfreq(len(x), t[1] - t[0])
        out[lab] = (f, F, P.std())
    fig, ax = plt.subplots(1, 1, figsize=(7.2, 3.4))
    for k in range(1, 6):
        ax.axvspan(360 * k - 6, 360 * k + 6, color=GREY, alpha=0.25, lw=0)
    ax.axvspan(5, 300, color=AQUA, alpha=0.08, lw=0)
    for (lab, (f, F, sd)), c in zip(out.items(), (BLUE, ORANGE)):
        ax.semilogy(f, np.maximum(F, 1e-7), color=c, lw=0.9, label=f"{lab}, 표준편차 {sd:.4f} pu")
    ax.text(150, 2e-2, "판정 대역 5~300 Hz", ha="center", fontsize=8, color=INK2)
    ax.text(1080, 2e-2, "360 Hz 배수 ±6 Hz 제외", ha="center", fontsize=8, color=INK2)
    ax.set_xlim(0, 1900)
    ax.set_ylim(1e-6, 1e-1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"1e{int(round(math.log10(v)))}"))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("주파수 [Hz]")
    ax.set_title("정상상태 유효전력 P의 진폭 스펙트럼 [pu]  (GFM, P 0.5 pu, SCR 3, 기록 100 µs)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.86))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C13-스펙트럼-에일리어싱.png"), dpi=150)
    plt.close(fig)


def fig3():
    """GFL 3상 고장 중 PCC 전압: 해석 간격 10 / 5 / 2 µs (스위칭 모델)."""
    p = Params(P_ref=0.8, scr=3.0)
    sc = Scenario(t_end=T + 0.17, grid_v=lambda t: 0.3 if T <= t < T + 0.15 else 1.0)
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw=dict(width_ratios=[1.5, 1]))
    rows = []
    for dt, c in ((10e-6, ORANGE), (5e-6, AQUA), (2e-6, BLUE)):
        r = simulate("GFL", p, sc, dt=dt, x0=steady_state("GFL", p, dt=dt))
        t, V = np.asarray(r["t"]) - T, np.asarray(r["V"])
        m = (t >= 0) & (t < 0.15)
        rows.append((dt, V[m].min(), V[m].mean(), c))
        ax[0].plot(t * 1e3, V, color=c, lw=1.0, label=f"dt {dt * 1e6:g} µs")
    ax[0].set_xlim(-2, 20)
    ax[0].set_title("GFL 고장 직후 PCC 전압 [pu]")
    ax[0].set_xlabel("고장 시작 후 시간 [ms]")
    ax[0].legend(loc="upper right")
    x = np.arange(len(rows))
    w = 0.38
    ax[1].bar(x - w / 2, [r[1] for r in rows], w, color=VIOLET, label="순간 최저")
    ax[1].bar(x + w / 2, [r[2] for r in rows], w, color=GREY, label="구간 평균")
    for i, r in enumerate(rows):
        ax[1].text(i - w / 2, r[1] + 0.02, f"{r[1]:.2f}", ha="center", fontsize=7.5)
        ax[1].text(i + w / 2, r[2] + 0.02, f"{r[2]:.2f}", ha="center", fontsize=7.5)
    ax[1].set_xticks(x, [f"{r[0] * 1e6:g} µs" for r in rows])
    ax[1].set_ylim(0, 0.95)
    ax[1].set_title("고장 150 ms 구간 지표 [pu]")
    ax[1].legend(loc="upper left", ncol=2)
    fig.text(0.99, 0.005, "스위칭 모델, 이 강의용 짧은 실행", ha="right", va="bottom", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(OUT, "C13-해석간격-지표민감도.png"), dpi=150)
    plt.close(fig)
    for dt, vmin, vmean, _ in rows:
        print(f"dt {dt * 1e6:g} us: Vmin {vmin:.3f}  Vmean {vmean:.3f}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3"]
    for k in which:
        {"1": fig1, "2": fig2, "3": fig3}[k]()
    print("saved to", OUT)
