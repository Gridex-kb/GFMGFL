"""9강 실습 · 전류 제한과 고장

실행 (저장소 루트에서):
    python practice/lec09_current_limit.py            # 해석 실습
    python practice/lec09_current_limit.py --plot     # 그림 저장 (practice/out/)
    python practice/lec09_current_limit.py --emt      # EMT(평균값): 보정 유무 고장 응답, PCC 지락 1.2/2.0 pu (약 2 분)
    python practice/lec09_current_limit.py --answers

실습 목록
    1. 고장 시 가상 임피던스 전류 |i*| ≈ |E − v|/|Zv| (PCC 0.15 pu → 2.8 pu, 0.4 pu → 2.0 pu)
    2. 원형 포화: 요구 전류를 1.2 pu 원 위로 (각도 유지), 전력 상한 P ≤ |v|·I_max
    3. 평형점 조건 E·Vg/X ≥ P*: Vg 1.0 → 1.36, 0.3 → 0.41 < 0.8
    4. 고장전류 2.0 pu 의 전압 여유 |v_conv| ≈ 0.15 + 0.3 × 2.0 = 0.75 < 1.303
    5. (EMT) 계통 전압 0.3 pu × 150 ms: GFM 보정/보정 없음/GFL (위상 이탈·포화·회복), PCC 지락 I_max 1.2/2.0
    해보기 A. H 를 4 → 2 s 로 줄이면 회복 시간과 고장 후 스윙은? (--emt)
    해보기 B. 고장 컨덕턴스 20 → 3 pu 로 낮추면 1.2 pu 사양이 한계 안에 머무나? (--emt)
"""
import math

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, MUTED

from gfm_gfl_emt import Params

P = Params()
ZV = math.hypot(P.Rv, P.Xv)


def fault_current(v, E=1.0, Zv=ZV):
    return abs(E - v) / Zv


def circular_sat(i_req, I_max=P.I_max):
    m = abs(i_req)
    return i_req * I_max / m if m > I_max else i_req


def practice_1(args):
    header("실습 1 · 고장 시 가상 임피던스 전류")
    print(f"  |Zv| = √({P.Rv}² + {P.Xv}²) = {ZV:.3f} pu, E = 1")
    for v in (0.85, 0.6, 0.4, 0.15):
        print(f"  PCC 전압 {v:.2f} pu → |i*| ≈ (1 − {v:.2f})/{ZV:.3f} = {fault_current(v):.2f} pu" + ("  (> 1.2 포화)" if fault_current(v) > P.I_max else ""))
    check("PCC 0.15 pu 요구 전류 [pu]", fault_current(0.15), 2.8, 0.05)
    check("PCC 0.4 pu 요구 전류 (Xv 만) [pu]", (1 - 0.4) / P.Xv, 2.0, 0.01)


def practice_2(args):
    header("실습 2 · 원형 포화와 전력 상한")
    req = complex(1.6, -2.2)
    lim = circular_sat(req)
    print(f"  요구 {req:.2f} (|i| {abs(req):.2f}) → 제한 {lim:.2f} (|i| {abs(lim):.2f}), 각도 {math.degrees(math.atan2(req.imag, req.real)):.1f}° → {math.degrees(math.atan2(lim.imag, lim.real)):.1f}° (유지)")
    for v in (0.3, 0.4, 0.6):
        print(f"  |v| = {v}: P ≤ |v|·I_max = {v * P.I_max:.2f} pu" + ("  < P* 0.8 → VSM 가속 원인" if v * P.I_max < 0.8 else ""))
    check("제한 후 크기 [pu]", abs(lim), 1.2, 1e-6)
    check("|v| 0.4 전력 상한 [pu]", 0.4 * P.I_max, 0.48, 0.001)


def practice_3(args):
    header("실습 3 · 평형점 조건 E·Vg/X ≥ P*")
    X = P.Xv + P.Lt + 1 / 3
    for Vg in (1.0, 0.6, 0.3):
        pmax = Vg / X
        print(f"  Vg = {Vg}: Pmax = {pmax:.2f} pu → {'평형점 있음' if pmax >= 0.8 else '평형점 없음 (δ 가속)'}")
    check("X = Xv + Lt + 1/SCR [pu]", X, 0.733, 0.001)
    check("Vg 0.3 Pmax [pu]", 0.3 / X, 0.41, 0.01)
    if args.plot:
        plt = plt_ready()
        d = np.linspace(0, 180, 361)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for Vg, c in ((1.0, BLUE), (0.3, ORANGE)):
            ax.plot(d, Vg / X * np.sin(np.radians(d)), color=c, label=f"Vg = {Vg}")
        ax.axhline(0.8, color=MUTED, ls="--", label="P* = 0.8"); ax.set_xlabel("δ [°]"); ax.set_ylabel("P [pu]"); ax.legend()
        savefig(fig, "lec09_3_평형점.png")


def practice_4(args):
    header("실습 4 · 2.0 pu 고장전류의 전압 여유")
    vconv = 0.15 + (P.Lf + P.Lt) * 2.0
    print(f"  |v_conv| ≈ |v| + X(Lf+Lt)·|i| = 0.15 + {P.Lf + P.Lt:.1f} × 2.0 = {vconv:.2f} pu < 최대 {P.V_conv_max:.3f} pu → 변조 여유 남음")
    print("  → 2.0 pu·140 ms 요건의 부담은 전압이 아니라 전류(열) 정격 쪽")
    check("|v_conv| [pu]", vconv, 0.75, 0.01)


