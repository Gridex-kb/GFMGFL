"""6강 실습 · GFL: PLL로 따라가기

실행 (저장소 루트에서):
    python practice/lec06_gfl_pll.py            # 해석 실습
    python practice/lec06_gfl_pll.py --plot     # 그림 저장 (practice/out/)
    python practice/lec06_gfl_pll.py --emt      # EMT(평균값): 위상 점프 PLL 10/20/50 Hz, FRT 모드 순환 (약 1 분)
    python practice/lec06_gfl_pll.py --answers

실습 목록
    1. SRF-PLL 이득: Kp = 2ζωn/ωb, Ki = ωn²/ωb (20 Hz → 0.471, 41.9)
    2. 강계통 PLL 비선형 응답: −20° 점프 직후 주파수 −4.8/−9.7/−24 Hz, 54 Hz 제한, 재정렬 시간
    3. P/Q → 전류 지령과 유효 우선 제한 (0.95 pu: |i*| 0.899, 0.7 pu: 1.22 → 제한)
    4. FRT 유효전류 여유 0.37 pu, 약계통 전압 상승 ΔV ≈ Xg·1.14
    5. (EMT) 위상 점프: PLL 대역폭별 ΔP·최저 주파수·정착 / SCR 5 → 1.5 FRT 모드 순환
    해보기 A. PLL 제한을 ±20 % 로 넓히면 20 Hz PLL 의 최저 측정 주파수는?
    해보기 B. FRT 무효전류를 0.5 × Imax 로 줄이면 SCR 1.5 순환이 멈출까?
"""
import math

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, MUTED

from gfm_gfl_emt import Params

P = Params()
WB = P.wb
F0 = P.f0


def pll_gains(f_n, zeta=0.707):
    wn = 2 * math.pi * f_n
    return 2 * zeta * wn / WB, wn * wn / WB


def pll_step(f_pll, dphi_deg=-20.0, zeta=0.707, dw_max=0.1, t_end=0.1, h=1e-5):
    """강계통(전압 1 pu)에 대한 SRF-PLL 비선형 응답. 위상 점프는 t = 0.
    바꿔 보기: dw_max=0.2 로 제한을 넓혀 본다 (해보기 A)."""
    kp, ki = pll_gains(f_pll, zeta)
    n = int(t_end / h); t = np.arange(n) * h
    e_out, f_out = np.zeros(n), np.zeros(n)
    th_err = math.radians(dphi_deg); x = 0.0
    for k in range(n):
        vq = math.sin(th_err)
        dw = min(dw_max, max(-dw_max, kp * vq + x))
        if not ((x >= dw_max and vq > 0) or (x <= -dw_max and vq < 0)):
            x += h * ki * vq
        th_err -= h * WB * dw
        e_out[k], f_out[k] = math.degrees(th_err), F0 * (1 + dw)
    return t, e_out, f_out


def current_ref(P_ref, Q_ref, v, I_max=P.I_max):
    """i_d* = P*/v, i_q* = −Q*/v, 정상 운전 유효 우선 제한."""
    vd = max(v, 0.3)
    id_ref, iq_ref = P_ref / vd, -Q_ref / vd
    limited = math.hypot(id_ref, iq_ref) > I_max
    if limited:
        id_ref = max(-I_max, min(I_max, id_ref))
        room = math.sqrt(max(I_max ** 2 - id_ref ** 2, 0.0))
        iq_ref = max(-room, min(room, iq_ref))
    return id_ref, iq_ref, limited


def practice_1(args):
    header("실습 1 · SRF-PLL 이득")
    for fn in (10, 20, 50):
        kp, ki = pll_gains(fn)
        print(f"  f_n = {fn:2d} Hz: Kp = {kp:.3f}, Ki = {ki:6.1f} pu/s")
    kp, ki = pll_gains(P.f_pll, P.pll_zeta)
    check("모델 기본 Kp (20 Hz)", kp, 0.471, 0.002)
    check("모델 기본 Ki (20 Hz)", ki, 41.9, 0.1)


