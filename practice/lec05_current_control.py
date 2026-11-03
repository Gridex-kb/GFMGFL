"""5강 실습 · 전류 제어

실행 (저장소 루트에서):
    python practice/lec05_current_control.py            # 해석 실습
    python practice/lec05_current_control.py --plot     # 그림 저장 (practice/out/)
    python practice/lec05_current_control.py --emt      # EMT: GFM, SCR 2 피드포워드 실험 (약 40 s)
    python practice/lec05_current_control.py --answers

실습 목록
    1. PI 이득: Kp = ωcc·Lf/ωb, Ki = Kp·ωcc/5
    2. 개루프 교차주파수와 위상여유 (지연 있음 815 Hz·34.9°, 지연 없음 약 79°)
    3. 독립 전류루프 0.1 pu 계단: 지연·디커플링 (오버슈트 50 % vs 15 %, iq 흔들림 절반)
    4. 1 pu 계단에서 anti-windup 유무 (오버슈트 3 % vs 68 %)
    5. (EMT) PCC 전압 피드포워드 없음 / 순시 / 100 Hz LPF → σ(P) 0.004 / 0.117 / 0.004 pu
    해보기 A. f_cc = 400 Hz 로 낮추면 위상여유는?
    해보기 B. Lf = 0.15 pu 설비에서 같은 800 Hz 를 원하면 Kp, Ki 는?
"""
import math

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, MUTED

from gfm_gfl_emt import Params

P = Params()
WB = P.wb
TS = 1 / (2 * P.f_sw)            # 100 µs
TD = 1.5 * TS                    # 150 µs


def gains(f_cc=P.f_cc, Lf=P.Lf):
    wcc = 2 * math.pi * f_cc
    Kp = wcc * Lf / WB
    return Kp, Kp * wcc / 5


def open_loop(f, Kp, Ki, Lf=P.Lf, Td=TD):
    """L(jω) = (Kp + Ki/jω)·e^{-jωTd}·ωb/(jωLf + Rf·ωb)"""
    w = 2 * np.pi * np.asarray(f, float)
    return (Kp + Ki / (1j * w)) * np.exp(-1j * w * Td) * WB / (1j * w * Lf + P.Rf * WB)


def crossover(Kp, Ki, Lf=P.Lf, Td=TD):
    f = np.linspace(100, 3000, 29001)
    L = open_loop(f, Kp, Ki, Lf, Td)
    k = int(np.argmin(abs(abs(L) - 1)))
    ph = np.degrees(np.unwrap(np.angle(L)))
    return f[k], 180 + ph[k]


def current_loop(i_ref_fn, Kp, Ki, t_end=0.01, decouple=True, delay=True, antiwindup=True, dt=2e-6):
    """dq 전류루프 독립 모의 (Cf 무시, 단자 전압 1 pu 고정). 10 kHz 샘플, 1샘플 계산 지연 + 영차 홀드.
    바꿔 보기: antiwindup=False 로 두면 포화 중에도 적분한다 (실습 4)."""
    n = int(round(t_end / dt)); per = int(round(TS / dt))
    i = 0j; x = 1.0 + 0j; v_now = v_next = 1.0 + 0j
    T, I = np.empty(n), np.empty(n, complex)
    for k in range(n):
        t = k * dt
        if k % per == 0:
            e = i_ref_fn(t) - i
            v = Kp * e + x + (1j * P.Lf * i if decouple else 0)
            sat = abs(v) > P.V_conv_max
            if sat:
                v *= P.V_conv_max / abs(v)
            if not sat or not antiwindup:
                x += Ki * TS * e
            if delay:
                v_now, v_next = v_next, v
            else:
                v_now = v
        i += (v_now - P.Rf * i - 1j * P.Lf * i - 1.0) * (WB / P.Lf) * dt
        T[k], I[k] = t, i
    return (T - 0.001) * 1e3, I


