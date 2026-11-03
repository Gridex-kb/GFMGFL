"""10강 실습 · 표준 시험으로 비교

실행 (저장소 루트에서):
    python practice/lec10_compliance.py            # 보고서 JSON 훑기 + 지표 재계산
    python practice/lec10_compliance.py --plot     # 그림 저장 (practice/out/)
    python practice/lec10_compliance.py --emt      # EMT(평균값): T10 전압 스텝·T07 위상 점프를 보고서 판정 함수로 (약 2 분)
    python practice/lec10_compliance.py --answers

실습 목록
    1. 보고서 JSON(simulation/emt/results/compliance.json) 판정표: GFM 12/14, GFL 3/14 와 부적합 항목
    2. 위상점프 전력 예상 ΔP ≈ (E Vg/X)[sin(δ0 − Δθ) − sin δ0] = 0.40 pu vs T07 GFM 초기 피크 0.64, 세 시간 기준
    3. RoCoF 관성 전력 0.133 pu 와 등가 관성 H_eq (T05a: GFM 3.44 / GFL+SI 1.09 / GFL −2.86 s)
    4. 감쇠비 ζ = Λ/√(π² + Λ²): T11 GFM 30.7 % (반주기 비 0.36), 퀴즈 0.6 → 16 %
    5. T13 2.0 pu 지속 시간(197/199 ms)과 T01 분리 후 주파수 60[1 + 0.02(P* − P_load)]
    6. (EMT) T10·T07 을 평균값 모델로 돌려 보고서 판정 함수(ct.eval_vstep, ct.eval_phase)로 지표 계산
    해보기 A. T07 에서 GFL 의 f_pll 을 20 → 50 Hz 로 올리면 세 기준은? (--emt)
    해보기 B. T01 에서 GFM 의 droop 을 0.02 → 0.04 로 바꾸면 분리 후 주파수는?
"""
import json
import math
import os

import numpy as np

from common import ROOT, header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, MUTED

JSON_PATH = os.path.join(ROOT, "simulation", "emt", "results", "compliance.json")
D = json.load(open(JSON_PATH, encoding="utf-8"))
TESTS = {t["id"]: t for t in D["tests"]}
MARK = {True: "적합", False: "부적합", None: "참고"}


def series(tid, idx, label):
    """보고서 그래프 계열 (500점으로 줄인 것). (t, y)"""
    c = TESTS[tid]["charts"][idx]
    return np.asarray(c["series"][label]["t"]), np.asarray(c["series"][label][c["key"]])


def practice_1(args):
    header("실습 1 · 보고서 판정표 (스위칭 모델 2 µs)")
    print(f"  해석 간격 {D['meta']['dt_us']:g} µs, f_sw {D['meta']['f_sw']:.0f} Hz, SCR·P* 는 시험별")
    cnt = {}
    print(f"  {'ID':5} {'시험':34} " + " ".join(f"{L:>14}" for L in ("GFL", "GFM")))
    for t in D["tests"]:
        row = []
        for L in ("GFL", "GFM"):
            v = t["verdict"].get(L)
            cnt.setdefault(L, [0, 0]); cnt[L][0] += bool(v); cnt[L][1] += 1
            row.append(f"{MARK[v]:>14}")
        print(f"  {t['id']:5} {t['title'][:32]:34} " + " ".join(row))
    print("  적합 수:", ", ".join(f"{L} {a}/{b}" for L, (a, b) in cnt.items()))
    print("  GFM 부적합: " + ", ".join(f"{t['id']}" for t in D["tests"] if t["verdict"].get("GFM") is False))
    print("  GFL 적합  : " + ", ".join(f"{t['id']}" for t in D["tests"] if t["verdict"].get("GFL")))
    check("GFM 적합 수", cnt["GFM"][0], 12, 0)
    check("GFL 적합 수", cnt["GFL"][0], 3, 0)
    # 부적합 하나는 여러 항목 중 하나만 어긋나도 붙는다: T09 GFM 의 근거 항목을 읽어 본다
    c = TESTS["T09"]["criteria"][0]
    print(f"  T09 GFM 근거: {c['values']['GFM']}")


