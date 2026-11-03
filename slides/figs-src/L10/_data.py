"""10강 그림용 데이터. 저장소 루트에서: python slides/figs-src/L10/_data.py (시뮬레이션 없음, 수 초)
simulation/emt/results/compliance.json (스위칭 모델 2 µs 보고서 결과)의 그래프 계열을 그림별 JSON으로 꺼내고,
라벨에 쓸 지표(위상점프 응답 시간, 감쇠 극값, 전압 스텝 90 % 도달, 2.0 pu 지속)를 같은 자료에서 다시 계산한다.
"""
import json
import math
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "simulation", "emt", "results", "compliance.json"), encoding="utf-8"))
TESTS = {t["id"]: t for t in D["tests"]}
r4 = lambda a: [round(float(v), 4) for v in a]


def series(tid, idx, label):
    c = TESTS[tid]["charts"][idx]
    s = c["series"][label]
    return np.asarray(s["t"]), np.asarray(s[c["key"]])


def dump(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False)
    print("저장:", name)


def report(tid, crit, label):
    """보고서 판정 항목의 측정값 문자열에서 숫자를 뽑는다 (라벨은 보고서 수치를 쓴다. 그래프 계열은 500점으로 줄인 것)."""
    import re
    s = TESTS[tid]["criteria"][crit]["values"][label]
    return [float(v) for v in re.findall(r"[-+]?\d+(?:\.\d+)?", s)]


# S02 위상 점프 T07: 점프 직후 60 ms (P) + 전체 2.5 s (P), T11 감쇠 극값
s02 = {}
for L in ("GFL", "GFM"):
    t, P = series("T07", 0, L)
    P0 = P[(t >= -0.005) & (t < 0)].mean()
    dPs = P - P0
    m = (t >= 0) & (t <= 0.05)
    pk = dPs[m].max()
    t90 = t[m][np.argmax(dPs[m] >= 0.9 * pk)] if pk > 0.05 else None
    t50 = t[m][np.argmax(dPs[m] >= 0.5 * pk)] if pk > 0.05 else None
    tf, Pf = series("T07", 1, L)
    s02[L] = dict(t_ms=r4(t * 1e3), P=r4(P), P0=round(float(P0), 4), peak=round(float(pk), 3),
                  t90_ms=None if t90 is None else round(float(t90) * 1e3, 1), t50_ms=None if t50 is None else round(float(t50) * 1e3, 1),
                  tf=r4(tf), Pf=r4(Pf), di10=report("T07", 0, L)[0])
    if L == "GFM":   # 보고서 값: 응답 속도 "8.4 ms (초기 피크 0.64 pu)", 자연 응답 "3.1 ms"
        s02[L].update(t90_ms=report("T07", 1, L)[0], peak=report("T07", 1, L)[1], t50_ms=report("T07", 2, L)[0])
    print(f"T07 {L}: P0 {P0:.3f}, 초기 피크 ΔP {pk:.3f}, t50 {t50}, t90 {t90} (보고서 {s02[L]['peak']}, {s02[L]['t50_ms']}, {s02[L]['t90_ms']})")
# 감쇠 극값 (보고서 damping_ratio 와 같은 방법: 0.15 s 이후, 20 ms 이동평균)
t, P = series("T07", 1, "GFM")
k = max(1, int(round(0.02 / (t[1] - t[0]))))
Pf = np.convolve(P, np.ones(k) / k, mode="same")
m = (t >= 0.15) & (t <= t[-1] - 0.1)
tt, x = t[m], Pf[m] - Pf[m][-int(0.3 / (t[1] - t[0])):].mean()
ext = []
for i in range(1, len(x) - 1):   # 500점 계열이라 문턱을 0.01 로 (보고서는 100 µs 기록에 0.002)
    if (x[i] - x[i - 1]) * (x[i + 1] - x[i]) < 0 and abs(x[i]) > 0.01:
        if ext and np.sign(x[i]) == np.sign(x[ext[-1]]):
            if abs(x[i]) > abs(x[ext[-1]]):
                ext[-1] = i
            continue
        ext.append(i)
tk, ak = tt[ext], np.log(np.abs(x[ext]))
sigma = -np.polyfit(tk, ak, 1)[0]
wd = math.pi / np.mean(np.diff(tk))
zeta = sigma / math.sqrt(sigma ** 2 + wd ** 2)
s02["ext_t"] = r4(tk)
s02["ext_P"] = r4(Pf[m][ext])
s02["zeta"], s02["fd"] = report("T11", 0, "GFM")[0] / 100, report("T11", 0, "GFM")[1]
print(f"T11 극값 {len(ext)}개 {[round(float(v), 3) for v in x[ext]]}, 재계산 ζ {zeta * 100:.1f} % @ {wd / 2 / math.pi:.2f} Hz (보고서 {s02['zeta'] * 100:.1f} % @ {s02['fd']} Hz)")
dump("S02-위상점프.json", s02)