def practice_1(args):
    header("실습 1 · PI 이득")
    Kp, Ki = gains()
    print(f"  ωcc = 2π·{P.f_cc:.0f} = {2 * math.pi * P.f_cc:.0f} rad/s, Lf = {P.Lf} pu, ωb = {WB:.0f} rad/s")
    check("Kp [pu/pu]", Kp, 2.667, 0.005)
    check("Ki [pu/(pu·s)]", Ki, 2681, 2)
    print(f"  PI 영점 Ki/Kp = {Ki / Kp / (2 * math.pi):.0f} Hz, 교차주파수에서 위상 −arctan(1/5) = {math.degrees(math.atan(0.2)):.1f}°")


def practice_2(args):
    header("실습 2 · 개루프 교차주파수와 위상여유")
    Kp, Ki = gains()
    fc, pm = crossover(Kp, Ki)
    fc0, pm0 = crossover(Kp, Ki, Td=0)      # 바꿔 보기: Td = 0 이면 지연이 먹는 위상이 사라진다
    print(f"  지연 1.5 Ts: 교차 {fc:.0f} Hz, 위상여유 {pm:.1f}°   (지연 위상 {360 * fc * TD:.1f}°)")
    print(f"  지연 없음 : 교차 {fc0:.0f} Hz, 위상여유 {pm0:.1f}°")
    check("교차주파수 [Hz]", fc, 815, 3)
    check("위상여유 [°]", pm, 34.9, 0.3)
    check("지연 없는 위상여유 [°]", pm0, 79, 1)
    if args.plot:
        plt = plt_ready()
        f = np.logspace(2, math.log10(5000), 600)
        L, L0 = open_loop(f, Kp, Ki), open_loop(f, Kp, Ki, Td=0)
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        a1.semilogx(f, 20 * np.log10(abs(L)), color=ORANGE); a1.axhline(0, color=MUTED, lw=1); a1.set_ylabel("|L| [dB]")
        a2.semilogx(f, np.degrees(np.unwrap(np.angle(L))), color=ORANGE, label="지연 1.5 Ts")
        a2.semilogx(f, np.degrees(np.unwrap(np.angle(L0))), color=BLUE, ls="--", label="지연 없음")
        a2.axhline(-180, color="#c8323c", ls=":"); a2.axvline(fc, color=MUTED, ls=":")
        a2.set_ylim(-300, -80); a2.set_xlabel("주파수 [Hz]"); a2.set_ylabel("∠L [°]"); a2.legend()
        savefig(fig, "lec05_2_보드.png")


def practice_3(args):
    header("실습 3 · 0.1 pu 계단: 지연과 디커플링")
    Kp, Ki = gains()
    step = lambda t: 0.1 + 0j if t >= 0.001 else 0j
    t, I1 = current_loop(step, Kp, Ki)
    _, I2 = current_loop(step, Kp, Ki, decouple=False)
    _, I3 = current_loop(step, Kp, Ki, delay=False)
    os1, os3 = (I1.real.max() - 0.1) / 0.1 * 100, (I3.real.max() - 0.1) / 0.1 * 100
    print(f"  오버슈트: 지연 1.5 Ts {os1:.0f} %, 지연 없음 {os3:.0f} %")
    print(f"  iq 최대 흔들림: 디커플링 있음 {I1.imag.min():.4f} pu, 없음 {I2.imag.min():.4f} pu")
    check("오버슈트 (지연) [%]", os1, 50, 2)
    check("오버슈트 (지연 없음) [%]", os3, 15, 2)
    check("iq 흔들림 비 (있음/없음)", I1.imag.min() / I2.imag.min(), 0.5, 0.1)
    if args.plot:
        plt = plt_ready()
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        a1.plot(t, I3.real, color=GREEN, label="지연 없음"); a1.plot(t, I2.real, color=ORANGE, label="디커플링 없음")
        a1.plot(t, I1.real, color=BLUE, lw=2.5, label="지연 + 디커플링"); a1.set_ylabel("id [pu]"); a1.legend()
        a2.plot(t, I3.imag, color=GREEN); a2.plot(t, I2.imag, color=ORANGE); a2.plot(t, I1.imag, color=BLUE, lw=2.5)
        a2.set_xlim(-0.5, 6); a2.set_xlabel("계단 이후 시간 [ms]"); a2.set_ylabel("iq [pu]")
        savefig(fig, "lec05_3_계단응답.png")