def phase_jump_dP(P0, dtheta_deg, X, E=1.0, Vg=1.0):
    d0 = math.asin(P0 * X / (E * Vg))
    return E * Vg / X * (math.sin(d0 - math.radians(dtheta_deg)) - math.sin(d0)), math.degrees(d0)


def practice_2(args):
    header("실습 2 · 위상점프 전력 예상과 세 시간 기준 (T07)")
    X = 0.3 + 0.1 + 1 / 3
    dP, d0 = phase_jump_dP(0.5, -20.0, X)
    print(f"  X = Xv + Lt + 1/SCR = {X:.3f}, δ0 = arcsin(0.5 × {X:.3f}) = {d0:.1f}°")
    print(f"  Δθ = −20°: ΔP ≈ {1 / X:.2f}[sin({d0 + 20:.1f}°) − sin({d0:.1f}°)] = {dP:.2f} pu")
    t, P = series("T07", 0, "GFM")
    P0 = P[(t >= -0.005) & (t < 0)].mean()
    m = (t >= 0) & (t <= 0.05)
    pk = (P[m] - P0).max()
    t50 = t[m][np.argmax(P[m] - P0 >= 0.5 * pk)] * 1e3
    t90 = t[m][np.argmax(P[m] - P0 >= 0.9 * pk)] * 1e3
    print(f"  T07 GFM (보고서 계열): 초기 피크 ΔP {pk:.2f} pu, 50 % {t50:.1f} ms (GB ≤ 5), 90 % {t90:.1f} ms (ERCOT ≤ 15)")
    print("  → 페이저 예상 0.40 보다 큰 이유: PCC 분로·전자기 과도가 더해지고, 전류 루프가 서브사이클로 따라간다")
    tl, Pl = series("T07", 0, "GFL")
    print(f"  T07 GFL: 50 ms 안 최대 ΔP {(Pl[(tl >= 0) & (tl <= 0.05)] - Pl[(tl < 0)].mean()).max():.3f} pu → 응답 없음 (PLL 을 거쳐야 지령이 바뀐다)")
    check("ΔP 예상 [pu]", dP, 0.40, 0.01)
    check("GFM 초기 피크 [pu]", pk, 0.64, 0.02)
    check("GFM 90 % 도달 [ms]", t90, 8.4, 0.5)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(t * 1e3, P, color=BLUE, label="GFM"); ax.plot(tl * 1e3, Pl, color=ORANGE, label="GFL")
        for x, c in ((5, GREEN), (10, MUTED), (15, MUTED)):
            ax.axvline(x, color=c, ls="--", lw=1)
        ax.set_xlim(-5, 60); ax.set_xlabel("점프 후 시간 [ms]"); ax.set_ylabel("P [pu]"); ax.legend()
        savefig(fig, "lec10_2_위상점프.png")


def practice_3(args):
    header("실습 3 · RoCoF 관성 전력과 등가 관성 (T05a)")
    H, rocof, f0 = 4.0, -1.0, 60.0
    dP_in = -2 * H * rocof / f0
    print(f"  ΔP_관성 = −2H·RoCoF/f0 = −2 × {H} × ({rocof}/{f0}) = {dP_in:.3f} pu")
    for L in ("GFL", "GFL+SI", "GFM"):
        t, P = series("T05a", 0, L)
        P0 = P[(t >= -0.1) & (t < 0)].mean()
        df_end = rocof * 0.5 / f0                      # 램프 끝 Δf (pu)
        K = (P[(t >= 1.4) & (t < 1.8)].mean() - P0) / (-df_end)
        dP = np.interp(0.5, t, P) - P0
        H_eq = (dP - K * (-df_end)) / (-2 * rocof / f0)
        rep = TESTS["T05a"]["criteria"][1]["values"][L]
        print(f"  {L:7}: ΔP(0.5 s) {dP:+.3f} pu, 드룹 K {K:.0f} → H_eq {H_eq:.2f} s (보고서 {rep})")
    print("  → 드룹만 있는 GFL 은 램프 중 출력이 늦게 따라와 H_eq 가 음수, GFL+SI(합성 관성)도 측정 지연 때문에 1 s 남짓")
    check("관성 전력 [pu]", dP_in, 0.133, 0.001)