# S03 T07 점프 직후 상전류 (2 µs 스위칭, hires)
s03 = {}
for L, h in TESTS["T07"]["hires"].items():
    s03[L] = dict(t_ms=r4(np.asarray(h["t"]) * 1e3), ia=r4(h["ia"]), ib=r4(h["ib"]), ic=r4(h["ic"]))
dump("S03-상전류.json", s03)

# S04 RoCoF T05a: P, freq (GFL, GFL+SI, GFM) + H_eq 재계산
s04 = {}
for L in ("GFL", "GFL+SI", "GFM"):
    t, P = series("T05a", 0, L)
    tf, f = series("T05a", 1, L)
    P0 = P[(t >= -0.1) & (t < 0)].mean()
    df_end = -1.0 * 0.5 / 60
    Kd = (P[(t >= 1.4) & (t < 1.8)].mean() - P0) / (-df_end)
    dP = np.interp(0.5, t, P) - P0
    H = (dP - Kd * (-df_end)) / (-2.0 * (-1.0 / 60))
    s04[L] = dict(t=r4(t), P=r4(P), tf=r4(tf), f=r4(f), P0=round(float(P0), 4), dP_end=round(float(dP), 4), K=round(float(Kd), 1), H_eq=report("T05a", 1, L)[0])
    print(f"T05a {L}: P0 {P0:.3f}, ΔP(0.5 s) {dP:+.3f}, K {Kd:.0f}, 재계산 H_eq {H:.2f} s (보고서 {s04[L]['H_eq']})")
dump("S04-RoCoF.json", s04)

# S05 동기원 상실 T01: freq, V
s05 = {}
for L in ("GFL", "GFM"):
    t, f = series("T01", 0, L)
    tv, V = series("T01", 1, L)
    s05[L] = dict(t=r4(t), f=r4(f), V=r4(V), f_mean=round(float(f[t >= 1.0].mean()), 2))
    print(f"T01 {L}: 분리 1 s 후 평균 주파수 {f[t >= 1.0].mean():.2f} Hz, V 범위 {V[t >= 1.0].min():.2f}~{V[t >= 1.0].max():.2f}")
dump("S05-동기원상실.json", s05)

# S06 60° 내성 T09: P, delta_deg
s06 = {}
for L in ("GFL", "GFM"):
    t, P = series("T09", 0, L)
    td, d = series("T09", 1, L)
    d0 = d[(td >= -0.05) & (td < 0)].mean()
    s06[L] = dict(t=r4(t), P=r4(P), dd=r4(d - d0), P_end=round(float(P[t >= 1.3].mean()), 3), dd_end=round(float((d - d0)[td >= 1.3].mean()), 1))
    print(f"T09 {L}: 끝 P {P[t >= 1.3].mean():.3f}, 끝 위상 {(d - d0)[td >= 1.3].mean():+.1f}°")
dump("S06-60도.json", s06)

# S07 전압 스텝 T10: Q, V + 90 % 도달
s07 = {}
for L in ("GFL", "GFM"):
    t, Q = series("T10", 0, L)
    tv, V = series("T10", 1, L)
    Q0 = Q[(t >= -0.01) & (t < 0)].mean()
    q100 = np.interp(0.1, t, Q) - Q0
    m = t >= 0
    t90 = t[m][np.argmax((Q - Q0)[m] >= 0.9 * q100)]
    s07[L] = dict(t_ms=r4(t * 1e3), Q=r4(Q), V=r4(V), Q0=round(float(Q0), 4), q100=round(float(q100), 4), t90_ms=report("T10", 0, L)[0], Q90=round(float(Q0 + 0.9 * q100), 4))
    print(f"T10 {L}: Q0 {Q0:+.3f}, ΔQ@100 ms {q100:.3f}, 재계산 t90 {t90 * 1e3:.1f} ms (보고서 {s07[L]['t90_ms']})")
dump("S07-전압스텝.json", s07)

# S08 고장전류 T13: |i| 네 경우 + 2.0 pu 지속
s08 = {}
for L in TESTS["T13"]["labels"]:
    t, I = series("T13", 0, L)
    m = (t >= 0) & (t < 0.2)
    above = I[m] >= 1.98
    best = run = 0
    for a in above:
        run = run + 1 if a else 0
        best = max(best, run)
    dur = best * (t[1] - t[0])
    key = L.replace(" (I_max 2.0)", "_2.0") if "2.0" in L else L + "_1.2"
    rep = report("T13", 0, L)   # "197 ms (최대 2.01 pu)"
    s08[key] = dict(t_ms=r4(t * 1e3), I=r4(I), dur_ms=int(rep[0]), Imax_fault=rep[1])
    print(f"T13 {L}: 재계산 2.0 pu 이상 {dur * 1e3:.0f} ms, 고장 중 최대 {I[m].max():.2f} pu (보고서 {rep[0]:.0f} ms, {rep[1]} pu)")
dump("S08-고장전류.json", s08)

# 판정표 요약
n = {}
for t in D["tests"]:
    for L, v in t["verdict"].items():
        n.setdefault(L, [0, 0]); n[L][1] += 1; n[L][0] += bool(v)
print("적합 수:", {L: f"{a}/{b}" for L, (a, b) in n.items()})