def practice_4(args):
    header("실습 4 · 1 pu 계단: anti-windup")
    Kp, Ki = gains()
    big = lambda t: 1.0 + 0j if t >= 0.001 else 0j
    t, A1 = current_loop(big, Kp, Ki, t_end=0.012)
    _, A2 = current_loop(big, Kp, Ki, t_end=0.012, antiwindup=False)   # 바꿔 보기: 포화 중에도 적분
    os1, os2 = (A1.real.max() - 1) * 100, (A2.real.max() - 1) * 100
    print(f"  오버슈트: 조건부 적분 {os1:.1f} %, anti-windup 없음 {os2:.1f} % (최대 {A2.real.max():.2f} pu > 한계 {P.I_max})")
    check("오버슈트 (조건부 적분) [%]", os1, 2.8, 0.5)
    check("오버슈트 (anti-windup 없음) [%]", os2, 68, 2)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t, A2.real, color=ORANGE, label="anti-windup 없음"); ax.plot(t, A1.real, color=BLUE, lw=2.5, label="조건부 적분")
        ax.axhline(P.I_max, color="#c8323c", ls=":", label="전류 한계 1.2 pu"); ax.set_xlim(-0.5, 11)
        ax.set_xlabel("계단 이후 시간 [ms]"); ax.set_ylabel("id [pu]"); ax.legend()
        savefig(fig, "lec05_4_와인드업.png")


def practice_5(args):
    header("실습 5 · (EMT) PCC 전압 피드포워드와 약계통 (GFM, SCR 2)")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 40 s).")
        return
    from gfm_gfl_emt import Scenario, simulate, steady_state, replace
    out = {}
    for name, ff, fv, exp in (("피드포워드 없음", 0.0, 100.0, 0.004), ("순시 피드포워드", 1.0, 0.0, 0.117), ("100 Hz 저역통과", 1.0, 100.0, 0.004)):
        pa = Params(converter="average", scr=2.0, ff_gain=ff, f_vff=fv)
        x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
        r = simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.2), x0=x0)
        t, Pw = np.array(r["t"]), np.array(r["P"])
        out[name] = (t, Pw)
        check(f"σ(P) {name} [pu]", Pw[t >= 0.1].std(), exp, 0.01)
    t, Pw = out["순시 피드포워드"]
    x = Pw[t >= 0.1] - Pw[t >= 0.1].mean()
    F = np.abs(np.fft.rfft(x * np.hanning(len(x)))); fr = np.fft.rfftfreq(len(x), 1e-4)
    check("순시 피드포워드 진동 주파수 [Hz]", fr[np.argmax(F)], 560, 20)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 4))
        for (name, (t, Pw)), c in zip(out.items(), (BLUE, ORANGE, GREEN)):
            ax.plot(t * 1e3, Pw, color=c, lw=1.2, label=name)
        ax.set_xlabel("시간 [ms]"); ax.set_ylabel("P [pu]"); ax.set_ylim(0, 1.2); ax.legend()
        savefig(fig, "lec05_5_피드포워드.png")


def try_a(args):
    header("해보기 A · f_cc = 400 Hz 의 위상여유")
    Kp, Ki = gains(f_cc=400.0)            # 바꿔 보기: 다른 대역폭
    fc, pm = crossover(Kp, Ki)
    print(f"  Kp = {Kp:.3f}, Ki = {Ki:.0f} → 교차 {fc:.0f} Hz, 위상여유 {pm:.1f}°")
    if args.answers:
        print("  답: 약 57°. 지연 위상이 22°로 줄어 90 − 11 − 22 ≈ 57°. 대역폭을 반으로 낮추면 위상여유는 22° 커진다.")


def try_b(args):
    header("해보기 B · Lf = 0.15 pu 에서 같은 800 Hz")
    Kp, Ki = gains(Lf=0.15)               # 바꿔 보기: 다른 인덕턴스
    fc, pm = crossover(Kp, Ki, Lf=0.15)
    print(f"  Kp = {Kp:.3f}, Ki = {Ki:.0f} → 교차 {fc:.0f} Hz, 위상여유 {pm:.1f}°")
    if args.answers:
        print("  답: Kp ≈ 2.0, Ki ≈ 2011. Kp 는 Lf 에 비례하고, 교차주파수와 위상여유는 그대로다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, try_a, try_b):
        fn(args)
