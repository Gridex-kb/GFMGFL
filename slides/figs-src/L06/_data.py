"""6강 그림용 데이터. 저장소 루트에서: python slides/figs-src/L06/_data.py (평균값 모델, 약 60 s)
N03-PLL대역폭.json: 강계통 SRF-PLL 비선형 응답, −20° 위상 점프, 10/20/50 Hz
N04-위상점프.json : 평균값 EMT GFL, SCR 3, P* 0.5, PLL 20 Hz, −20° 점프 → P, Q, 측정 주파수
N05-FRT순환.json  : 평균값 EMT GFL, SCR 5 → 1.5, P* 0.8, FRT 진입 0.85 / 0.5 → |v|, 주파수
"""
import os, sys, json, math
import numpy as np
sys.path.insert(0, os.path.join("simulation", "emt"))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state

OUT = os.path.dirname(os.path.abspath(__file__))
DT = 10e-6
r4 = lambda a: [round(float(v), 4) for v in a]


def pll_step(f_pll, dphi_deg=-20.0, zeta=0.707, dw_max=0.1, t_end=0.1, h=1e-5):
    wb = 2 * math.pi * 60; wn = 2 * math.pi * f_pll
    kp, ki = 2 * zeta * wn / wb, wn * wn / wb
    n = int(t_end / h); t = np.arange(n) * h
    e_out, f_out = np.zeros(n), np.zeros(n)
    th_err = math.radians(dphi_deg); x = 0.0
    for k in range(n):
        vq = math.sin(th_err)
        dw = min(dw_max, max(-dw_max, kp * vq + x))
        if not ((x >= dw_max and vq > 0) or (x <= -dw_max and vq < 0)):
            x += h * ki * vq
        th_err -= h * wb * dw
        e_out[k], f_out[k] = math.degrees(th_err), 60 * (1 + dw)
    return t, e_out, f_out, kp, ki


res = {}
for fp in (10, 20, 50):
    t, e, f, kp, ki = pll_step(fp)
    settle = float(t[np.abs(e) > 1.0].max() * 1e3) if np.any(np.abs(e) > 1.0) else 0.0
    d = slice(None, None, 10)
    res[str(fp)] = {"t": r4(t[d] * 1e3), "e": r4(e[d]), "f": r4(f[d]), "kp": round(kp, 3), "ki": round(ki, 1),
                    "fmin": round(float(f.min()), 2), "settle_ms": round(settle, 0),
                    "df0": round(60 * kp * math.sin(math.radians(-20)), 1)}
    print(f"PLL {fp} Hz: kp {kp:.3f} ki {ki:.1f}, fmin {f.min():.2f}, |e|<1° 정착 {settle:.0f} ms, 첫 반응 {res[str(fp)]['df0']} Hz")
json.dump(res, open(os.path.join(OUT, "N03-PLL대역폭.json"), "w"))

# 위상 점프 (평균값 EMT, SCR 3, PLL 20 Hz)
p = Params(converter="average")
x0 = steady_state("GFL", p, dt=DT)
t_ev = 0.1
sc = Scenario(t_end=0.35, grid_phase=lambda t: math.radians(-20) if t >= t_ev else 0.0)
r = simulate("GFL", p, sc, dt=DT, x0=x0)
t = np.asarray(r["t"]); P = np.asarray(r["P"]); Q = np.asarray(r["Q"]); f = np.asarray(r["freq"])
m10 = (t >= t_ev) & (t <= t_ev + 0.01)
dP = float(P[m10].max() - P[t < t_ev][-1])
t54 = float(((t >= t_ev) & (f <= 54.01)).sum() * (t[1] - t[0]) * 1e3)
sel = (t >= t_ev - 0.03) & (t <= t_ev + 0.25)
json.dump({"t": r4((t[sel] - t_ev) * 1e3), "P": r4(P[sel]), "Q": r4(Q[sel]), "f": r4(f[sel]),
           "dP10": round(dP, 3), "fmin": round(float(f.min()), 2), "t54_ms": round(t54, 1)},
          open(os.path.join(OUT, "N04-위상점프.json"), "w"))
print(f"위상 점프: 10 ms 내 ΔP {dP:+.3f} pu, 측정 주파수 최저 {f.min():.2f} Hz, 54 Hz 체류 {t54:.1f} ms")

# FRT 모드 순환 (평균값 EMT, SCR 5 → 1.5)
t_ev = 0.2
sc = Scenario(t_end=0.8, scr=lambda t: 5.0 if t < t_ev else 1.5)
out = {}
for key, enter in (("e085", 0.85), ("e050", 0.5)):
    p = Params(converter="average", scr=5.0, P_ref=0.8, gfl_frt_enter=enter)
    x0 = steady_state("GFL", p, dt=DT)
    r = simulate("GFL", p, sc, dt=DT, x0=x0)
    t = np.asarray(r["t"]); V = np.asarray(r["V"]); f = np.asarray(r["freq"])
    late = t > 0.5
    sel = (t >= t_ev - 0.05) & (t <= t_ev + 0.6)
    d = slice(None, None, 2)
    out[key] = {"t": r4((t[sel][d] - t_ev) * 1e3), "V": r4(V[sel][d]), "f": r4(f[sel][d]),
                "vmin": round(float(V[late].min()), 2), "vmax": round(float(V[late].max()), 2),
                "fmin": round(float(f[late].min()), 1), "fmax": round(float(f[late].max()), 1),
                "vmin_all": round(float(V[t > t_ev].min()), 2)}
    print(f"FRT 진입 {enter}: 0.3 s 이후 |v| {out[key]['vmin']}~{out[key]['vmax']} pu, 주파수 {out[key]['fmin']}~{out[key]['fmax']} Hz, 전환 후 최저 {out[key]['vmin_all']}")
json.dump(out, open(os.path.join(OUT, "N05-FRT순환.json"), "w"))