def practice_2(args):
    header("실습 2 · 강계통 PLL 응답: −20° 위상 점프")
    out = {}
    for fn, exp_df0 in ((10, -4.8), (20, -9.7), (50, -24.2)):
        kp, _ = pll_gains(fn)
        df0 = F0 * kp * math.sin(math.radians(-20))
        t, e, f = pll_step(fn)
        settle = t[np.abs(e) > 1.0].max() * 1e3
        out[fn] = (t, e, f)
        print(f"  PLL {fn:2d} Hz: 점프 직후 Δf0 = {df0:+.1f} Hz → 측정 최저 {f.min():.2f} Hz, |오차| < 1° 정착 {settle:.0f} ms")
        check(f"  Δf0 ({fn} Hz) [Hz]", df0, exp_df0, 0.15)
    check("20 Hz PLL 최저 측정 주파수 (제한)", out[20][2].min(), 54.0, 0.01)
    check("10 Hz PLL 최저 측정 주파수 (제한에 안 닿음)", out[10][2].min(), 55.16, 0.05)
    if args.plot:
        plt = plt_ready()
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        for (fn, (t, e, f)), c in zip(out.items(), (GREEN, ORANGE, BLUE)):
            a1.plot(t * 1e3, e, color=c, label=f"PLL {fn} Hz"); a2.plot(t * 1e3, f, color=c)
        a2.axhline(54, color="#c8323c", ls=":"); a1.set_ylabel("위상 오차 [°]"); a2.set_ylabel("측정 주파수 [Hz]")
        a2.set_xlabel("위상 점프 후 시간 [ms]"); a1.legend()
        savefig(fig, "lec06_2_PLL대역폭.png")


def practice_3(args):
    header("실습 3 · P/Q → 전류 지령과 유효 우선 제한")
    for v in (0.95, 0.7):
        id_, iq_, lim = current_ref(0.8, 0.3, v)
        raw = math.hypot(0.8 / v, 0.3 / v)
        print(f"  |v| = {v}: 지령 ({0.8 / v:.3f}, {-0.3 / v:.3f}) 크기 {raw:.3f} → "
              f"{'제한 ' if lim else '그대로 '}({id_:.3f}, {iq_:.3f}), 크기 {math.hypot(id_, iq_):.3f}")
    check("0.95 pu 전류 크기", math.hypot(0.8 / 0.95, 0.3 / 0.95), 0.899, 0.002)
    check("0.7 pu 제한 전 크기", math.hypot(0.8 / 0.7, 0.3 / 0.7), 1.22, 0.01)


def practice_4(args):
    header("실습 4 · FRT: 유효전류 여유와 약계통 전압 상승")
    iq = P.gfl_frt_iq * P.I_max
    room = math.sqrt(P.I_max ** 2 - iq ** 2)
    print(f"  FRT 무효전류 {iq:.2f} pu, 유효전류 여유 √(1.2² − {iq:.2f}²) = {room:.3f} pu")
    for scr in (5, 3, 1.5):
        print(f"  SCR {scr:>3}: Xg = {1 / scr:.2f} → ΔV ≈ Xg × {iq:.2f} = {iq / scr:.2f} pu")
    check("유효전류 여유 [pu]", room, 0.37, 0.01)
    check("SCR 1.5 전압 상승 [pu]", iq / 1.5, 0.76, 0.01)


