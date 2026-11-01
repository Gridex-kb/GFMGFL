"""
GFM vs GFL EMT 시나리오 실행 + 그래프/요약 생성

사용법:
    python run_scenarios.py              # 전체 시나리오 (약 2~4분, 4코어)
    python run_scenarios.py --quick      # 안정도 맵 축소판
    python run_scenarios.py --no-slides  # 슬라이드 데이터 갱신 생략

출력:
    results/fig*.png          그래프
    results/summary.md        핵심 지표 표
    results/emt_results.json  다운샘플 데이터 (슬라이드용)
    ../../slides/gfm-gfl-slides.html 의 EMT_DATA 블록 갱신
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gfm_gfl_emt import DT_DEFAULT, Params, Scenario, simulate, steady_state  # noqa: E402

RES = os.path.join(HERE, "results")
SLIDES = os.path.normpath(os.path.join(HERE, "..", "..", "slides", "gfm-gfl-slides.html"))
T_EV = 0.2  # 외란 시각 (웜스타트 이후)

# ---------------------------------------------------------------------------
# 색·스타일 (dataviz 기준 팔레트, 범주 슬롯 1~3 + 무채색 기준선)
# ---------------------------------------------------------------------------
C = {
    "GFM": "#2a78d6",      # slot 1 blue
    "GFL": "#eb6834",      # slot 2 orange
    "GFL+SI": "#1baf7a",   # slot 3 aqua (대비 < 3:1 → 점선 + 직접 라벨)
    "GFM (보정 없음)": "#6250d6",
    "ref": "#898781",
}
LS = {"GFM": "-", "GFL": "-", "GFL+SI": "--", "GFM (보정 없음)": ":"}
INK, INK2, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7", "#fcfcfb"


def setup_mpl():
    import logging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": ["WenQuanYi Zen Hei", "Noto Sans CJK KR", "NanumGothic",
                        "Malgun Gothic", "AppleGothic", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.titlesize": 11, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "font.size": 9, "lines.linewidth": 1.5,
        "legend.frameon": False, "legend.fontsize": 8.5,
    })
    return plt


def arr(r, k):
    return np.asarray(r[k], dtype=float)


# ---------------------------------------------------------------------------
# 시뮬레이션 실행 헬퍼 (프로세스 풀용 최상위 함수)
# ---------------------------------------------------------------------------
DT = DT_DEFAULT  # main() 에서 --dt 로 바꿀 수 있음 (자식 프로세스에는 job 으로 전달)


def _init(args):
    mode, pkw, dt = args
    try:
        steady_state(mode, Params(**pkw), dt=dt)
    except RuntimeError:
        pass
    return True


def _run(job):
    mode, pkw, skw, label, dt = job
    p = Params(**pkw)
    try:
        x0 = steady_state(mode, p, dt=dt)
    except RuntimeError:
        return label, None
    events = make_events(**skw)
    sc = Scenario(**events)
    r = simulate(mode, p, sc, x0=x0, dt=dt)
    r.pop("x_final", None)
    return label, r


def make_events(kind, t_end=1.2, **kw):
    """피클 가능한 형태로 시나리오를 만들기 위해 종류 문자열로 생성."""
    ev = dict(name=kind, t_end=t_end)
    if kind == "phase_jump":
        dphi = math.radians(kw.get("deg", -20.0))
        ev["grid_phase"] = lambda t, d=dphi: d if t >= T_EV else 0.0
    elif kind == "rocof":
        rate = kw.get("rate_hz_s", -1.0) / 60.0
        dur = kw.get("dur", 0.5)
        ev["grid_f"] = lambda t, a=rate, T=dur: 1.0 + a * min(max(t - T_EV, 0.0), T)
    elif kind == "scr_step":
        s0, s1 = kw.get("scr0", 5.0), kw["scr1"]
        ev["scr"] = lambda t, a=s0, b=s1: a if t < T_EV else b
    elif kind == "fault":
        vr, dur = kw.get("v_res", 0.3), kw.get("dur", 0.15)
        ev["grid_v"] = lambda t, v=vr, T=dur: v if T_EV <= t < T_EV + T else 1.0
    elif kind == "island":
        ev["breaker_closed"] = lambda t: t < T_EV
    return ev


def run_jobs(jobs, workers, dt=None):
    """같은 초기 상태를 쓰는 작업이 많으므로 정상상태를 먼저 병렬 계산(캐시)한 뒤 외란을 돌린다."""
    dt = dt or DT
    uniq = {}
    for mode, pkw, _, _ in jobs:
        uniq[(mode, tuple(sorted(pkw.items())))] = (mode, pkw, dt)
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_init, uniq.values()))
        for label, r in ex.map(_run, [(*j, dt) for j in jobs]):
            out[label] = r
    return out


# ---------------------------------------------------------------------------
# 그래프
# ---------------------------------------------------------------------------
def stacked(plt, results, panels, title, fname, xlim=None, refs=None, label_end=True):
    """panels: [(키, y라벨), ...]. 한 패널 = 한 축 (이중축 없음)."""
    n = len(panels)
    fig, axes = plt.subplots(n, 1, figsize=(7.2, 1.55 * n + 0.6), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, (key, ylabel) in zip(axes, panels):
        for label, r in results.items():
            if r is None:
                continue
            t = arr(r, "t") - T_EV
            ax.plot(t, arr(r, key), color=C[label], ls=LS.get(label, "-"), label=label)
        if refs and key in refs:
            rt, ry, rl = refs[key]
            ax.plot(rt, ry, color=C["ref"], ls="--", lw=1.2, label=rl)
        ax.set_ylabel(ylabel)
        ax.axvline(0, color=AXIS, lw=0.8)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", bbox_to_anchor=(0.995, 0.955), ncol=4)
    axes[-1].set_xlabel("외란 후 시간 [s]")
    if xlim:
        axes[-1].set_xlim(*xlim)
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(RES, fname), dpi=140)
    plt.close(fig)


def waveforms(plt, results, fname, title, win=(-0.03, 0.06)):
    labels = [k for k in results if results[k] is not None]
    fig, axes = plt.subplots(len(labels), 1, figsize=(7.2, 1.9 * len(labels) + 0.5), sharex=True)
    phase_c = ["#2a78d6", "#eb6834", "#1baf7a"]
    for ax, label in zip(np.atleast_1d(axes), labels):
        r = results[label]
        t = arr(r, "t") - T_EV
        m = (t >= win[0]) & (t <= win[1])
        for ph, col, ls in zip(("ia", "ib", "ic"), phase_c, ("-", "-", "--")):
            ax.plot(t[m] * 1000, arr(r, ph)[m], color=col, ls=ls, lw=1.3, label=ph.replace("i", "i_"))
        ax.set_ylabel(f"{label}\n상전류 [pu]")
        ax.axvline(0, color=AXIS, lw=0.8)
    h, l = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", bbox_to_anchor=(0.995, 0.955), ncol=3)
    np.atleast_1d(axes)[-1].set_xlabel("외란 후 시간 [ms]")
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(RES, fname), dpi=140)
    plt.close(fig)


def stability_map(plt, table, scrs, rows, fname):
    fig, ax = plt.subplots(figsize=(7.2, 0.55 * len(rows) + 1.3))
    ax.set_xlim(0, len(scrs))
    ax.set_ylim(0, len(rows))
    ax.invert_yaxis()
    ax.axis("off")
    good, bad = "#0ca30c", "#d03b3b"
    for j, s in enumerate(scrs):
        ax.text(j + 0.5, -0.25, f"SCR {s}", ha="center", va="bottom", color=INK2, fontsize=9)
    for i, row in enumerate(rows):
        ax.text(-0.08, i + 0.5, row, ha="right", va="center", color=INK, fontsize=9)
        for j, s in enumerate(scrs):
            ok = table[(row, s)]
            col = good if ok else bad
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.08), 0.92, 0.84, color=col, alpha=0.14, lw=0))
            ax.text(j + 0.5, i + 0.5, ("✓ 안정" if ok else "✗ 불안정"), ha="center", va="center",
                    color=("#006300" if ok else "#b02a2a"), fontsize=9, fontweight="bold")
    fig.suptitle("약계통 안정도 맵 — SCR 5에서 목표 SCR로 급변(선로 트립), P = 0.8 pu, 1.8 s 관찰",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.subplots_adjust(left=0.22, right=0.99, top=0.80, bottom=0.03)
    fig.savefig(os.path.join(RES, fname), dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 지표
# ---------------------------------------------------------------------------
def window(r, key, a, b):
    t = arr(r, "t") - T_EV
    m = (t >= a) & (t < b)
    return arr(r, key)[m]


def is_stable(r, a=0.8):
    """a 이후를 두 구간으로 나눠 진동이 작거나 감쇠 중이면 안정으로 본다."""
    if r is None or "diverged_at" in r:
        return False
    t_end = arr(r, "t")[-1] - T_EV
    mid = a + 0.5 * (t_end - a)
    s1 = window(r, "P", a, mid).std()
    s2 = window(r, "P", mid, 99).std()
    f = window(r, "freq", a, 99)
    damped = s2 < 0.005 or (s2 < 0.03 and s2 < 0.7 * s1)
    return damped and bool(np.all(np.abs(f - 60.0) < 1.5))


def sync_kept(r, p0):
    """고장 후 동기 유지 판정: 위상 이탈 < 90°, 마지막 0.2 s 의 P 가 지령 ±10 %."""
    if r is None or "diverged_at" in r:
        return False
    d = arr(r, "delta_deg")
    d0 = window(r, "delta_deg", -0.05, 0).mean()
    dd = (d - d0 + 180) % 360 - 180
    P_end = window(r, "P", arr(r, "t")[-1] - T_EV - 0.2, 99).mean()
    return bool(np.abs(dd).max() < 90 and abs(P_end - p0) < 0.1 * p0)


def downsample(r, keys, t0=-0.05, t1=None, n=1000):
    t = arr(r, "t") - T_EV
    t1 = t[-1] if t1 is None else t1
    grid = np.linspace(t0, t1, n)
    d = {"t": np.round(grid, 4).tolist()}
    for k in keys:
        d[k] = np.round(np.interp(grid, t, arr(r, k)), 3).tolist()
    return d


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--no-slides", action="store_true")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--dt", type=float, default=DT_DEFAULT, help="해석 시간 간격 [s] (기본 1e-6)")
    args = ap.parse_args()
    global DT
    DT = args.dt
    print(f"해석 시간 간격 dt = {DT * 1e6:g} µs", flush=True)
    os.makedirs(RES, exist_ok=True)
    plt = setup_mpl()
    summary, data = [], {}

    # 1) 위상 점프 ---------------------------------------------------------
    pj = run_jobs([(m, dict(scr=3.0, P_ref=0.5), dict(kind="phase_jump", deg=-20.0, t_end=1.2), m)
                   for m in ("GFL", "GFM")], args.workers)
    stacked(plt, pj, [("P", "P [pu]"), ("Q", "Q [pu]"), ("I", "|i| [pu]"), ("freq", "주파수 [Hz]")],
            "위상 점프 −20° (SCR 3, P₀ = 0.5 pu)", "fig01_phase_jump.png", xlim=(-0.05, 1.0))
    waveforms(plt, pj, "fig02_phase_jump_waveforms.png", "위상 점프 순간의 순시 상전류 (EMT 파형)")
    for m, r in pj.items():
        dP = window(r, "P", 0, 0.01).max() - 0.5
        summary.append(("위상 점프 −20°", m, f"10 ms 내 ΔP 최대 {dP:+.2f} pu",
                        f"최대 전류 {window(r, 'I', 0, 0.5).max():.2f} pu"))
    data["phase_jump"] = {m: downsample(r, ["P", "Q", "I", "freq"], t1=1.0) for m, r in pj.items()}
    data["phase_jump_wave"] = {m: downsample(r, ["ia", "ib", "ic"], -0.03, 0.06, 500) for m, r in pj.items()}

    # 2) RoCoF -------------------------------------------------------------
    jobs = [("GFL", dict(scr=5.0, P_ref=0.3, gfl_droop=True), dict(kind="rocof", t_end=2.0), "GFL"),
            ("GFL", dict(scr=5.0, P_ref=0.3, gfl_droop=True, gfl_H_syn=4.0), dict(kind="rocof", t_end=2.0), "GFL+SI"),
            ("GFM", dict(scr=5.0, P_ref=0.3), dict(kind="rocof", t_end=2.0), "GFM")]
    rc = run_jobs(jobs, args.workers)
    any_r = rc["GFM"]
    stacked(plt, rc, [("grid_freq", "계통 주파수 [Hz]"), ("P", "P [pu]"), ("freq", "인버터 주파수 [Hz]")],
            "주파수 램프 −1 Hz/s × 0.5 s (SCR 5, P₀ = 0.3 pu, 드룹 2 %, H = H_syn = 4 s)",
            "fig03_rocof.png", xlim=(-0.1, 1.6))
    theo = 2 * 4.0 * (1.0 / 60.0)
    for m, r in rc.items():
        p1 = window(r, "P", 0.245, 0.255).mean() - 0.3
        p2 = window(r, "P", 0.495, 0.505).mean() - 0.3
        summary.append(("RoCoF −1 Hz/s", m, f"ΔP: 램프 0.25 s {p1:+.3f} pu, 0.5 s {p2:+.3f} pu",
                        f"이론 관성분 2H·RoCoF/f₀ = {theo:.3f} pu"))
    data["rocof"] = {m: downsample(r, ["grid_freq", "P", "freq"], -0.1, 1.6) for m, r in rc.items()}

    # 3) 약계통 (선로 트립 SCR 5 → 1.5) ------------------------------------
    wg = run_jobs([(m, dict(scr=5.0, P_ref=0.8, f_pll=35.0, gfl_frt_enter=0.5), dict(kind="scr_step", scr1=1.5, t_end=1.6), m)
                   for m in ("GFL", "GFM")], args.workers)
    # 웜스타트 파라미터는 SCR 5, 시나리오가 1.5로 바꾼다
    stacked(plt, wg, [("P", "P [pu]"), ("V", "|V_PCC| [pu]"), ("I", "|i| [pu]")],
            "선로 트립: SCR 5 → 1.5 (P = 0.8 pu, GFL PLL 35 Hz)", "fig04_weak_grid.png", xlim=(-0.05, 1.4))
    for m, r in wg.items():
        summary.append(("SCR 5→1.5 (PLL 35 Hz)", m, "안정" if is_stable(r, 0.6) else "불안정(지속 진동)",
                        f"P 표준편차(1.0 s~) {window(r, 'P', 1.0, 99).std():.3f} pu"))
    data["weak_grid"] = {m: downsample(r, ["P", "V", "I"], t1=1.4, n=1600) for m, r in wg.items()}

    # 4) 안정도 맵 ---------------------------------------------------------
    scrs = [5.0, 3.0, 2.0, 1.5, 1.3, 1.2] if not args.quick else [3.0, 1.5]
    rows = {"GFL · PLL 10 Hz": ("GFL", 10.0), "GFL · PLL 35 Hz": ("GFL", 35.0),
            "GFL · PLL 50 Hz": ("GFL", 50.0), "GFM · VSM": ("GFM", 20.0)}
    jobs = []
    for row, (m, fp) in rows.items():
        for s in scrs:
            # FRT 진입을 0.5 pu 로 낮춰 FRT 모드 순환을 배제하고 소신호(PLL) 안정도만 비교
            jobs.append((m, dict(scr=5.0, P_ref=0.8, f_pll=fp, gfl_frt_enter=0.5),
                         dict(kind="scr_step", scr1=s, t_end=2.0), (row, s)))
    mp = run_jobs(jobs, args.workers)
    table = {k: is_stable(v, 0.9) for k, v in mp.items()}
    stability_map(plt, table, scrs, list(rows), "fig05_stability_map.png")
    data["stability_map"] = {"scr": scrs, "rows": list(rows),
                             "ok": [[bool(table[(r, s)]) for s in scrs] for r in rows]}

    # 5) 고장 (계통 전압 0.3 pu, 150 ms) -----------------------------------
    jobs = [("GFL", dict(scr=3.0, P_ref=0.8), dict(kind="fault", t_end=1.5), "GFL"),
            ("GFM", dict(scr=3.0, P_ref=0.8), dict(kind="fault", t_end=1.5), "GFM"),
            ("GFM", dict(scr=3.0, P_ref=0.8, gfm_limit_freeze=False), dict(kind="fault", t_end=1.5),
             "GFM (보정 없음)")]
    ft = run_jobs(jobs, args.workers)
    stacked(plt, ft, [("V", "|V_PCC| [pu]"), ("I", "|i| [pu]"), ("P", "P [pu]"), ("Q", "Q [pu]"),
                      ("delta_deg", "계통 대비 위상 [°]")],
            "3상 고장: 계통 전압 0.3 pu × 150 ms (SCR 3, P₀ = 0.8 pu, I_max = 1.2 pu)",
            "fig06_fault.png", xlim=(-0.05, 1.2))
    for m, r in ft.items():
        # 고장 제거(0.15 s) 후 P 가 0.72~0.88 pu (±10 %) 범위에 들어와 끝까지 머무는 시각
        t_all = arr(r, "t") - T_EV
        P_all = arr(r, "P")
        outside = np.where((t_all > 0.15) & ((P_all < 0.72) | (P_all > 0.88)))[0]
        rec = (t_all[outside[-1]] - 0.15) if len(outside) and outside[-1] < len(t_all) - 1 else float("nan")
        summary.append(("고장 0.3 pu·150 ms", m,
                        f"최대 전류 {window(r, 'I', 0, 0.15).max():.2f} pu, 고장 중 평균 V {window(r, 'V', 0, 0.15).mean():.2f} pu",
                        ("동기 유지" if sync_kept(r, 0.8) else "동기 이탈") +
                        (f", P ±10 % 정착 {rec*1000:.0f} ms" if not math.isnan(rec) else "")))
    data["fault"] = {m: downsample(r, ["V", "I", "P", "Q", "delta_deg"], t1=1.2) for m, r in ft.items()}

    # 6) 단독운전 (최후 동기원 상실) ----------------------------------------
    # FRT 진입을 0.5 pu 로 낮춰 FRT 모드 순환과 '기준 전압 상실'을 분리
    jobs = [(m, dict(scr=3.0, P_ref=0.5, P_load=0.8, gfl_frt_enter=0.5), dict(kind="island", t_end=1.5), m)
            for m in ("GFL", "GFM")]
    il = run_jobs(jobs, args.workers)
    stacked(plt, il, [("V", "|V_PCC| [pu]"), ("freq", "인버터 주파수 [Hz]"), ("P", "P [pu]")],
            "계통 분리(단독운전): 국부 부하 0.8 pu, P* = 0.5 pu", "fig07_islanding.png", xlim=(-0.05, 1.3))
    for m, r in il.items():
        f_end = window(r, "freq", 1.1, 99).mean()
        v_end = window(r, "V", 1.1, 99).mean()
        summary.append(("계통 분리", m, f"1.1 s 후 f = {f_end:.2f} Hz, V = {v_end:.2f} pu",
                        "V/f 유지" if abs(f_end - 60) < 1 and abs(v_end - 1) < 0.1 else "V/f 유지 실패"))
    data["island"] = {m: downsample(r, ["V", "freq", "P"], t1=1.3) for m, r in il.items()}

    # 요약 ------------------------------------------------------------------
    lines = ["# EMT 시뮬레이션 결과 요약", "",
             f"`python run_scenarios.py` 로 생성. 해석 시간 간격 dt = {DT * 1e6:g} µs (RK4), 기록 간격 100 µs. "
             "모델·가정은 [README](../README.md) 참고.", "",
             "| 시나리오 | 방식 | 지표 1 | 지표 2 |", "|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in summary]
    lines += ["", "## 약계통 안정도 맵", "",
              "| 구성 | " + " | ".join(f"SCR {s}" for s in scrs) + " |",
              "|---|" + "---|" * len(scrs)]
    for row in rows:
        lines.append(f"| {row} | " + " | ".join("✓ 안정" if table[(row, s)] else "✗ 불안정" for s in scrs) + " |")
    open(os.path.join(RES, "summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    data["summary"] = summary
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(RES, "emt_results.json"), "w", encoding="utf-8").write(js)
    print("\n".join(lines))

    if not args.no_slides and os.path.exists(SLIDES):
        html = open(SLIDES, encoding="utf-8").read()
        new, n = re.subn(r"/\*EMT_DATA_START\*/.*?/\*EMT_DATA_END\*/",
                         lambda m: "/*EMT_DATA_START*/" + js + "/*EMT_DATA_END*/", html, flags=re.S)
        if n:
            open(SLIDES, "w", encoding="utf-8").write(new)
            print(f"슬라이드 데이터 갱신: {SLIDES}")


if __name__ == "__main__":
    main()