def practice_5(args):
    header("실습 5 · (EMT 평균값) 보정 유무 고장 응답, PCC 지락 전류 정격")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 2 분).")
        return
    from gfm_gfl_emt import Scenario, simulate, steady_state
    T, DT = 0.2, 10e-6
    sc = Scenario(t_end=1.7, grid_v=lambda t: 0.3 if T <= t < T + 0.15 else 1.0)
    res = {}
    for name, mode, kw in (("GFM 보정", "GFM", {}), ("GFM 보정 없음", "GFM", dict(gfm_limit_freeze=False)), ("GFL", "GFL", {})):
        p = Params(converter="average", P_ref=0.8, scr=3.0, **kw)      # 바꿔 보기: H=2.0 (해보기 A)
        r = simulate(mode, p, sc, dt=DT, x0=steady_state(mode, p, dt=DT))
        t = np.asarray(r["t"]) - T
        d = np.asarray(r["delta_deg"]); d -= d[(t > -0.05) & (t < 0)].mean()
        sat = np.asarray(r["sat"]); Pw = np.asarray(r["P"]); V = np.asarray(r["V"])
        sat_end = t[(sat > 0.5) & (t > 0.15)].max(initial=0.15) - 0.15
        off = np.where((t > 0.15) & (np.abs(Pw - 0.8) > 0.08))[0]
        rec = t[off[-1]] - 0.15 if len(off) else 0.0
        m = (t >= 0) & (t < 0.15)
        res[name] = (t, Pw, rec)
        print(f"  {name:12s}: 최대 위상 이탈 {np.abs(d).max():5.1f}°, 제거 후 포화 {sat_end * 1e3:4.0f} ms, P 회복 {rec * 1e3:4.0f} ms, 고장 중 평균 V {V[m].mean():.2f} pu")
    check("GFM 보정 회복 [ms]", res["GFM 보정"][2] * 1e3, 482, 30)
    check("GFM 보정 없음 회복 [ms]", res["GFM 보정 없음"][2] * 1e3, 673, 30)
    check("GFL 회복 [ms]", res["GFL"][2] * 1e3, 110, 30)

    sc2 = Scenario(t_end=0.6, pcc_fault_g=lambda t: 20.0 if T <= t < T + 0.2 else 0.0)   # 바꿔 보기: 20 → 3 (해보기 B)

    def longest_run(mask, step):
        best = run = 0
        for mm in mask:
            run = run + 1 if mm else 0
            best = max(best, run)
        return best * step

    for mode in ("GFL", "GFM"):
        for imax in (1.2, 2.0):
            p = Params(converter="average", P_ref=0.8, scr=3.0, I_max=imax)
            r = simulate(mode, p, sc2, dt=DT, x0=steady_state(mode, p, dt=DT))
            t, I, V = (np.asarray(r[k]) for k in ("t", "I", "V"))
            t = t - T
            m = (t >= 0) & (t < 0.2)
            dur = longest_run(I[m] >= 1.98, t[1] - t[0])
            print(f"  {mode} I_max {imax}: 고장 중 |i| 최대 {I[m].max():.2f} pu, 2.0 pu 이상 {dur * 1e3:3.0f} ms, PCC 전압 평균 {V[m].mean():.2f} pu")
            if imax == 2.0:
                check(f"  {mode} 2.0 pu 유지 [ms] ≥ 140", min(dur * 1e3, 140.0), 140.0, 0.5)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for (name, (t, Pw, _)), c in zip(res.items(), (BLUE, GREEN, ORANGE)):
            ax.plot(t, Pw, color=c, label=name)
        ax.axvspan(0, 0.15, color=MUTED, alpha=0.15); ax.set_xlim(-0.05, 1.3); ax.set_xlabel("고장 시작 후 시간 [s]"); ax.set_ylabel("P [pu]"); ax.legend()
        savefig(fig, "lec09_5_고장응답.png")


def try_a(args):
    header("해보기 A · H 를 4 → 2 s")
    print("  practice_5 의 Params(...) 에 H=2.0 을 넣고 회복 시간과 고장 후 스윙을 비교한다 (--emt).")
    if args.answers:
        print("  답: 관성이 작아져 위상 복귀가 빨라지고 회복 시간이 줄지만, 고장 후 스윙 진폭은 커진다 (ωn ∝ 1/√H, ζ ∝ 1/√H).")


def try_b(args):
    header("해보기 B · 고장 컨덕턴스 20 → 3 pu")
    print("  pcc_fault_g 를 3.0 으로 낮춰(고장 저항 증가) 1.2 pu 사양의 전류가 한계 안에 머무는지 본다 (--emt).")
    if args.answers:
        print("  답: 고장 저항이 커지면 PCC 전압이 덜 떨어져 요구 전류가 1.2 pu 안에 머무는 조건이 생긴다. 그 경우 GFM 은 전압원 그대로다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, try_a, try_b):
        fn(args)
