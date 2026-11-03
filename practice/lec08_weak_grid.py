"""8강 실습 · 약계통과 제어 상호작용

실행 (저장소 루트에서):
    python practice/lec08_weak_grid.py            # 해석 실습
    python practice/lec08_weak_grid.py --plot     # 그림 저장 (practice/out/)
    python practice/lec08_weak_grid.py --emt      # EMT(평균값): 선로 트립 SCR 5 → 1.5/1.3, 판정 5건 (약 2 분)
    python practice/lec08_weak_grid.py --answers

실습 목록
    1. SCR 과 계통 임피던스: Zg = 1/SCR (SCR 1.5 → 0.667, X/R 10), 두 대면 SCR 절반
    2. GFL 정적 운전점: sin δ = Xg·id, PLL 유효 이득 cos δ, 평형점이 사라지는 SCR = id
    3. 음저항 크기 −V²/P (P 0.8 → −1.25 pu)
    4. GFM 전력 루프 감쇠비 vs SCR (Xv 0.3: SCR 3 → 0.36, SCR 20 → 0.27; Xv 0.03: SCR 20 → 0.13)
    5. (EMT) 선로 트립 판정: GFL 20/50/10 Hz, GFM — 진동 유무·주파수 (90 Hz 상호작용형, 10 Hz 동기화 상실형)
    해보기 A. 20 Hz GFL 은 SCR 1.5 → 1.4 → 1.3 중 어디서 무너지나? (--emt)
    해보기 B. 강계통(SCR 10) GFM 의 P 계단 오버슈트: Xv 0.3 vs 0.05 (--emt)
"""
import math

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, MUTED

from gfm_gfl_emt import Params

P = Params()
WB = P.wb


def grid_z(scr, xr=10.0):
    z = 1 / scr
    x = z * xr / math.hypot(xr, 1)
    return z, x, x / xr


def pll_gain(scr, id_=0.8, vg=1.0):
    s = min(1.0, id_ / (scr * vg))
    return math.degrees(math.asin(s)), math.sqrt(max(0.0, 1 - s * s))


def gfm_zeta(scr, Xv=P.Xv, H=P.H, D=P.D):
    Ks = 1 / (Xv + 1 / scr)
    wn = math.sqrt(WB * Ks / (2 * H))
    return D / (4 * H * wn), wn / (2 * math.pi)


def practice_1(args):
    header("실습 1 · SCR 과 계통 임피던스")
    for scr in (5, 3, 2, 1.5):
        z, x, r = grid_z(scr)
        print(f"  SCR {scr:>4}: |Zg| = {z:.3f}, Xg = {x:.3f}, Rg = {r:.3f} pu (모델 근사: Xg = {1 / scr:.3f})")
    z, x, r = grid_z(1.5)
    check("SCR 1.5 |Zg| [pu]", z, 0.667, 0.001)
    check("SCR 1.5 Xg [pu]", x, 0.663, 0.002)
    print("  같은 연계점에 같은 용량 한 대 더 → 정격 두 배 → SCR 1.5 → 0.75")


def practice_2(args):
    header("실습 2 · GFL 정적 운전점과 PLL 유효 이득 (id = 0.8 pu)")
    for scr in (5, 3, 2, 1.5, 1.2, 1.0, 0.8):
        d, c = pll_gain(scr)
        print(f"  SCR {scr:>4}: δ = {d:5.1f}°, cos δ = {c:.2f}" + ("  ← 평형점 소멸" if c == 0 else ""))
    check("SCR 1.5 운전점 각 [°]", pll_gain(1.5)[0], 32.2, 0.2)
    check("평형점이 사라지는 SCR (= id)", 0.8, 0.8, 0.01)
    if args.plot:
        plt = plt_ready()
        scr = np.linspace(0.8, 10, 400)
        c = [pll_gain(s)[1] for s in scr]; d = [pll_gain(s)[0] / 90 for s in scr]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.semilogx(scr, c, color=ORANGE, label="PLL 유효 이득 cos δ"); ax.semilogx(scr, d, color=BLUE, ls="--", label="δ / 90°")
        ax.set_xlabel("SCR"); ax.legend()
        savefig(fig, "lec08_2_유효이득.png")


def practice_3(args):
    header("실습 3 · 음저항")
    for Pw in (0.3, 0.5, 0.8, 1.0):
        print(f"  P = {Pw} pu: R_eq ≈ −V²/P = {-1 / Pw:.2f} pu (PLL 대역 안)")
    check("P 0.8 pu 음저항 [pu]", -1 / 0.8, -1.25, 0.001)