def damping_ratio(ratio_half):
    lam = math.log(1 / ratio_half)
    return lam / math.sqrt(math.pi ** 2 + lam ** 2)


def practice_4(args):
    header("실습 4 · 감쇠비 ζ = Λ/√(π² + Λ²) (T11)")
    z = 0.307
    lam = math.pi * z / math.sqrt(1 - z ** 2)
    print(f"  보고서 T11 GFM ζ = {z * 100:.1f} % → Λ = πζ/√(1−ζ²) = {lam:.2f}, 반주기 진폭 비 e^−Λ = {math.exp(-lam):.2f}")
    print(f"  기준 ζ = 5 % → 반주기 진폭 비 {math.exp(-math.pi * 0.05 / math.sqrt(1 - 0.05 ** 2)):.2f}")
    # 보고서 계열에서 극값 비로 직접 확인 (20 ms 이동평균, 0.15 s 이후, 문턱 0.01)
    t, P = series("T11", 0, "GFM")
    k = max(1, int(round(0.02 / (t[1] - t[0]))))
    Pf = np.convolve(P, np.ones(k) / k, mode="same")
    m = (t >= 0.15) & (t <= t[-1] - 0.1)
    tt, x = t[m], Pf[m] - Pf[m][-60:].mean()
    ext = []
    for i in range(1, len(x) - 1):
        if (x[i] - x[i - 1]) * (x[i + 1] - x[i]) < 0 and abs(x[i]) > 0.01:
            if ext and np.sign(x[i]) == np.sign(x[ext[-1]]):
                if abs(x[i]) > abs(x[ext[-1]]):
                    ext[-1] = i
                continue
            ext.append(i)
    amps = np.abs(x[ext])
    ratios = amps[1:] / amps[:-1]
    print("  극값:", ", ".join(f"{tt[i]:.2f} s {x[i]:+.3f}" for i in ext), "→ 반주기 비", np.round(ratios, 2))
    zeta = damping_ratio(float(ratios.mean()))
    print(f"  반주기 비 평균 {ratios.mean():.2f} → ζ ≈ {zeta * 100:.0f} %, 주기 {2 * np.mean(np.diff(tt[ext])):.2f} s → {1 / (2 * np.mean(np.diff(tt[ext]))):.2f} Hz")
    check("극값 비로 구한 ζ [%]", zeta * 100, 30.7, 4.0)
    check("퀴즈: 반주기 비 0.6 → ζ", damping_ratio(0.6), 0.16, 0.005)


def practice_5(args):
    header("실습 5 · T13 2.0 pu 지속 시간, T01 분리 후 주파수")
    for L in TESTS["T13"]["labels"]:
        t, I = series("T13", 0, L)
        m = (t >= 0) & (t < 0.2)
        best = run = 0
        for a in I[m] >= 1.98:
            run = run + 1 if a else 0
            best = max(best, run)
        dur = best * (t[1] - t[0]) * 1e3
        print(f"  {L:16}: 2.0 pu 이상 {dur:3.0f} ms (보고서 {TESTS['T13']['criteria'][0]['values'][L]}) — 계열이 1 ms 간격이라 몇 ms 짧게 나온다")
    print("  전압원 동작 항목: " + ", ".join(f"{L} {MARK[v]}" for L, v in TESTS["T13"]["criteria"][1]["passes"].items()))
    for tid, Pr, Pl in (("T01", 0.5, 0.8), ("T02", -0.3, 0.5)):
        f = 60 * (1 + 0.02 * (Pr - Pl))
        t, fr = series(tid, 0, "GFM")
        print(f"  {tid} GFM: 60[1 + 0.02({Pr} − {Pl})] = {f:.2f} Hz, 보고서 계열 1 s 후 평균 {fr[t >= 1.0].mean():.2f} Hz")
    check("T01 분리 후 주파수 [Hz]", 60 * (1 + 0.02 * (0.5 - 0.8)), 59.64, 0.01)
    t, fr = series("T01", 0, "GFM")
    check("T01 보고서 계열 평균 [Hz]", float(fr[t >= 1.0].mean()), 59.6, 0.1)


