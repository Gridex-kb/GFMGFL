"""7강 그림용 데이터. 저장소 루트에서: python slides/figs-src/L07/_data.py (평균값 모델, 약 90 s)
G04-위상점프.json: 평균값 EMT, SCR 3, P* 0.5, −20° 위상 점프 → GFM(VSM)과 GFL(PLL 20 Hz)의 P, 내부 주파수
G06-주파수계단.json: 계통 주파수 −0.2 Hz 계단 → GFM P 응답, H = 1 / 4 / 8 s (정상상태 = 드룹 2 %)
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

OUT = os.path.dirname(os.path.abspath(__file__))
DT = 10e-6
r4 = lambda a: [round(float(v), 4) for v in a]

# 위상 점프 −20°: GFM vs GFL
p = Params(converter="average")
t_ev = 0.1
jump = Scenario(t_end=0.9, grid_phase=lambda t: math.radians(-20) if t >= t_ev else 0.0)
res = {}
for mode in ("GFM", "GFL"):
    r = simulate(mode, p, jump, dt=DT, x0=steady_state(mode, p, dt=DT))
    t = np.asarray(r["t"]); P = np.asarray(r["P"]); f = np.asarray(r["freq"])
    P0 = float(P[t < t_ev][-1])
    m10 = (t >= t_ev) & (t <= t_ev + 0.01)
    dmax = float(P[m10].max() - P0); davg = float(P[(t > t_ev + 0.01) & (t < t_ev + 0.03)].mean() - P0)
    d = slice(None, None, 2)
    res[mode] = {"t": r4((t[d] - t_ev) * 1e3), "P": r4(P[d]), "f": r4(f[d]), "dP10": round(dmax, 3), "dP10_30": round(davg, 3),
                 "fmin": round(float(f.min()), 2), "Pmax": round(float(P.max()), 3)}
    print(f"{mode}: 10 ms 내 최대 ΔP {dmax:+.3f} pu, 10~30 ms 평균 ΔP {davg:+.3f} pu, 주파수 최저 {f.min():.2f} Hz, P 최대 {P.max():.3f}")
X = p.Xv + 1 / p.scr; d0 = math.asin(p.P_ref * X)
res["phasor"] = {"X": round(X, 3), "d0_deg": round(math.degrees(d0), 1), "dP": round((math.sin(d0 + math.radians(20)) - math.sin(d0)) / X, 3),
                 "Ks": round(math.cos(d0) / X, 3)}
Ks = math.cos(d0) / X; wn = math.sqrt(p.wb * Ks / (2 * p.H)); zeta = p.D / (4 * p.H * wn)
res["phasor"].update({"fn": round(wn / (2 * math.pi), 2), "zeta": round(zeta, 2)})
print("페이저:", res["phasor"])
json.dump(res, open(os.path.join(OUT, "G04-위상점프.json"), "w"))

# 계통 주파수 −0.2 Hz 계단, H = 1/4/8
out = {}
step = Scenario(t_end=2.0, grid_f=lambda t: 1.0 - 0.2 / 60 if t >= 0.1 else 1.0)
for H in (1.0, 4.0, 8.0):
    p = Params(converter="average", H=H)
    r = simulate("GFM", p, step, dt=DT, x0=steady_state("GFM", p, dt=DT))
    t = np.asarray(r["t"]); P = np.asarray(r["P"])
    P0 = float(P[t < 0.1][-1]); dss = float(P[t > 1.8].mean() - P0); dmax = float(P.max() - P0)
    d = slice(None, None, 5)
    out[f"H{H:.0f}"] = {"t": r4((t[d] - 0.1) * 1e3), "P": r4(P[d]), "dP_ss": round(dss, 3), "dP_max": round(dmax, 3)}
    print(f"H = {H:.0f} s: 정상상태 ΔP {dss:+.3f} pu (드룹 예측 {p.D * 0.2 / 60:+.3f}), 최대 ΔP {dmax:+.3f} pu")
out["droop"] = round(50 * 0.2 / 60, 3)
json.dump(out, open(os.path.join(OUT, "G06-주파수계단.json"), "w"))
