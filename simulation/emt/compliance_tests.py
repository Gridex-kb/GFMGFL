"""
표준 기반 GFM/GFL 시험 (NERC·AEMO·ERCOT·ENTSO-E·GB·한국 연계기준안의 시험 의도를 이 모델에 적용)

사용법:  python compliance_tests.py [--dt 2e-6] [--workers 4]
출력:    results/compliance.json, ../../reports/gfm-gfl-test-report.html 의 데이터 블록 갱신

주의: 공식 적합성 판정이 아니다. 단일 인버터·테브난 계통 모델에 시험 의도를 옮긴 것이며,
      규격이 정성적인 항목은 판정 기준을 보고서에서 '본 보고서 기준'으로 명시한다.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import re
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gfm_gfl_emt import DT_DEFAULT, Params, Scenario, oscillation_check, simulate, steady_state  # noqa: E402

REPORT = os.path.normpath(os.path.join(HERE, "..", "..", "reports", "gfm-gfl-test-report.html"))
T = 0.2  # 외란 시각 (웜스타트 이후)
F0 = 60.0

# ---------------------------------------------------------------------------
# 시험 정의
# ---------------------------------------------------------------------------
LSM_REF = ["NERC 2023 GFM 기능사양 Test 1~3", "AEMO 2024 Core Test 1~4", "ERCOT AGS #1~4"]
TESTS = [
    dict(id="T01", group="최후 동기기 상실", title="동기원 상실 — 방전 중",
         refs=LSM_REF, cond="SCR 3, P* = 0.5 pu, PCC 국부 부하 0.8 pu, t = 0 에 계통 차단기 개방",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.5, P_load=0.8), ev=dict(kind="island"), t_end=1.5),
    dict(id="T02", group="최후 동기기 상실", title="동기원 상실 — 충전 중 (방전 전환 필요)",
         refs=LSM_REF, cond="SCR 3, P* = −0.3 pu(충전), 국부 부하 0.5 pu, 차단기 개방",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=-0.3, P_load=0.5), ev=dict(kind="island"), t_end=1.5),
    dict(id="T03", group="최후 동기기 상실", title="동기원 상실 — 전류 한계 초과 부하",
         refs=LSM_REF, cond="SCR 3, P* = 0.8 pu, 국부 부하 1.4 pu (> I_max 1.2 pu), 차단기 개방",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.8, P_load=1.4), ev=dict(kind="island"), t_end=1.5),
    dict(id="T04", group="최후 동기기 상실", title="동기원 상실 — 전력 균형",
         refs=["AEMO 2024 Core Test 4"], cond="SCR 3, P* = 0.6 pu, 국부 부하 0.6 pu, 차단기 개방",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.6, P_load=0.6), ev=dict(kind="island"), t_end=1.5),
    dict(id="T05a", group="주파수 변화", title="RoCoF −1 Hz/s × 0.5 s",
         refs=["AEMO 2024 Core Test 5", "ERCOT AGS #5", "GB GC0137 Active ROCOF Response Power"],
         cond="SCR 5, P₀ = 0.3 pu, 계통 주파수 60 → 59.5 Hz 램프. GFL 은 드룹 2 % 사용",
         labels=["GFL", "GFL+SI", "GFM"], p=dict(scr=5.0, P_ref=0.3), ev=dict(kind="rocof", rate=-1.0), t_end=2.0),
    dict(id="T05b", group="주파수 변화", title="RoCoF +1 Hz/s × 0.5 s",
         refs=["AEMO 2024 Core Test 5 (양방향)", "AEMO 자발적 규격 2.3.3"],
         cond="SCR 5, P₀ = 0.3 pu, 계통 주파수 60 → 60.5 Hz 램프. GFL 은 드룹 2 % 사용",
         labels=["GFL", "GFL+SI", "GFM"], p=dict(scr=5.0, P_ref=0.3), ev=dict(kind="rocof", rate=1.0), t_end=2.0),
    dict(id="T06", group="약계통", title="SCR 급감 후 3상 고장",
         refs=["AEMO 2024 Core Test 6", "ERCOT AGS #6"],
         cond="P₀ = 0.8 pu, t = 0 에 SCR 3 → 1.5, t = 0.5 s 에 계통 전압 0.3 pu × 150 ms. 기본 FRT 설정",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.8), ev=dict(kind="scr_fault"), t_end=2.2),
    dict(id="T07", group="위상 점프", title="위상각 스텝 −20° (전력 공급 방향)",
         refs=["ERCOT AGS #7", "ENTSO-E TG GFC 2025", "GB GC0137 Active Phase Jump Power", "AEMO 2024 Core Test 7"],
         cond="SCR 3, P₀ = 0.5 pu, 계통 전압 위상 −20° 계단 변화",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.5), ev=dict(kind="phase", deg=-20.0), t_end=2.7, hires=(-0.005, 0.02)),
    dict(id="T08", group="위상 점프", title="위상각 스텝 +20° (전력 흡수 방향)",
         refs=["ERCOT AGS #7", "ENTSO-E TG GFC 2025", "GB GC0137"],
         cond="SCR 3, P₀ = 0.5 pu, 계통 전압 위상 +20° 계단 변화",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.5), ev=dict(kind="phase", deg=20.0), t_end=1.2),
    dict(id="T09", group="위상 점프", title="위상각 60° 내성",
         refs=["GB GC0137 Phase Jump Angle Withstand", "MISO 초안(60° 요건, 이후 삭제)"],
         cond="SCR 3, P₀ = 0.5 pu, 계통 전압 위상 −60° 계단 변화 (전류 제한 동작)",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.5), ev=dict(kind="phase", deg=-60.0), t_end=2.7),
    dict(id="T10", group="전압원 거동", title="계통 전압 크기 스텝 −5 %",
         refs=["ENTSO-E TG GFC 2025 (무효전류 30 ms 내 90 %)", "ERCOT AGS #9(정보용)"],
         cond="SCR 3, P₀ = 0.5 pu, 계통 전압 1.00 → 0.95 pu 계단 변화",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.5), ev=dict(kind="vstep", v=0.95), t_end=0.8),
    dict(id="T11", group="전압원 거동", title="유효전력 진동 감쇠 (0.1~10 Hz)",
         refs=["ENTSO-E TG GFC 2025 (감쇠비 ≥ 5 %)", "AEMO 2.3.2"],
         cond="T07 응답에서 스윙 진동의 감쇠비를 대수감쇠율로 추정", labels=["GFL", "GFM"], derived="T07"),
    dict(id="T12", group="고장", title="3상 고장 통과 (계통 전압 0.3 pu × 150 ms)",
         refs=["IEEE 2800-2022 라이드스루", "국내 송·배전용 전기설비 이용규정 FRT"],
         cond="SCR 3, P₀ = 0.8 pu, 계통 전압 0.3 pu × 150 ms. 기본 FRT 설정",
         labels=["GFL", "GFM"], p=dict(scr=3.0, P_ref=0.8), ev=dict(kind="fault"), t_end=1.7),
    dict(id="T13", group="고장", title="한국 연계기준안 — 고장전류 2.0 pu × 140 ms",
         refs=["한전 GFM 연계기준안 (2026-04 전력전자학회 포럼, 초안)"],
         cond="SCR 3, P₀ = 0.8 pu, PCC 3상 지락(고장 저항 0.05 pu) × 200 ms. I_max 1.2 / 2.0 pu 사양 비교",
         labels=["GFL", "GFM", "GFL (I_max 2.0)", "GFM (I_max 2.0)"], p=dict(scr=3.0, P_ref=0.8),
         ev=dict(kind="pcc_fault"), t_end=1.0),
]


def label_params(label: str, base: dict, tid: str) -> tuple[str, dict]:
    mode = "GFM" if label.startswith("GFM") else "GFL"
    kw = dict(base)
    if mode == "GFL" and tid.startswith("T05"):
        kw["gfl_droop"] = True
    if label == "GFL+SI":
        kw.update(gfl_droop=True, gfl_H_syn=4.0)
    if "I_max 2.0" in label:
        kw["I_max"] = 2.0
    return mode, kw


def scenario(ev: dict, t_end: float) -> Scenario:
    k = ev["kind"]
    d = dict(name=k, t_end=t_end)
    if k == "island":
        d["breaker_closed"] = lambda t: t < T
    elif k == "rocof":
        a = ev["rate"] / F0
        d["grid_f"] = lambda t, a=a: 1.0 + a * min(max(t - T, 0.0), 0.5)
    elif k == "scr_fault":
        d["scr"] = lambda t: 3.0 if t < T else 1.5
        d["grid_v"] = lambda t: 0.3 if T + 0.5 <= t < T + 0.65 else 1.0
    elif k == "phase":
        ph = math.radians(ev["deg"])
        d["grid_phase"] = lambda t, ph=ph: ph if t >= T else 0.0
    elif k == "vstep":
        d["grid_v"] = lambda t, v=ev["v"]: v if t >= T else 1.0
    elif k == "fault":
        d["grid_v"] = lambda t: 0.3 if T <= t < T + 0.15 else 1.0
    elif k == "pcc_fault":
        # 고장 제거는 1 ms 램프 (계단 제거 시 대수 PCC 노드에 비물리적 전압 스파이크가 생김)
        d["pcc_fault_g"] = lambda t: 20.0 if T <= t < T + 0.2 else (20.0 * (1.0 - (t - T - 0.2) / 1e-3) if T + 0.2 <= t < T + 0.201 else 0.0)
    return Scenario(**d)


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------
def _init(a):
    mode, kw, dt = a
    try:
        steady_state(mode, Params(**kw), dt=dt)
    except RuntimeError:
        pass
    return True


def _run(job):
    tid, label, dt = job
    td = next(x for x in TESTS if x["id"] == tid)
    mode, kw = label_params(label, td["p"], tid)
    p = Params(**kw)
    x0 = steady_state(mode, p, dt=dt)
    hires = (T + td["hires"][0], T + td["hires"][1]) if td.get("hires") else None
    r = simulate(mode, p, scenario(td["ev"], td["t_end"]), dt=dt, x0=x0, hires=hires)
    out = {k: np.asarray(v, dtype=float).tolist() for k, v in r.items()
           if isinstance(v, list) and k in ("t", "P", "Q", "V", "I", "freq", "grid_freq", "delta_deg")}
    out["t"] = (np.asarray(out["t"]) - T).tolist()
    if "hires" in r:
        h = r["hires"]
        out["hires"] = {k: (np.asarray(v) - (T if k == "t" else 0.0)).tolist() for k, v in h.items()}
    out["diverged"] = "diverged_at" in r
    out["I_max"] = p.I_max
    return (tid, label), out


# ---------------------------------------------------------------------------
# 판정 도구
# ---------------------------------------------------------------------------
def A(r, k):
    return np.asarray(r[k])


def win(r, k, a, b):
    t = A(r, "t")
    return A(r, k)[(t >= a) & (t < b)]


def at(r, k, tt):
    return float(np.interp(tt, A(r, "t"), A(r, k)))


def damped(r, a):
    """a 이후 진동이 작거나 감쇠 중이면 True (스위칭 에일리어싱 제외, gfm_gfl_emt.oscillation_check)."""
    if r["diverged"]:
        return False
    ok, _ = oscillation_check(A(r, "t"), A(r, "P"), a)
    return ok


def movavg(x, n=200):
    """20 ms 이동평균 (기록 100 µs). 스위칭 에일리어싱 잡음 제거용."""
    x = np.asarray(x)
    return np.convolve(x, np.ones(n) / n, mode="valid") if len(x) > n else x


def crit(name, ref, threshold, values, passes, note=""):
    return dict(name=name, ref=ref, threshold=threshold, values=values, passes=passes, note=note)


def fmt(v, d=3):
    return f"{v:.{d}f}"


def eval_lsm(td, R):
    labs = td["labels"]
    c = []
    vals, ok = {}, {}
    for L in labs:
        r = R[L]
        ok[L] = damped(r, 0.6)
        vals[L] = "감쇠·안정" if ok[L] else "지속 진동/발산"
    c.append(crit("분리 후 안정 운전", "NERC·AEMO 공통", "진동이 감쇠하고 발산하지 않을 것", vals, ok))
    vals, ok = {}, {}
    for L in labs:
        f = movavg(win(R[L], "freq", 1.0, 99))
        fw = movavg(win(R[L], "freq", 0.3, 99))
        fmin, fmax = fw.min(), fw.max()
        vals[L] = f"{f.mean():.2f} Hz (범위 {fmin:.1f}~{fmax:.1f})"
        ok[L] = bool(58.8 <= fmin and fmax <= 61.2)
    c.append(crit("주파수 유지", "본 보고서 기준", "분리 0.3 s 후 58.8~61.2 Hz (±2 %, 20 ms 이동평균)", vals, ok))
    if td["id"] == "T03":
        vals, ok = {}, {}
        for L in labs:
            i = win(R[L], "I", 1.0, 99).mean()
            vals[L] = f"{i:.2f} pu (V {win(R[L], 'V', 1.0, 99).mean():.2f} pu)"
            ok[L] = bool(i <= 1.05 * R[L]["I_max"]) and damped(R[L], 0.6)
        c.append(crit("전류 한계 내 안정 동작", "NERC Test 3·AEMO Test 3", "정상상태 |i| ≤ 1.05 × I_max, 안정 유지 (전압 저하 허용)", vals, ok))
    else:
        vals, ok = {}, {}
        for L in labs:
            v = win(R[L], "V", 1.0, 99)
            vals[L] = f"{v.mean():.3f} pu (범위 {v.min():.2f}~{v.max():.2f})"
            ok[L] = bool(0.9 <= v.min() and v.max() <= 1.1)
        c.append(crit("전압 유지", "본 보고서 기준", "분리 1 s 후 0.9~1.1 pu", vals, ok))
    return c


def eval_rocof(td, R):
    rate = td["ev"]["rate"]
    rocof = rate / F0
    c = []
    vals, ok = {}, {}
    for L in td["labels"]:
        ok[L] = damped(R[L], 1.0)
        vals[L] = "안정" if ok[L] else "불안정"
    c.append(crit("RoCoF 중·후 안정", "AEMO Test 5·ERCOT #5", "동기 유지, 진동 감쇠", vals, ok))
    vals, ok = {}, {}
    for L in td["labels"]:
        r = R[L]
        P0 = win(r, "P", -0.1, 0).mean()
        df_end = rate * 0.5 / F0
        Kd = (win(r, "P", 1.4, 1.8).mean() - P0) / (-df_end)
        dP = at(r, "P", 0.5) - P0
        H = (dP - Kd * (-df_end)) / (-2.0 * rocof)
        vals[L] = f"H_eq {H:.2f} s (드룹 K {Kd:.0f})"
        ok[L] = bool(H >= 2.0)
    c.append(crit("관성 응답 (RoCoF 응답 전력)", "본 보고서 기준 (GB ROCOF Response Power 의도)",
                  "램프 종료 시점 ΔP 에서 드룹 기여를 뺀 등가 관성 H_eq ≥ 2.0 s (설정 H 4 s 의 50 %)", vals, ok,
                  "드룹 이득 K 는 램프 후 정상상태에서 식별. 계통 주파수 기준이라 VSM 의 드룹·관성 결합분만큼 실제 H 보다 작게 나온다."))
    return c


def recovery(r, t_clear, p0):
    t, P = A(r, "t"), A(r, "P")
    out = np.where((t > t_clear) & ((P < 0.9 * p0) | (P > 1.1 * p0)))[0]
    if len(out) == 0:
        return 0.0
    if out[-1] >= len(t) - 1:
        return float("inf")
    return float(t[out[-1]] - t_clear)


def eval_fault(td, R, t_f, dur):
    c = []
    vals, ok = {}, {}
    for L in td["labels"]:
        r = R[L]
        d = A(r, "delta_deg")
        d0 = win(r, "delta_deg", -0.05, 0).mean()
        dd = (d - d0 + 180) % 360 - 180
        sync = (not r["diverged"]) and np.abs(dd).max() < 90 and damped(r, t_f + dur + 0.6)
        ok[L] = bool(sync)
        vals[L] = f"최대 위상 이탈 {np.abs(dd).max():.0f}°" + ("" if sync else ", 불안정")
    c.append(crit("동기 유지", "IEEE 2800·AEMO", "위상 이탈 < 90°, 고장 후 진동 감쇠", vals, ok))
    vals, ok = {}, {}
    for L in td["labels"]:
        rec = recovery(R[L], t_f + dur, 0.8)
        vals[L] = (f"{rec * 1000:.0f} ms" if math.isfinite(rec) else "미회복")
        ok[L] = bool(rec <= 1.0)
    c.append(crit("유효전력 회복", "본 보고서 기준", "고장 제거 후 1.0 s 이내 P₀ ±10 % 정착", vals, ok))
    vals, ok = {}, {}
    for L in td["labels"]:
        vals[L] = f"평균 V {win(R[L], 'V', t_f, t_f + dur).mean():.2f} pu, 최대 |i| {win(R[L], 'I', t_f, t_f + dur).max():.2f} pu"
        ok[L] = None
    c.append(crit("고장 중 전압·전류 (참고)", "—", "고장 구간 평균 PCC 전압, 최대 전류", vals, ok))
    return c


def eval_phase(td, R):
    deg = td["ev"]["deg"]
    sgn = 1.0 if deg < 0 else -1.0
    c = []
    v1, o1, v2, o2, v3, o3 = {}, {}, {}, {}, {}, {}
    for L in td["labels"]:
        r = R[L]
        t, P, V = A(r, "t"), A(r, "P"), A(r, "V")
        P0, V0 = win(r, "P", -0.02, 0).mean(), win(r, "V", -0.02, 0).mean()
        m = (t >= 0) & (t <= 0.05)
        dPs = sgn * (P[m] - P0)
        tm = t[m]
        ia = sgn * (P[m] / np.maximum(V[m], 0.05) - P0 / V0)
        di10 = ia[tm <= 0.010].max()
        v1[L], o1[L] = f"{di10:+.2f} pu", bool(di10 >= 0.25)
        pk = dPs.max()
        if pk < 0.05:
            v2[L], o2[L] = f"응답 없음 (최대 {pk:.3f} pu)", False
            v3[L], o3[L] = "응답 없음", False
        else:
            t90 = tm[np.argmax(dPs >= 0.9 * pk)]
            t50 = tm[np.argmax(dPs >= 0.5 * pk)]
            v2[L], o2[L] = f"{t90 * 1000:.1f} ms (초기 피크 {pk:.2f} pu)", bool(t90 <= 0.015)
            v3[L], o3[L] = f"{t50 * 1000:.1f} ms", bool(t50 <= 0.005)
    c.append(crit("위상점프 유효전류", "ENTSO-E TG GFC", "10 ms 이내 유효전류 변화 ≥ 0.25 pu (시험 하한: 정격의 25 %)", v1, o1))
    c.append(crit("응답 속도", "ERCOT AGS #7", "초기 유효전력 변화의 90 %에 15 ms 이내 도달", v2, o2))
    c.append(crit("자연 응답 개시", "GB GC0137 (본 보고서 해석)", "초기 피크의 50 %에 5 ms 이내 도달 (5 ms 이내 자연 응답)", v3, o3))
    vals, ok = {}, {}
    for L in td["labels"]:
        r = R[L]
        P0 = win(r, "P", -0.02, 0).mean()
        tail = win(r, "P", A(r, "t")[-1] - 0.2, 99).mean()
        ok[L] = damped(r, 0.4) and abs(tail - P0) < 0.1 * max(abs(P0), 0.1)
        vals[L] = f"최종 P {tail:.3f} pu" + ("" if ok[L] else ", 미안정")
    c.append(crit("점프 후 복귀", "공통", "진동 감쇠, 최종 P 가 점프 전 ±10 %", vals, ok))
    return c


def eval_phase60(td, R):
    c = []
    vals, ok = {}, {}
    for L in td["labels"]:
        r = R[L]
        d = A(r, "delta_deg")
        d0 = win(r, "delta_deg", -0.02, 0).mean()
        dd = (d - d0 + 180) % 360 - 180
        end = win(r, "delta_deg", A(r, "t")[-1] - 0.2, 99).mean()
        P0 = win(r, "P", -0.02, 0).mean()
        tail = win(r, "P", A(r, "t")[-1] - 0.2, 99).mean()
        okk = (not r["diverged"]) and np.abs(dd).max() < 180 and abs(((end - d0) + 180) % 360 - 180) < 10 \
            and abs(tail - P0) < 0.1 * P0 and damped(r, 0.5)
        ok[L] = bool(okk)
        i_end = win(r, "I", A(r, "t")[-1] - 0.2, 99).mean()
        stuck = i_end >= 0.98 * r["I_max"]
        why = "" if okk else (f", 전류 제한 고착(끝까지 |i| {i_end:.2f} pu, P {tail:.2f} pu, 위상 {end - d0:+.0f}°)" if stuck else ", 미복귀")
        vals[L] = f"최대 이탈 {np.abs(dd).max():.0f}°, 최대 |i| {win(r, 'I', 0, 0.3).max():.2f} pu" + why
    c.append(crit("60° 점프 후 동기 유지", "GB GC0137 Withstand", "극 미끄럼 없음(최대 이탈 < 180°), 진동 감쇠, 마지막 0.2 s 위상 ±10°·P ±10 %", vals, ok,
                  "GFM 부적합 원인: 전류 제한 중 VSM 가속을 멈추는 보정(gfm_limit_freeze)이 재동기에 필요한 위상 이동까지 막아, "
                  "지속되는 60° 위상차에서 전류 제한 상태에 갇힌다. 고장(T12)은 전압 회복으로 풀리지만 위상 차는 스스로 풀리지 않는다. "
                  "과도 가상 임피던스 등 제한 중에도 전력-위상 관계를 유지하는 방식이 필요하다."))
    return c


def eval_vstep(td, R):
    vals, ok = {}, {}
    for L in td["labels"]:
        r = R[L]
        t, Q = A(r, "t"), A(r, "Q")
        Q0 = win(r, "Q", -0.02, 0).mean()
        dQ = Q - Q0
        q100 = at(r, "Q", 0.1) - Q0
        m = t >= 0
        if q100 < 0.02:
            vals[L], ok[L] = f"응답 미미 (100 ms 시점 ΔQ {q100:.3f} pu)", False
        else:
            t90 = t[m][np.argmax(dQ[m] >= 0.9 * q100)]
            vals[L] = f"{t90 * 1000:.1f} ms (ΔQ@100 ms {q100:.3f} pu)"
            ok[L] = bool(t90 <= 0.030)
    return [crit("무효전류 응답 속도", "ENTSO-E TG GFC", "ΔQ 가 100 ms 시점 값의 90 %에 30 ms 이내 도달", vals, ok)]


def damping_ratio(r, t_skip=0.15):
    """스윙 진동 감쇠비: t_skip 이후 교번 극값의 진폭 로그 기울기 σ 와 주기로 ζ = σ/√(σ²+ω_d²).

    점프 직후 수십 ms 의 전자기 과도(60~80 Hz 감쇠 진동)는 t_skip 으로 제외하고,
    20 ms 이동평균으로 스위칭 잔류 성분을 지운다.
    """
    t, P = A(r, "t"), A(r, "P")
    k = max(1, int(round(0.02 / (t[1] - t[0]))))
    Pf = np.convolve(P, np.ones(k) / k, mode="same")
    m = (t >= t_skip) & (t <= t[-1] - 0.02)
    t, x = t[m], Pf[m] - Pf[m][-int(0.3 / (t[1] - t[0])):].mean()
    if np.abs(x).max() < 0.01:
        return None, None
    ext = []
    for i in range(1, len(x) - 1):
        if (x[i] - x[i - 1]) * (x[i + 1] - x[i]) < 0 and abs(x[i]) > 0.002:
            if ext and np.sign(x[i]) == np.sign(x[ext[-1]]):
                if abs(x[i]) > abs(x[ext[-1]]):
                    ext[-1] = i
                continue
            ext.append(i)
    if len(ext) < 3:
        return None, None
    tk, ak = t[ext], np.log(np.abs(x[ext]))
    sigma = -np.polyfit(tk, ak, 1)[0]
    wd = math.pi / np.mean(np.diff(tk))
    zeta = sigma / math.sqrt(sigma ** 2 + wd ** 2)
    return float(zeta), float(wd / (2 * math.pi))


def eval_damping(td, R):
    vals, ok = {}, {}
    for L in td["labels"]:
        z, f = damping_ratio(R[L])
        if z is None:
            vals[L], ok[L] = "유의한 저주파 진동 없음", True
        else:
            vals[L], ok[L] = f"ζ = {z * 100:.1f} % ({f:.2f} Hz)", bool(z >= 0.05)
    return [crit("저주파 진동 감쇠비", "ENTSO-E TG GFC", "0.1~10 Hz 유효전력 진동 감쇠비 ≥ 5 %", vals, ok,
                 "T07(−20° 점프) 응답에서 점프 후 0.15 s 이후 스윙 극값의 진폭 감소율로 추정 (20 ms 이동평균)")]


def eval_kr(td, R):
    c = []
    vals, ok = {}, {}
    for L in td["labels"]:
        r = R[L]
        t, I = A(r, "t"), A(r, "I")
        m = (t >= 0) & (t < 0.2)
        above = I[m] >= 1.98
        best = run = 0
        for a in above:
            run = run + 1 if a else 0
            best = max(best, run)
        dur = best * (t[1] - t[0])
        vals[L] = f"{dur * 1000:.0f} ms (최대 {I[m].max():.2f} pu)"
        ok[L] = bool(dur >= 0.140)
    c.append(crit("순시 고장전류 크기·지속", "한전 연계기준안(초안)", "|i| ≥ 2.0 pu 를 140 ms 이상 연속 유지", vals, ok))
    vals, ok = {}, {}
    for L in td["labels"]:
        gfm = L.startswith("GFM")
        vals[L] = "전압원 (가상 임피던스 뒤 E∠θ)" if gfm else "전류원 (PLL 기준 전류 지령)"
        ok[L] = gfm
    c.append(crit("고장 시 전압원 동작", "한전 연계기준안(초안)", "고장 중에도 전압원으로 동작 (제어 구조 판정)", vals, ok,
                  "시뮬레이션 지표가 아니라 제어 구조로 판정. GFM 도 전류 제한 중에는 전류 크기가 고정된다."))
    vals, ok = {}, {}
    for L in td["labels"]:
        vals[L] = f"고장 중 평균 V {win(R[L], 'V', 0, 0.2).mean():.3f} pu"
        ok[L] = None
    c.append(crit("고장 중 PCC 전압 (참고)", "—", "고장 저항 0.05 pu, 평균값", vals, ok))
    return c


# ---------------------------------------------------------------------------
def ds(r, keys, t0, t1, n=500):
    t = A(r, "t")
    g = np.linspace(t0, min(t1, t[-1]), n)
    d = {"t": np.round(g, 4).tolist()}
    for k in keys:
        d[k] = np.round(np.interp(g, t, A(r, k)), 4).tolist()
    return d


CHARTS = {
    "T01": [("freq", "인버터 주파수 [Hz]", -0.05, 1.3), ("V", "PCC 전압 [pu]", -0.05, 1.3)],
    "T02": [("freq", "인버터 주파수 [Hz]", -0.05, 1.3), ("P", "유효전력 [pu]", -0.05, 1.3)],
    "T03": [("freq", "인버터 주파수 [Hz]", -0.05, 1.3), ("I", "전류 |i| [pu]", -0.05, 1.3)],
    "T04": [("freq", "인버터 주파수 [Hz]", -0.05, 1.3), ("V", "PCC 전압 [pu]", -0.05, 1.3)],
    "T05a": [("P", "유효전력 [pu]", -0.1, 1.8), ("freq", "인버터 주파수 [Hz]", -0.1, 1.8)],
    "T05b": [("P", "유효전력 [pu]", -0.1, 1.8), ("freq", "인버터 주파수 [Hz]", -0.1, 1.8)],
    "T06": [("P", "유효전력 [pu]", -0.05, 2.0), ("V", "PCC 전압 [pu]", -0.05, 2.0)],
    "T07": [("P", "유효전력, 점프 직후 60 ms [pu]", -0.005, 0.06), ("P", "유효전력, 전체 [pu]", -0.05, 2.5)],
    "T08": [("P", "유효전력, 점프 직후 60 ms [pu]", -0.005, 0.06), ("P", "유효전력, 전체 [pu]", -0.05, 1.0)],
    "T09": [("P", "유효전력 [pu]", -0.05, 1.5), ("delta_deg", "계통 대비 위상 [°]", -0.05, 1.5)],
    "T10": [("Q", "무효전력 [pu]", -0.01, 0.3), ("V", "PCC 전압 [pu]", -0.01, 0.3)],
    "T11": [("P", "유효전력 (T07) [pu]", -0.05, 2.5)],
    "T12": [("V", "PCC 전압 [pu]", -0.05, 1.5), ("P", "유효전력 [pu]", -0.05, 1.5)],
    "T13": [("I", "전류 |i| [pu]", -0.02, 0.5), ("V", "PCC 전압 [pu]", -0.02, 0.5)],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dt", type=float, default=DT_DEFAULT)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--reuse", action="store_true", help="저장된 원시 결과로 판정만 다시 계산")
    args = ap.parse_args()
    dt = args.dt
    raw_path = os.path.join(HERE, ".cache", f"compliance_raw_{dt * 1e6:g}us.pkl")
    jobs, inits = [], {}
    for td in TESTS:
        if td.get("derived"):
            continue
        for L in td["labels"]:
            mode, kw = label_params(L, td["p"], td["id"])
            inits[(mode, tuple(sorted(kw.items())))] = (mode, kw, dt)
            jobs.append((td["id"], L, dt))
    jobs.sort(key=lambda j: -next(x for x in TESTS if x["id"] == j[0])["t_end"])
    print(f"dt = {dt * 1e6:g} µs, 시뮬레이션 {len(jobs)}건, 초기화 {len(inits)}건", flush=True)
    if args.reuse and os.path.exists(raw_path):
        with open(raw_path, "rb") as f:
            res = pickle.load(f)
        print("원시 결과 재사용:", raw_path, flush=True)
    else:
        with ProcessPoolExecutor(args.workers) as ex:
            list(ex.map(_init, inits.values()))
            res = dict(ex.map(_run, jobs))
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        with open(raw_path, "wb") as f:
            pickle.dump(res, f)
    out_tests = []
    for td in TESTS:
        src = td.get("derived", td["id"])
        R = {L: res[(src, L)] for L in td["labels"]}
        g = td["id"]
        if g in ("T01", "T02", "T03", "T04"):
            cr = eval_lsm(td, R)
        elif g.startswith("T05"):
            cr = eval_rocof(td, R)
        elif g == "T06":
            cr = eval_fault(td, R, 0.5, 0.15)
        elif g in ("T07", "T08"):
            cr = eval_phase(td, R)
        elif g == "T09":
            cr = eval_phase60(td, R)
        elif g == "T10":
            cr = eval_vstep(td, R)
        elif g == "T11":
            cr = eval_damping(td, R)
        elif g == "T12":
            cr = eval_fault(td, R, 0.0, 0.15)
        else:
            cr = eval_kr(td, R)
        verdict = {}
        for L in td["labels"]:
            ps = [c["passes"][L] for c in cr if c["passes"][L] is not None]
            verdict[L] = bool(all(ps)) if ps else None
        charts = [dict(key=k, title=ti, series={L: ds(R[L], [k], a, b, 700 if b - a < 0.1 else 500) for L in td["labels"]})
                  for k, ti, a, b in CHARTS[g]]
        item = {k: td[k] for k in ("id", "group", "title", "refs", "cond", "labels")}
        item.update(criteria=cr, verdict=verdict, charts=charts)
        if td.get("hires"):
            h = {L: res[(td["id"], L)].get("hires") for L in td["labels"]}
            item["hires"] = {L: {k: np.round(np.asarray(v)[::5], 4).tolist() for k, v in hh.items() if k in ("t", "ia", "ib", "ic")}
                             for L, hh in h.items() if hh}
        out_tests.append(item)
        print(td["id"], td["title"], {L: ("적합" if v else ("부적합" if v is False else "-")) for L, v in verdict.items()}, flush=True)
    p = Params()
    meta = dict(dt_us=dt * 1e6, f_sw=p.f_sw, f_samp=2 * p.f_sw, V_dc_pu=round(p.V_dc / p.V_base_peak, 3),
                V_conv_max=round(p.V_conv_max, 3), Lf=p.Lf, Cf=p.Cf, Rd=p.Rd, Lt=p.Lt, I_max=p.I_max,
                f_cc=p.f_cc, f_pll=p.f_pll, H=p.H, droop=p.droop, Xv=p.Xv, Rv=p.Rv, converter=p.converter)
    data = dict(meta=meta, tests=out_tests)
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"),
                    default=lambda o: o.item() if hasattr(o, "item") else str(o))
    open(os.path.join(HERE, "results", "compliance.json"), "w", encoding="utf-8").write(js)
    if os.path.exists(REPORT):
        html = open(REPORT, encoding="utf-8").read()
        new, n = re.subn(r"/\*REPORT_DATA_START\*/.*?/\*REPORT_DATA_END\*/",
                         lambda m: "/*REPORT_DATA_START*/" + js + "/*REPORT_DATA_END*/", html, flags=re.S)
        if n:
            open(REPORT, "w", encoding="utf-8").write(new)
            print("보고서 데이터 갱신:", REPORT)


if __name__ == "__main__":
    main()
