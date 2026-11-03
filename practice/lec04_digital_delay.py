"""4강 실습 · 디지털 제어와 지연

실행 (저장소 루트에서):
    python practice/lec04_digital_delay.py            # 해석 실습
    python practice/lec04_digital_delay.py --plot     # 그림 저장 (practice/out/)
    python practice/lec04_digital_delay.py --emt      # EMT: 연속 θ 버그 재현 61.35 → 60.00 Hz (약 10 s)
    python practice/lec04_digital_delay.py --answers

실습 목록
    1. 1.5 Ts 순수 지연 vs 1차 지연 근사의 위상
    2. 영차 홀드가 정확히 0.5 Ts 지연임을 수치로 확인
    3. 800 Hz 교차주파수에서 위상 예산
    4. 연속 θ로 변환하면 vq 가 톱니가 된다: 평균 −ωTs/2, PLL 주파수 오프셋 예측
    5. (EMT) 각도 처리 버그 재현: 샘플 시점 θ vs 연속 θ
    해보기 A. 1 kHz 에서 위상 지연은?
    해보기 B. PLL 대역폭 20 Hz 에서 오프셋은?
"""
import math

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE

F_SW = 5000.0
TS = 1 / (2 * F_SW)          # 100 µs (2회 갱신)
TD = 1.5 * TS                # 150 µs
WB = 2 * math.pi * 60


def practice_1(args):
    header("실습 1 · 순수 지연 vs 1차 근사")
    print("     f      순수 지연   1차 근사   1차 근사 크기")
    for f in (100, 400, 800, 1000, 2000):
        w = 2 * math.pi * f
        print(f"  {f:5d} Hz   {math.degrees(w*TD):7.1f}°   {math.degrees(math.atan(w*TD)):7.1f}°   "
              f"{-10*math.log10(1 + (w*TD)**2):6.2f} dB")
    check("800 Hz 순수 지연 [°]", 360 * 800 * TD, 43.2, 0.05)
    if args.plot:
        plt = plt_ready()
        f = np.logspace(1, math.log10(5000), 500)
        w = 2 * np.pi * f
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.semilogx(f, -np.degrees(w * TD), color=ORANGE, lw=2.5, label="순수 지연 e^{-1.5sTs}")
        ax.semilogx(f, -np.degrees(np.arctan(w * TD)), color=BLUE, lw=2.5, ls="--", label="1차 근사 1/(1+sTd)")
        ax.axvline(800, color="#888", ls=":"); ax.set_xlabel("주파수 [Hz]"); ax.set_ylabel("위상 [°]"); ax.legend()
        savefig(fig, "lec04_1_지연위상.png")


def practice_2(args):
    header("실습 2 · 영차 홀드 = 0.5 Ts 지연")
    for f in (100, 800, 2000):
        w = 2 * math.pi * f
        g = (1 - np.exp(-1j * w * TS)) / (1j * w * TS)
        print(f"  {f:5d} Hz: ZOH 위상 = {math.degrees(np.angle(g)):7.2f}°, −ωTs/2 = {-math.degrees(w*TS/2):7.2f}°, 크기 = {abs(g):.4f}")


def practice_3(args):
    header("실습 3 · 교차주파수 800 Hz 의 위상 예산")
    delay = 360 * 800 * TD
    plant, pi_zero = 90.0, 10.0
    pm = 180 - plant - delay - pi_zero
    print(f"  플랜트 적분 {plant:.0f}° + 지연 {delay:.1f}° + PI 영점 ≈{pi_zero:.0f}° → 위상여유 ≈ {pm:.1f}°")
    print(f"  f_c·T_d = {800 * TD:.3f}  (경험칙: 0.1 근처)")


def practice_4(args):
    header("실습 4 · 연속 θ 변환의 톱니와 PLL 오프셋")
    t = np.linspace(0, 5 * TS, 5001, endpoint=False)
    tk = np.floor(t / TS) * TS
    vq = -np.sin(WB * (t - tk))
    check("vq 평균 = −ωTs/2", vq.mean(), -WB * TS / 2, 1e-4)
    kp = 2 * 0.707 * 2 * math.pi * 50 / WB
    print(f"  PLL 50 Hz: kp = {kp:.3f} → 예상 오프셋 = {kp * WB * TS / 2 * 60:.2f} Hz")
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(t * 1e6, vq, color=ORANGE, label="연속 θ"); ax.axhline(0, color=BLUE, label="샘플 시점 θ")
        ax.axhline(vq.mean(), color=ORANGE, ls="--"); ax.set_xlabel("시간 [µs]"); ax.set_ylabel("vq [pu]"); ax.legend()
        savefig(fig, "lec04_4_톱니.png")


def practice_5(args):
    header("실습 5 · (EMT) 각도 처리 버그 재현")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 10 s).")
        return
    import gfm_gfl_emt as emt
    from gfm_gfl_emt import Params, Scenario, simulate, steady_state, replace

    class ContTheta(emt.Inverter):
        """잘못된 각도 처리: 홀드된 측정을 연속 회전 θ 로 dq 변환."""
        def deriv(self, t, x):
            self.th_hold = x[emt.TH_C]
            return super().deriv(t, x)

    p = Params(f_pll=50.0, scr=5.0)
    x0 = steady_state("GFL", replace(p, converter="average"), t_init=1.5, dt=1e-5)
    orig = emt.Inverter
    out = {}
    try:
        for name, cls in (("샘플 시점 θ", orig), ("연속 θ", ContTheta)):
            emt.Inverter = cls
            r = simulate("GFL", p, Scenario(t_end=0.15), x0=x0)
            out[name] = (np.array(r["freq"])[500:].mean(), np.array(r["delta_deg"])[500:].mean())
            print(f"  {name}: PLL 주파수 {out[name][0]:.2f} Hz, 위상차 {out[name][1]:.2f}°")
    finally:
        emt.Inverter = orig
    check("주파수 오프셋 [Hz]", out["연속 θ"][0] - out["샘플 시점 θ"][0], 1.35, 0.1)


def try_a(args):
    header("해보기 A · 1 kHz 에서 위상 지연")
    print(f"  {360 * 1000 * TD:.1f}°")
    if args.answers:
        print("  답: 54°. 1 kHz 로 전류 제어 대역을 올리면 지연만으로 위상여유가 바닥난다.")


def try_b(args):
    header("해보기 B · PLL 대역폭 20 Hz 에서 오프셋")
    kp = 2 * 0.707 * 2 * math.pi * 20 / WB
    print(f"  kp = {kp:.3f}, 오프셋 = {kp * WB * TS / 2 * 60:.2f} Hz")
    if args.answers:
        print("  답: 약 0.53 Hz. 오프셋은 kp 에 비례하고, SCR 과는 거의 무관한 디지털 처리 오차다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, practice_5, try_a, try_b):
        fn(args)
