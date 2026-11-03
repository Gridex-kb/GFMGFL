"""5강 그림용 데이터. 저장소 루트에서: python slides/figs-src/L05/_data.py (약 40 s)
M02-계단응답.json: dq 전류루프 독립 모의(0.1 pu id 계단) — 지연·디커플링 조합
M07-와인드업.json: 1 pu 계단에서 anti-windup 유무
M04-피드포워드.json: EMT GFM, SCR 2, PCC 전압 피드포워드 (없음 / 순시 / 100 Hz LPF)
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state, replace

OUT = os.path.dirname(os.path.abspath(__file__))
p0 = Params(); wb = p0.wb; Ts = 1 / (2 * p0.f_sw)
wcc = 2 * math.pi * p0.f_cc; Kp = wcc * p0.Lf / wb; Ki = Kp * wcc / 5
r5 = lambda a: [round(float(v), 5) for v in a]


def current_loop(i_ref_fn, t_end=0.01, decouple=True, delay=True, antiwindup=True, dt=2e-6):
    """dq 전류루프 독립 모의 (Cf 무시, 단자 전압 1 pu). 10 kHz 샘플, 1샘플 계산 지연 + 영차 홀드."""
    n = int(round(t_end / dt)); per = int(round(Ts / dt))
    i = 0j; x = 1.0 + 0j; v_now = v_next = 1.0 + 0j
    T, I = np.empty(n), np.empty(n, complex)
    for k in range(n):
        t = k * dt
        if k % per == 0:
            e = i_ref_fn(t) - i
            v = Kp * e + x + (1j * p0.Lf * i if decouple else 0)
            sat = abs(v) > p0.V_conv_max
            if sat:
                v *= p0.V_conv_max / abs(v)
            if not sat or not antiwindup:
                x += Ki * Ts * e
            if delay:
                v_now, v_next = v_next, v
            else:
                v_now = v
        i += (v_now - p0.Rf * i - 1j * p0.Lf * i - 1.0) * (wb / p0.Lf) * dt
        T[k], I[k] = t, i
    return T, I


step = lambda t: 0.1 + 0j if t >= 0.001 else 0j
T, I1 = current_loop(step); _, I2 = current_loop(step, decouple=False); _, I3 = current_loop(step, delay=False)
d = slice(None, None, 5)
json.dump({"t": r5((T[d] - 0.001) * 1e3), "base_d": r5(I1.real[d]), "base_q": r5(I1.imag[d]),
           "nodec_d": r5(I2.real[d]), "nodec_q": r5(I2.imag[d]), "nodelay_d": r5(I3.real[d]), "nodelay_q": r5(I3.imag[d]),
           "os_delay": round(float((I1.real.max() - 0.1) / 0.1 * 100), 1), "os_nodelay": round(float((I3.real.max() - 0.1) / 0.1 * 100), 1)},
          open(os.path.join(OUT, "M02-계단응답.json"), "w"))

big = lambda t: 1.0 + 0j if t >= 0.001 else 0j
T, A1 = current_loop(big, t_end=0.012); _, A2 = current_loop(big, t_end=0.012, antiwindup=False)
json.dump({"t": r5((T[d] - 0.001) * 1e3), "aw": r5(A1.real[d]), "noaw": r5(A2.real[d]),
           "os_aw": round(float((A1.real.max() - 1) * 100), 1), "os_noaw": round(float((A2.real.max() - 1) * 100), 1)},
          open(os.path.join(OUT, "M07-와인드업.json"), "w"))
print("os", (I1.real.max() - 0.1) / 0.1 * 100, (I3.real.max() - 0.1) / 0.1 * 100, "aw", A1.real.max(), A2.real.max())

res = {}
for key, ff, fv in (("none", 0.0, 100.0), ("inst", 1.0, 0.0), ("lpf", 1.0, 100.0)):
    pa = Params(converter="average", scr=2.0, ff_gain=ff, f_vff=fv)
    x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
    r = simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.2), x0=x0)
    t = np.array(r["t"]); P = np.array(r["P"])
    res[key] = {"t": r5(t * 1e3), "P": r5(P), "std": round(float(P[t >= 0.1].std()), 3)}
    if key == "inst":
        x = P[t >= 0.1] - P[t >= 0.1].mean(); F = np.abs(np.fft.rfft(x * np.hanning(len(x)))); f = np.fft.rfftfreq(len(x), 1e-4)
        res[key]["f_osc"] = round(float(f[np.argmax(F)]), 0)
    print(key, res[key]["std"], res[key].get("f_osc"))
json.dump(res, open(os.path.join(OUT, "M04-피드포워드.json"), "w"))
