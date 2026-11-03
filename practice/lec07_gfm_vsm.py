"""7강 실습 · GFM: 위상을 만들기

실행 (저장소 루트에서):
    python practice/lec07_gfm_vsm.py            # 해석 실습
    python practice/lec07_gfm_vsm.py --plot     # 그림 저장 (practice/out/)
    python practice/lec07_gfm_vsm.py --emt      # EMT(평균값): 위상 점프 GFM vs GFL, 주파수 계단 H 1/4/8 (약 1.5 분)
    python practice/lec07_gfm_vsm.py --answers

실습 목록
    1. P–δ 곡선과 동기화 토크: X = Xv + 1/SCR = 0.633, δ0 18.5°, Ks 1.50, 위상 점프 페이저 근사 0.48 pu
    2. 스윙 모드: ωn = √(ωb·Ks/2H) → 1.34 Hz, ζ = D/(4H·ωn) → 0.37
    3. VSM = 드룹 2 % + LPF: mp = 1/D, ωc = D/2H = 6.25 rad/s (1.0 Hz)
    4. 동적 가상 인덕턴스 시정수 Xv/(ωb·Rv) ≈ 16 ms
    5. (EMT) 위상 점프 −20° GFM +0.64 / GFL +0.007, 주파수 −0.2 Hz 계단: 정상상태 0.169 (드룹 0.167), H별 오버슈트
    해보기 A. SCR 10 에서 스윙 모드 주파수와 감쇠비는?
    해보기 B. Xv = 0.15 로 줄이면 위상 점프 전력이 커질까? (--emt 로 r["sat"] 확인)
"""
import math

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, MUTED

from gfm_gfl_emt import Params

P = Params()
WB = P.wb


def pdelta(scr=P.scr, Xv=P.Xv, P0=P.P_ref, E=1.0, V=1.0):
    """X, δ0, Ks, Pmax."""
    X = Xv + 1 / scr
    d0 = math.asin(P0 * X / (E * V))
    return X, d0, E * V / X * math.cos(d0), E * V / X


def swing_mode(Ks, H=P.H, D=P.D):
    wn = math.sqrt(WB * Ks / (2 * H))
    return wn, D / (4 * H * wn)


def practice_1(args):
    header("실습 1 · P–δ 곡선, 동기화 토크, 위상 점프 페이저 근사")
    X, d0, Ks, Pmax = pdelta()
    dP = (math.sin(d0 + math.radians(20)) - math.sin(d0)) / X
    print(f"  SCR {P.scr}: X = {P.Xv} + {1 / P.scr:.3f} = {X:.3f} pu, δ0 = {math.degrees(d0):.1f}°, Pmax = {Pmax:.2f} pu")
    check("동기화 토크 Ks [pu/rad]", Ks, 1.50, 0.01)
    check("−20° 점프 페이저 ΔP [pu]", dP, 0.482, 0.003)
    if args.plot:
        plt = plt_ready()
        d = np.linspace(0, 180, 361)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(d, np.sin(np.radians(d)) / X, color=BLUE, label=f"P = sin δ / {X:.3f}")
        ax.plot([math.degrees(d0)], [P.P_ref], "o", color=BLUE); ax.plot([math.degrees(d0) + 20], [P.P_ref + dP], "o", color=ORANGE)
        ax.axhline(P.P_ref, color=MUTED, ls=":"); ax.set_xlabel("δ [°]"); ax.set_ylabel("P [pu]"); ax.legend()
        savefig(fig, "lec07_1_P델타.png")


def practice_2(args):
    header("실습 2 · 스윙 모드 (선형화)")
    _, _, Ks, _ = pdelta()
    wn, zeta = swing_mode(Ks)
    print(f"  ωn = √(377 × {Ks:.2f} / (2 × {P.H})) = {wn:.2f} rad/s = {wn / (2 * math.pi):.2f} Hz, ζ = {P.D}/(4 × {P.H} × {wn:.2f}) = {zeta:.2f}")
    check("스윙 모드 주파수 [Hz]", wn / (2 * math.pi), 1.34, 0.02)
    check("감쇠비 ζ", zeta, 0.37, 0.01)


def practice_3(args):
    header("실습 3 · VSM = 드룹 + LPF")
    mp, wc = 1 / P.D, P.D / (2 * P.H)
    print(f"  mp = 1/D = {mp:.3f} ({mp * 100:.0f} %), ωc = D/2H = {wc:.2f} rad/s = {wc / (2 * math.pi):.2f} Hz")
    print(f"  주파수 −0.2 Hz 계단의 정상상태 ΔP = D·Δf/f0 = {P.D * 0.2 / 60:+.3f} pu")
    check("드룹 [%]", mp * 100, 2.0, 0.01)
    check("LPF 차단주파수 [Hz]", wc / (2 * math.pi), 1.0, 0.01)


def practice_4(args):
    header("실습 4 · 동적 가상 인덕턴스")
    tau = P.Xv / (WB * P.Rv)
    print(f"  (Xv/ωb)·di/dt = E − v − Rv·i − jωXv·i → 시정수 Xv/(ωb·Rv) = {tau * 1e3:.1f} ms (전자기 과도)")
    print(f"  정적 가상 임피던스라면 i = (E − v)/({P.Rv} + j{P.Xv}): |Z| = {math.hypot(P.Rv, P.Xv):.3f} pu")
    check("시정수 [ms]", tau * 1e3, 15.9, 0.2)