def practice_5(args):
    header("실습 5 · (EMT 평균값) 위상 점프와 FRT 모드 순환")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 1 분).")
        return
    from gfm_gfl_emt import Scenario, simulate, steady_state
    DT = 10e-6
    jump = Scenario(t_end=0.3, grid_phase=lambda t: math.radians(-20) if t >= 0.1 else 0.0)
    for f_pll, exp_settle in ((10, 84), (20, 47), (50, 24)):
        p = Params(converter="average", f_pll=f_pll)      # SCR 3, P* = 0.5 pu
        x0 = steady_state("GFL", p, dt=DT)
        r = simulate("GFL", p, jump, dt=DT, x0=x0)
        t, Pw, f = (np.asarray(r[k]) for k in ("t", "P", "freq"))
        m10 = (t >= 0.1) & (t <= 0.11)
        dP = Pw[m10].max() - Pw[t < 0.1][-1]
        settle = (t[(t > 0.1) & (np.abs(f - 60) > 0.1)].max() - 0.1) * 1e3
        print(f"  PLL {f_pll:2d} Hz: 10 ms 내 최대 ΔP {dP:+.3f} pu, 측정 주파수 최저 {f.min():.2f} Hz, 정착 {settle:.0f} ms")
        if f_pll == 20:
            check("  20 Hz: 10 ms 내 ΔP [pu]", dP, 0.007, 0.003)
            check("  20 Hz: 최저 측정 주파수 [Hz]", f.min(), 54.0, 0.01)
        check(f"  {f_pll} Hz 정착 [ms]", settle, exp_settle, 5)
    trip = Scenario(t_end=0.8, scr=lambda t: 5.0 if t < 0.2 else 1.5)
    res = {}
    for enter in (0.85, 0.5):          # 바꿔 보기: gfl_frt_iq=0.5 (해보기 B)
        p = Params(converter="average", scr=5.0, P_ref=0.8, gfl_frt_enter=enter)
        r = simulate("GFL", p, trip, dt=DT, x0=steady_state("GFL", p, dt=DT))
        t, V, f = (np.asarray(r[k]) for k in ("t", "V", "freq"))
        late = t > 0.5
        res[enter] = (t, V, f)
        print(f"  FRT 진입 {enter} pu: 0.3 s 이후 |v| {V[late].min():.2f}~{V[late].max():.2f} pu, 주파수 {f[late].min():.1f}~{f[late].max():.1f} Hz")
    t, V, f = res[0.85]; late = t > 0.5
    check("진입 0.85: |v| 최대 (과전압) [pu]", V[late].max(), 1.28, 0.03)
    check("진입 0.85: 주파수 최저 [Hz]", f[late].min(), 54.0, 0.1)
    t, V, f = res[0.5]; late = t > 0.5
    check("진입 0.5: |v| 유지 [pu]", V[late].min(), 1.0, 0.01)
    if args.plot:
        plt = plt_ready()
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        for (enter, (t, V, f)), c in zip(res.items(), (ORANGE, GREEN)):
            a1.plot((t - 0.2) * 1e3, V, color=c, label=f"FRT 진입 {enter} pu"); a2.plot((t - 0.2) * 1e3, f, color=c)
        a1.axhline(0.85, color=MUTED, ls=":"); a1.axhline(0.92, color=MUTED, ls=":"); a1.set_ylabel("|v| [pu]"); a1.legend()
        a2.set_ylabel("PLL 주파수 [Hz]"); a2.set_xlabel("SCR 5 → 1.5 전환 후 시간 [ms]")
        savefig(fig, "lec06_5_FRT순환.png")


def try_a(args):
    header("해보기 A · PLL 제한 ±20 % 에서 20 Hz PLL 의 최저 측정 주파수")
    t, e, f = pll_step(20, dw_max=0.2)         # 바꿔 보기: dw_max
    print(f"  최저 측정 주파수 {f.min():.1f} Hz (제한 ±10 % 이면 54.0 Hz)")
    if args.answers:
        print("  답: 약 50 Hz (EMT 모델에서는 약 49 Hz). 54 Hz 는 물리 현상이 아니라 제한값이다. 비례항 첫 반응 −9.7 Hz 에 적분항이 더해져 더 내려간다.")


def try_b(args):
    header("해보기 B · FRT 무효전류 0.5 × Imax 로 줄이면?")
    iq = 0.5 * P.I_max
    v_sag = 0.74                                # 전환 직후 순간 저전압 (FRT 없이 넘길 때의 최저, 실습 5)
    print(f"  SCR 1.5: ΔV ≈ {1 / 1.5:.2f} × {iq:.2f} = {iq / 1.5:.2f} pu 상승 → {v_sag} + {iq / 1.5:.2f} = {v_sag + iq / 1.5:.2f} pu, "
          f"해제 전압 0.92 를 {'넘는다' if v_sag + iq / 1.5 > 0.92 else '못 넘는다'}")
    if args.answers:
        print("  답: 멈추지 않는다. 0.6 pu × Xg 0.67 ≈ 0.4 pu 상승이면 여전히 0.92 pu 를 넘어 해제·재진입이 반복된다.")
        print("      진입 전압(gfl_frt_enter), 해제 전압(gfl_frt_exit), 주입량 중 무엇을 바꿔야 끊기는지 --emt 로 찾아본다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, try_a, try_b):
        fn(args)