def practice_6(args):
    header("실습 6 · (EMT 평균값) T10 전압 스텝·T07 위상 점프를 보고서 판정 함수로")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 2 분).")
        return
    import compliance_tests as ct
    from gfm_gfl_emt import Params, simulate, steady_state
    DT = 10e-6
    out = {}
    for tid, evalf, t_end in (("T10", ct.eval_vstep, 0.8), ("T07", ct.eval_phase, 1.2)):
        td = dict(next(x for x in ct.TESTS if x["id"] == tid))
        print(f"  {tid} {td['title']} | {td['cond']}")
        R = {}
        for L in td["labels"]:
            mode, kw = ct.label_params(L, td["p"], td["id"])
            # 해보기 A: if mode == "GFL": kw["f_pll"] = 50.0
            p = Params(converter="average", **kw)
            r = simulate(mode, p, ct.scenario(td["ev"], t_end), dt=DT, x0=steady_state(mode, p, dt=DT))
            R[L] = {k: np.asarray(v) for k, v in r.items() if isinstance(v, list)}
            R[L]["t"] = R[L]["t"] - ct.T
            R[L]["diverged"], R[L]["I_max"] = "diverged_at" in r, p.I_max
        for c in evalf(td, R):
            print(f"    - {c['name']} / {c['threshold']}")
            for L, v in c["values"].items():
                print(f"        {L:4} {v}  [{MARK[c['passes'][L]]}]")
        out[tid] = R
    # 평균값 모델 결과를 보고서(스위칭 2 µs)와 비교: 같은 결론이어야 한다
    R = out["T10"]
    t, Q = R["GFM"]["t"], R["GFM"]["Q"]
    Q0 = Q[(t >= -0.02) & (t < 0)].mean(); q100 = np.interp(0.1, t, Q) - Q0
    t90 = t[t >= 0][np.argmax((Q - Q0)[t >= 0] >= 0.9 * q100)] * 1e3
    check("T10 GFM 무효전력 90 % 도달 [ms] (기준 ≤ 30)", t90, 4.3, 3.0)
    R = out["T07"]
    t, P = R["GFM"]["t"], R["GFM"]["P"]
    P0 = P[(t >= -0.02) & (t < 0)].mean(); m = (t >= 0) & (t <= 0.05)
    pk = (P[m] - P0).max()
    check("T07 GFM 초기 피크 ΔP [pu]", pk, 0.64, 0.12)
    check("T07 GFM 90 % 도달 [ms] (기준 ≤ 15)", t[m][np.argmax(P[m] - P0 >= 0.9 * pk)] * 1e3, 8.4, 2.0)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for L, c in (("GFM", BLUE), ("GFL", ORANGE)):
            ax.plot(out["T07"][L]["t"] * 1e3, out["T07"][L]["P"], color=c, label=L)
        ax.set_xlim(-5, 60); ax.set_xlabel("점프 후 시간 [ms]"); ax.set_ylabel("P [pu] (평균값 10 µs)"); ax.legend()
        savefig(fig, "lec10_6_T07_평균값.png")


def try_a(args):
    header("해보기 A · T07 에서 GFL 의 f_pll 20 → 50 Hz")
    print("  practice_6 의 주석(kw['f_pll'] = 50.0)을 풀고 --emt 로 세 기준(5/10/15 ms)을 다시 본다.")
    if args.answers:
        print("  답: PLL 이 빨라져 복귀는 빨라지지만, 10 ms 안의 유효전류 변화와 5 ms 자연 응답은 여전히 거의 0 이다. 측정을 거쳐야 하는 구조는 안 바뀐다 (교재 C12 3.3).")


def try_b(args):
    header("해보기 B · T01 에서 GFM 의 droop 0.02 → 0.04")
    print("  분리 후 주파수 f = f0[1 + droop(P* − P_load)] 로 예측하고, compliance_tests 의 T01 을 droop=0.04 로 돌려 비교한다.")
    if args.answers:
        print(f"  답: 60[1 + 0.04(0.5 − 0.8)] = {60 * (1 + 0.04 * (0.5 - 0.8)):.2f} Hz. 드룹이 크면 부하 불일치가 더 큰 주파수 편차로 나타난다 (0.02 일 때 59.64 Hz).")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, practice_6, try_a, try_b):
        fn(args)