def practice_5(args):
    header("실습 5 · (EMT 평균값) 위상 점프 GFM vs GFL, 주파수 계단")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 1.5 분).")
        return
    from gfm_gfl_emt import Scenario, simulate, steady_state
    DT = 10e-6
    p = Params(converter="average")                 # 바꿔 보기: Xv=0.15, P_ref=0.8 (해보기 B)
    jump = Scenario(t_end=0.3, grid_phase=lambda t: math.radians(-20) if t >= 0.1 else 0.0)
    res = {}
    for mode in ("GFM", "GFL"):
        r = simulate(mode, p, jump, dt=DT, x0=steady_state(mode, p, dt=DT))
        t, Pw = np.asarray(r["t"]), np.asarray(r["P"])
        P0 = Pw[t < 0.1][-1]
        m10 = (t >= 0.1) & (t <= 0.11)
        dmax, davg = Pw[m10].max() - P0, Pw[(t > 0.11) & (t < 0.13)].mean() - P0
        sat = np.asarray(r["sat"]).any() if "sat" in r else False
        res[mode] = (t, Pw)
        print(f"  {mode}: 10 ms 내 최대 ΔP {dmax:+.3f} pu, 10~30 ms 평균 ΔP {davg:+.3f} pu, 전류 제한 {'걸림' if sat else '없음'}")
        if mode == "GFM":
            check("  GFM 10 ms 내 최대 ΔP [pu]", dmax, 0.636, 0.02)
            check("  GFM 10~30 ms 평균 ΔP [pu]", davg, 0.498, 0.02)
        else:
            check("  GFL 10 ms 내 최대 ΔP [pu]", dmax, 0.007, 0.005)
    step = Scenario(t_end=2.0, grid_f=lambda t: 1.0 - 0.2 / 60 if t >= 0.1 else 1.0)
    out = {}
    for H in (1.0, 4.0, 8.0):
        pH = Params(converter="average", H=H)
        r = simulate("GFM", pH, step, dt=DT, x0=steady_state("GFM", pH, dt=DT))
        t, Pw = np.asarray(r["t"]), np.asarray(r["P"])
        P0 = Pw[t < 0.1][-1]
        out[H] = (t, Pw, Pw[t > 1.8].mean() - P0, Pw.max() - P0)
        print(f"  H = {H:.0f} s: 정상상태 ΔP {out[H][2]:+.3f} pu (드룹 예측 {pH.D * 0.2 / 60:+.3f}), 최대 ΔP {out[H][3]:+.3f} pu")
    check("H 4 s 정상상태 ΔP [pu]", out[4.0][2], 0.169, 0.005)
    check("H 4 s 최대 ΔP [pu]", out[4.0][3], 0.287, 0.01)
    if args.plot:
        plt = plt_ready()
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 7))
        for (mode, (t, Pw)), c in zip(res.items(), (BLUE, ORANGE)):
            a1.plot((t - 0.1) * 1e3, Pw, color=c, label=mode)
        a1.set_xlabel("위상 점프 후 시간 [ms]"); a1.set_ylabel("P [pu]"); a1.legend()
        for (H, (t, Pw, _, _)), c in zip(out.items(), (GREEN, BLUE, ORANGE)):
            a2.plot((t - 0.1) * 1e3, Pw, color=c, label=f"H = {H:.0f} s")
        a2.axhline(0.5 + 50 * 0.2 / 60, color="#c8323c", ls=":"); a2.set_xlabel("주파수 계단 후 시간 [ms]"); a2.set_ylabel("P [pu]"); a2.legend()
        savefig(fig, "lec07_5_위상점프_주파수계단.png")


def try_a(args):
    header("해보기 A · SCR 10 에서 스윙 모드")
    _, _, Ks, _ = pdelta(scr=10)                  # 바꿔 보기: scr
    wn, zeta = swing_mode(Ks)
    print(f"  SCR 10: X = {P.Xv + 0.1:.2f}, Ks = {Ks:.2f} → {wn / (2 * math.pi):.2f} Hz, ζ = {zeta:.2f}")
    if args.answers:
        print("  답: 약 1.7 Hz, ζ ≈ 0.29. 강계통일수록 Ks 가 커져 스윙이 빨라지고 감쇠는 나빠진다 (8강: GFM 의 강계통 쪽 문제).")


def try_b(args):
    header("해보기 B · Xv = 0.15 이면 위상 점프 전력이 커질까?")
    X, d0, _, _ = pdelta(Xv=0.15)                 # 바꿔 보기: Xv
    dP = (math.sin(d0 + math.radians(20)) - math.sin(d0)) / X
    print(f"  페이저 근사: X = {X:.3f}, ΔP = {dP:.2f} pu (0.3 일 때 0.48)")
    if args.answers:
        print("  답: 페이저 식으로는 0.66 pu 로 커져야 하지만, 모델의 10 ms 최대 ΔP 는 오히려 약 0.51 pu 로 준다.")
        print("      Params(converter='average', Xv=0.15) 로 --emt 를 돌려 r['sat'] 을 보면 전류가 1.2 pu 한계에 걸린다. 과부하 정격이 먼저 막는다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, try_a, try_b):
        fn(args)
