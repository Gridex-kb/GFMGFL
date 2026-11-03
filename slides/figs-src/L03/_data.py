"""3강 그림용 EMT 데이터 (강계통 GFM, 스위칭 2 µs). 저장소 루트에서: python slides/figs-src/L03/_data.py
출력: H04-리플.json (a상 Lf/변압기 전류), H05-측정점.json (샘플 시점 P와 스펙트럼)
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
import gfm_gfl_emt as emt
from gfm_gfl_emt import Params, Scenario, simulate, steady_state, replace

OUT = os.path.dirname(os.path.abspath(__file__))
fine = {"t": [], "if": [], "it": []}
samp = {"t": [], "P_pcc": [], "P_lf": []}

class Logged(emt.Inverter):
    def sample(self, t, x):
        v_term, v_pcc, i_t = self.network(t, x)[:3]
        i_f = complex(x[emt.IF_RE], x[emt.IF_IM])
        samp["t"].append(t)
        samp["P_pcc"].append((v_pcc * i_t.conjugate()).real)
        samp["P_lf"].append((v_term * i_f.conjugate()).real)
        super().sample(t, x)
    def pcc_voltage(self, t, x):
        fine["t"].append(t); fine["if"].append(x[emt.IF_RE]); fine["it"].append(x[emt.IG_RE])
        return super().pcc_voltage(t, x)

emt.Inverter = Logged
pa = Params(converter="average", scr=10.0)
x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.2), x0=x0, hires=(0.15, 0.2))

tf, i_f, i_t = (np.array(fine[k]) for k in ("t", "if", "it"))
k = 100
sm = np.convolve(i_f, np.ones(k) / k, mode="same"); rip = (i_f - sm)[k:-k]
f0 = 60.0
m1 = (tf >= 0.15) & (tf <= 0.15 + 1 / f0)
t0z = 0.15 + 0.25 / f0 - 0.0005
m2 = (tf >= t0z) & (tf <= t0z + 0.001)
r4 = lambda a: [round(float(v), 4) for v in a]
json.dump({"cyc": {"t": r4((tf[m1] - 0.15) * 1e3), "if": r4(i_f[m1]), "it": r4(i_t[m1])},
           "zoom": {"t": r4((tf[m2] - t0z) * 1e3), "if": r4(i_f[m2]), "it": r4(i_t[m2])},
           "ripple_pp": round(float(rip.max() - rip.min()), 3)},
          open(os.path.join(OUT, "H04-리플.json"), "w"))

ts, Pp, Pl = (np.array(samp[k]) for k in ("t", "P_pcc", "P_lf"))
m = ts >= 0.1
def spec(x):
    x = x - x.mean(); F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) * 4.0 / len(x)
    return np.fft.rfftfreq(len(x), 1e-4), F
fs, Fl = spec(Pl[m]); _, Fp = spec(Pp[m]); sel = fs <= 2000
json.dump({"t": r4((ts[m] - 0.1) * 1e3), "Pp": r4(Pp[m]), "Pl": r4(Pl[m]),
           "sp": round(float(Pp[m].std()), 4), "sl": round(float(Pl[m].std()), 4),
           "f": r4(fs[sel]), "Fp": r4(Fp[sel] * 1e3), "Fl": r4(Fl[sel] * 1e3)},
          open(os.path.join(OUT, "H05-측정점.json"), "w"))
print("ripple", round(float(rip.max() - rip.min()), 3), "sigma pcc", Pp[m].std(), "lf", Pl[m].std(), "Pmean", Pp[m].mean())
