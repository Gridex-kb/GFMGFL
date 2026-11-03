"""8강 그림용 데이터. 저장소 루트에서: python slides/figs-src/L08/_data.py (평균값 모델, 약 90 s)
W03-SCR급변.json: 선로 트립 SCR 5 → 1.5, P* 0.8, FRT 진입 0.5 — GFM / GFL 20 Hz / GFL 50 Hz 의 P
W04-진동유형.json: ① GFL 10 Hz, SCR 5 → 1.3 (동기화 상실형 ~10 Hz) ② GFL 50 Hz, SCR 5 → 1.5 (상호작용형 ~90 Hz)
W06-판정.json: oscillation_check 결과 5건 (교재 실습 표)
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state, oscillation_check

OUT = os.path.dirname(os.path.abspath(__file__))
DT = 10e-6; T_EV = 0.2
r4 = lambda a: [round(float(v), 4) for v in a]


def run_scr(mode, f_pll, scr1, t_end=1.0):
    p = Params(converter="average", scr=5.0, P_ref=0.8, f_pll=f_pll, gfl_frt_enter=0.5)
    sc = Scenario(t_end=t_end, scr=lambda t: 5.0 if t < T_EV else scr1)
    return simulate(mode, p, sc, dt=DT, x0=steady_state(mode, p, dt=DT))


res = {}
for key, mode, fp in (("GFM", "GFM", 20), ("GFL20", "GFL", 20), ("GFL50", "GFL", 50)):
    r = run_scr(mode, fp, 1.5, 0.8)
    t = np.asarray(r["t"]); P = np.asarray(r["P"]); f = np.asarray(r["freq"])
    sel = (t >= T_EV - 0.05) & (t <= T_EV + 0.6); d = slice(None, None, 2)
    res[key] = {"t": r4((t[sel][d] - T_EV) * 1e3), "P": r4(P[sel][d]), "f": r4(f[sel][d]), "Pmin": round(float(P[t > T_EV].min()), 3)}
    print(key, "P min", P[t > T_EV].min(), "P late std", P[t > 0.6].std())
json.dump(res, open(os.path.join(OUT, "W03-SCR급변.json"), "w"))

out = {}
r1 = run_scr("GFL", 10, 1.3, 0.8); t = np.asarray(r1["t"]); P = np.asarray(r1["P"]); f = np.asarray(r1["freq"])
sel = (t >= T_EV - 0.05) & (t <= T_EV + 0.6); d = slice(None, None, 2)
out["loss"] = {"t": r4((t[sel][d] - T_EV) * 1e3), "P": r4(P[sel][d]), "f": r4(f[sel][d])}
r2 = run_scr("GFL", 50, 1.5, 0.8); t = np.asarray(r2["t"]); P = np.asarray(r2["P"])
sel = (t >= T_EV + 0.4) & (t <= T_EV + 0.46)
out["inter"] = {"t": r4((t[sel] - T_EV) * 1e3), "P": r4(P[sel])}
x = P[t > 0.6] - P[t > 0.6].mean(); F = np.abs(np.fft.rfft(x * np.hanning(len(x)))); fr = np.fft.rfftfreq(len(x), 1e-4)
out["inter"]["f_osc"] = round(float(fr[np.argmax(F[fr > 5]) + int((fr <= 5).sum())]), 0)
print("inter f_osc", out["inter"]["f_osc"])
json.dump(out, open(os.path.join(OUT, "W04-진동유형.json"), "w"))

tab = []
for mode, f_pll, scr_after in [("GFL", 20, 1.5), ("GFL", 50, 1.5), ("GFL", 50, 2.0), ("GFL", 10, 1.3), ("GFM", 20, 1.3)]:
    r = run_scr(mode, f_pll, scr_after, 1.0)
    t, P = np.asarray(r["t"]), np.asarray(r["P"])
    ok, info = oscillation_check(t, P, T_EV + 0.2)
    row = {"mode": mode, "f_pll": f_pll, "scr": scr_after, "ok": bool(ok), "osc_amp": round(float(info["osc_amp"]), 3), "osc_f": round(float(info["osc_f"]), 0), "swing_std": round(float(info["swing_std"]), 3)}
    tab.append(row); print(row)
json.dump(tab, open(os.path.join(OUT, "W06-판정.json"), "w"))