def practice_4(args):
    header("실습 4 · GFM 전력 루프 감쇠비 vs SCR (선형 근사)")
    for Xv in (0.3, 0.1, 0.03):
        row = ", ".join(f"SCR {s}: ζ {gfm_zeta(s, Xv)[0]:.2f} ({gfm_zeta(s, Xv)[1]:.1f} Hz)" for s in (3, 10, 20))
        print(f"  Xv = {Xv:.2f}: {row}")
    check("Xv 0.3, SCR 3 ζ", gfm_zeta(3, 0.3)[0], 0.36, 0.01)
    check("Xv 0.3, SCR 20 ζ", gfm_zeta(20, 0.3)[0], 0.27, 0.01)
    check("Xv 0.03, SCR 20 ζ", gfm_zeta(20, 0.03)[0], 0.13, 0.01)
    if args.plot:
        plt = plt_ready()
        scr = np.linspace(1, 20, 200)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for Xv, c in ((0.3, BLUE), (0.1, GREEN), (0.03, ORANGE)):
            ax.plot(scr, [gfm_zeta(s, Xv)[0] for s in scr], color=c, label=f"Xv = {Xv}")
        ax.set_xlabel("SCR"); ax.set_ylabel("ζ"); ax.legend()
        savefig(fig, "lec08_4_GFM감쇠.png")


def scr_step(mode, f_pll, scr_after, t_end=1.0):
    from gfm_gfl_emt import Scenario, simulate, steady_state
    DT, T_EV = 10e-6, 0.2
    p = Params(converter="average", scr=5.0, P_ref=0.8, f_pll=f_pll, gfl_frt_enter=0.5)   # FRT 순환 배제 (6강)
    sc = Scenario(t_end=t_end, scr=lambda t: 5.0 if t < T_EV else scr_after)
    return simulate(mode, p, sc, dt=DT, x0=steady_state(mode, p, dt=DT))


def practice_5(args):
    header("실습 5 · (EMT 평균값) 선로 트립 판정")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 2 분).")
        return
    from gfm_gfl_emt import oscillation_check
    exp = {("GFL", 20, 1.5): (True, None), ("GFL", 50, 1.5): (False, 90), ("GFL", 50, 2.0): (True, None),
           ("GFL", 10, 1.3): (False, 10), ("GFM", 20, 1.3): (True, None)}
    res = {}
    for (mode, f_pll, scr_after), (exp_ok, exp_f) in exp.items():          # 바꿔 보기: scr_after (해보기 A)
        r = scr_step(mode, f_pll, scr_after)
        t, Pw = np.asarray(r["t"]), np.asarray(r["P"])
        ok, info = oscillation_check(t, Pw, 0.4)
        res[(mode, f_pll, scr_after)] = (t, Pw)
        tag = f"{mode}" + (f" PLL {f_pll} Hz" if mode == "GFL" else "")
        print(f"  {tag:14s} SCR 5→{scr_after}: {'안정' if ok else '불안정'}  (5~300 Hz 최대 {info['osc_amp']:.3f} pu @ {info['osc_f']:.0f} Hz, 저주파 스윙 σ {info['swing_std']:.3f} pu)")
        check(f"  {tag} →{scr_after} 판정", float(ok), float(exp_ok), 0.1)
        if exp_f:
            check(f"  {tag} →{scr_after} 진동 주파수 [Hz]", info["osc_f"], exp_f, 5)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for key, c in ((("GFM", 20, 1.3), BLUE), (("GFL", 20, 1.5), ORANGE), (("GFL", 50, 1.5), GREEN)):
            t, Pw = res[key]; ax.plot((t - 0.2) * 1e3, Pw, color=c, lw=1.2, label=f"{key[0]} {key[1]} Hz → SCR {key[2]}")
        ax.set_xlim(-50, 600); ax.set_xlabel("SCR 전환 후 시간 [ms]"); ax.set_ylabel("P [pu]"); ax.legend()
        savefig(fig, "lec08_5_SCR급변.png")


def try_a(args):
    header("해보기 A · 20 Hz GFL 은 어느 SCR 에서 무너지나?")
    print("  practice_5 의 scr_after 를 1.5 → 1.4 → 1.3 으로 낮춰 본다 (--emt).")
    if args.answers:
        print("  답: 평균값 모델에서는 1.3 근처에서 무너지며, 10 Hz 부근 대진폭(동기화 상실형)이 먼저 나타난다.")
        print("      스위칭 모델 안정도 맵(summary.md)에서는 10/35 Hz 가 SCR 1.3 이하, 50 Hz 가 1.5 이하에서 불안정이다.")


def try_b(args):
    header("해보기 B · 강계통(SCR 10) GFM 의 P 계단 오버슈트: Xv 0.3 vs 0.05")
    print("  Params(converter='average', scr=10.0, Xv=...) 에 Scenario(p_ref=lambda t: 0.5 if t < 0.1 else 0.6) 을 주고 비교한다 (--emt).")
    print("  SCR 20 이상은 dt=5e-6 으로 줄인다 (10 µs 에서는 PCC 모선의 강성 회로 때문에 RK4 가 수치 발산: 제어 불안정이 아니다).")
    if args.answers:
        print("  답(작성 시 확인값): 오버슈트 약 0.05 pu (Xv 0.3) 대 0.08 pu (Xv 0.05). Xv 가 작을수록 Ks 가 커져 감쇠가 나빠진다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, try_a, try_b):
        fn(args)
