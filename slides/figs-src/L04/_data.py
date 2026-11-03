"""4강 그림용 EMT 데이터. 저장소 루트에서: python slides/figs-src/L04/_data.py (약 20 s)
K02-꼭짓점샘플.json: 강계통 GFM의 Lf 전류(2 µs)와 반송파 꼭짓점 샘플
K04-연속각.json: GFL(PLL 대역폭 50 Hz, SCR 5)의 PLL 주파수, 샘플 시점 θ vs 연속 θ
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
import gfm_gfl_emt as emt
from gfm_gfl_emt import Params, Scenario, simulate, steady_state, replace

OUT = os.path.dirname(os.path.abspath(__file__))
Orig = emt.Inverter
r4 = lambda a: [round(float(v), 5) for v in a]

fine = {"t": [], "if": []}; samp = {"t": [], "if": []}
class LoggedA(Orig):
    def sample(self, t, x):
        samp["t"].append(t); samp["if"].append(x[emt.IF_RE]); super().sample(t, x)
    def pcc_voltage(self, t, x):
        fine["t"].append(t); fine["if"].append(x[emt.IF_RE]); return super().pcc_voltage(t, x)
emt.Inverter = LoggedA
pa = Params(converter="average", scr=3.0)
x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.06), x0=x0, hires=(0.05, 0.06))
emt.Inverter = Orig
tf, i_f = np.array(fine["t"]), np.array(fine["if"]); st, si = np.array(samp["t"]), np.array(samp["if"])
t0 = 0.0532; mf = (tf >= t0) & (tf <= t0 + 0.0006); ms = (st >= t0 - 1e-9) & (st <= t0 + 0.0006)
json.dump({"t": r4((tf[mf] - t0) * 1e6), "i": r4(i_f[mf]), "ts": r4((st[ms] - t0) * 1e6), "is": r4(si[ms])},
          open(os.path.join(OUT, "K02-꼭짓점샘플.json"), "w"))

class ContTheta(Orig):
    def deriv(self, t, x):
        self.th_hold = x[emt.TH_C]
        return super().deriv(t, x)
pg = Params(converter="average", scr=5.0, f_pll=50.0)
xg = steady_state("GFL", pg, t_init=1.5, dt=1e-5)
res = {}
for name, cls in (("hold", Orig), ("cont", ContTheta)):
    emt.Inverter = cls
    r = simulate("GFL", replace(pg, converter="switching"), Scenario(t_end=0.15), x0=xg)
    tr, fr = np.array(r["t"]), np.array(r["freq"])
    k = 50; fs = np.convolve(fr, np.ones(k) / k, mode="same"); m = (tr >= 0.05) & (tr <= tr[-1] - k * 1e-4)
    res[name] = {"t": r4((tr[m] - 0.05) * 1e3), "f": r4(fs[m]), "mean": round(float(fr[tr >= 0.05].mean()), 3)}
emt.Inverter = Orig
json.dump(res, open(os.path.join(OUT, "K04-연속각.json"), "w"))
print({k: v["mean"] for k, v in res.items()})
