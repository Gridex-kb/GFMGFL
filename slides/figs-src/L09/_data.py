"""9강 그림용 데이터. 저장소 루트에서: python slides/figs-src/L09/_data.py (평균값 모델 10 µs, 약 2 분)
F02-고장응답.json: 계통 전압 0.3 pu × 150 ms, SCR 3, P* 0.8 — GFM(보정) / GFM(보정 없음) / GFL 의 |i|, P, Δδ + 지표
F03-PCC지락.json : PCC 3상 지락(컨덕턴스 20 pu) × 200 ms, 전류 한계 1.2 / 2.0 — GFM/GFL 의 |i|, V + 지표
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

OUT = os.path.dirname(os.path.abspath(__file__))
T, DT = 0.2, 10e-6
r4 = lambda a: [round(float(v), 4) for v in a]


def run(mode, sc, **kw):
    p = Params(converter="average", P_ref=0.8, scr=3.0, **kw)
    r = simulate(mode, p, sc, dt=DT, x0=steady_state(mode, p, dt=DT))
    d = {k: np.asarray(v) for k, v in r.items() if isinstance(v, list)}
    d["t"] = d["t"] - T
    return d


# 그림 2: 계통 전압 0.3 pu × 150 ms
sc = Scenario(t_end=1.5, grid_v=lambda t: 0.3 if T <= t < T + 0.15 else 1.0)
res = {}
for key, mode, kw in (("freeze", "GFM", {}), ("nofreeze", "GFM", dict(gfm_limit_freeze=False)), ("GFL", "GFL", {})):
    r = run(mode, sc, **kw)
    t, I, P, V, sat = r["t"], r["I"], r["P"], r["V"], r["sat"]
    d = r["delta_deg"]; d = d - d[(t > -0.05) & (t < 0)].mean()
    m = (t >= 0) & (t < 0.15)
    sat_end = float(t[(sat > 0.5) & (t > 0.15)].max(initial=0.15) - 0.15)
    off = np.where((t > 0.15) & (np.abs(P - 0.8) > 0.08))[0]
    rec = float(t[off[-1]] - 0.15) if len(off) else 0.0
    sel = (t >= -0.05) & (t <= 1.3); s = slice(None, None, 4)
    res[key] = {"t": r4(t[sel][s] * 1e3), "I": r4(I[sel][s]), "P": r4(P[sel][s]), "dd": r4(d[sel][s]),
                "Ipk": round(float(I[m].max()), 2), "Vmean": round(float(V[m].mean()), 2), "ddmax": round(float(np.abs(d).max()), 1),
                "sat_end_ms": round(sat_end * 1e3, 0), "rec_ms": round(rec * 1e3, 0)}
    print(key, {k: v for k, v in res[key].items() if k not in ("t", "I", "P", "dd")})
json.dump(res, open(os.path.join(OUT, "F02-고장응답.json"), "w"))

# 그림 3: PCC 지락, 전류 한계 1.2 / 2.0
sc = Scenario(t_end=0.6, pcc_fault_g=lambda t: 20.0 if T <= t < T + 0.2 else 0.0)


def longest_run(mask, step):
    best = run_ = 0
    for mm in mask:
        run_ = run_ + 1 if mm else 0
        best = max(best, run_)
    return best * step


out = {}
for mode in ("GFL", "GFM"):
    for imax in (1.2, 2.0):
        r = run(mode, sc, I_max=imax)
        t, I, V = r["t"], r["I"], r["V"]
        m = (t >= 0) & (t < 0.2)
        dur = longest_run(I[m] >= 1.98, t[1] - t[0])
        sel = (t >= -0.03) & (t <= 0.4); s = slice(None, None, 2)
        key = f"{mode}_{imax:.1f}"
        out[key] = {"t": r4(t[sel][s] * 1e3), "I": r4(I[sel][s]), "V": r4(np.minimum(V[sel][s], 1.6)),
                    "Imax_fault": round(float(I[m].max()), 2), "dur_ms": round(dur * 1e3, 0), "Vmean": round(float(V[m].mean()), 2),
                    "Ipk_after": round(float(I[(t >= 0.2) & (t < 0.25)].max()), 2)}
        print(key, {k: v for k, v in out[key].items() if k not in ("t", "I", "V")})
json.dump(out, open(os.path.join(OUT, "F03-PCC지락.json"), "w"))
