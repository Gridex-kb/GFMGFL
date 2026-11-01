"""
해석 시간 간격(dt) 수렴 확인: 50 / 25 / 10 / 1 µs 에서 같은 시나리오의 핵심 지표를 비교한다.

사용법:  python convergence.py        (약 5분, 4코어)
출력:    results/convergence.md
"""
from __future__ import annotations

import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gfm_gfl_emt import Params, Scenario, simulate, steady_state  # noqa: E402

T = 0.2
DTS = (50e-6, 25e-6, 10e-6, 1e-6)


def run(job):
    case, mode, dt = job
    if case == "phase":
        p = Params(P_ref=0.5, scr=3.0)
        sc = Scenario(t_end=0.6, grid_phase=lambda t: math.radians(-20) if t >= T else 0.0)
    elif case == "weak":
        p = Params(scr=5.0, P_ref=0.8, f_pll=35.0, gfl_frt_enter=0.5)
        sc = Scenario(t_end=1.6, scr=lambda t: 5.0 if t < T else 1.5)
    else:
        p = Params(P_ref=0.8, scr=3.0)
        sc = Scenario(t_end=1.0, grid_v=lambda t: 0.3 if T <= t < T + 0.15 else 1.0)
    x0 = steady_state(mode, p, dt=dt)
    r = simulate(mode, p, sc, dt=dt, x0=x0)
    t = np.asarray(r["t"]) - T
    P, I, V = (np.asarray(r[k]) for k in ("P", "I", "V"))
    if case == "phase":
        m = (t >= 0) & (t < 0.01)
        return job, {"dP10": P[m].max() - 0.5}
    if case == "weak":
        return job, {"Pstd": P[t > 1.0].std()}
    m = (t >= 0) & (t < 0.15)
    return job, {"Imax": I[m].max(), "Vmean": V[m].mean(), "Vmin": V[m].min()}


def main():
    jobs = [(c, m, dt) for c in ("phase", "weak", "fault") for m in ("GFL", "GFM") for dt in DTS]
    # 무거운 1 µs 작업을 먼저 시작
    jobs.sort(key=lambda j: j[2])
    with ProcessPoolExecutor(os.cpu_count() or 2) as ex:
        res = dict(ex.map(run, jobs))
    head = "| 시나리오 | 방식 | 지표 | " + " | ".join(f"{dt * 1e6:g} µs" for dt in DTS) + " |"
    rows = [head, "|---|---|---|" + "---|" * len(DTS)]
    spec = [("phase", "위상 점프 −20°", [("dP10", "10 ms 내 ΔP 최대 [pu]")]),
            ("weak", "SCR 5→1.5 (PLL 35 Hz)", [("Pstd", "P 표준편차 1.0 s~ [pu]")]),
            ("fault", "고장 0.3 pu·150 ms", [("Imax", "최대 전류 [pu]"), ("Vmean", "고장 중 평균 V [pu]"),
                                            ("Vmin", "고장 중 순간 최저 V [pu]")])]
    for case, name, keys in spec:
        for m in ("GFL", "GFM"):
            for k, lab in keys:
                vals = " | ".join(f"{res[(case, m, dt)][k]:.3f}" for dt in DTS)
                rows.append(f"| {name} | {m} | {lab} | {vals} |")
    md = "# 해석 시간 간격 수렴 확인\n\n`python convergence.py` 로 생성. RK4 고정 스텝.\n\n" + "\n".join(rows) + "\n"
    open(os.path.join(HERE, "results", "convergence.md"), "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
