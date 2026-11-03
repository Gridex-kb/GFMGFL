"""2강 실습 · 2레벨 전압형 컨버터(VSC)

실행 (저장소 루트에서):
    python practice/lec02_two_level_vsc.py            # 계산 실습
    python practice/lec02_two_level_vsc.py --plot     # 그림 저장 (practice/out/)
    python practice/lec02_two_level_vsc.py --emt      # 시뮬레이션 모델의 PWM 함수로도 확인
    python practice/lec02_two_level_vsc.py --answers  # '해보기' 답

실습 목록
    1. 스위칭 상태 8개 표: 극전압, 영상분, 상전압, 공간벡터 (영상분은 αβ에 안 보인다)
    2. 반송파 PWM: 듀티 (0.5, −0.2, −0.3)일 때 한 주기의 상태 순서
    3. 6스텝 파형과 기본파 진폭 2V_dc/π = 1.436 pu
    4. 평균 벡터: 1.0∠20°를 만드는 t1, t2, t0 와 선형 한계 1.303 pu
    해보기 A. 상태 (011)의 영상분과 공간벡터
    해보기 B. V_dc 를 10 % 낮추면 최대 상전압은?
"""
import itertools

import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, GREEN, NAVY, MUTED

V_DC = 700.0 / (380.0 * np.sqrt(2.0 / 3.0))     # 2.256 pu (700 V / 상전압 피크 310.3 V)
A = np.exp(2j * np.pi / 3)


def state_voltages(s, vdc=V_DC):
    """상태 (Sa, Sb, Sc) → 극전압, 영상분, 상전압, 공간벡터."""
    v_pole = (2 * np.array(s, dtype=float) - 1) * vdc / 2
    v_n0 = v_pole.mean()
    v_ph = v_pole - v_n0
    vec = (2 / 3) * (v_pole[0] + A * v_pole[1] + A**2 * v_pole[2])
    return v_pole, v_n0, v_ph, vec


def practice_1(args):
    header("실습 1 · 스위칭 상태 8개")
    print(f"  V_dc = {V_DC:.3f} pu")
    print("  상태   극전압 (a, b, c)          영상분   상전압 a   |v|     각도")
    for s in itertools.product((1, 0), repeat=3):
        v_pole, v_n0, v_ph, vec = state_voltages(s)
        vec2 = (2 / 3) * (v_ph[0] + A * v_ph[1] + A**2 * v_ph[2])
        assert abs(vec - vec2) < 1e-12, "영상분은 공간벡터에 나타나지 않아야 한다"
        ang = np.degrees(np.angle(vec)) if abs(vec) > 1e-9 else float("nan")
        print(f"  {''.join(map(str, s))}   {np.array2string(v_pole, precision=3, sign='+')}  "
              f"{v_n0:+.3f}   {v_ph[0]:+.3f}    {abs(vec):.3f}  {ang:6.1f}°")
    check("유효 벡터 크기 (2/3)V_dc", abs(state_voltages((1, 0, 0))[3]), 1.504, 1e-3)


def pwm_states(duty, t_us):
    """삼각 반송파(0 µs 골, 100 µs 꼭짓점, 주기 200 µs)와 비교한 상태."""
    ph = (t_us / 200.0) % 1.0
    car = np.where(ph < 0.5, 4 * ph - 1, 3 - 4 * ph)
    return np.array([[1 if d > c else 0 for d in duty] for c in car]), car


def practice_2(args):
    header("실습 2 · 반송파 PWM: 한 주기의 상태 순서")
    duty = (0.5, -0.2, -0.3)
    t = np.arange(0, 200.0, 0.5)
    S, car = pwm_states(duty, t)
    seq, start = [], 0
    for k in range(1, len(t) + 1):
        if k == len(t) or not np.array_equal(S[k], S[start]):
            seq.append(("".join(map(str, S[start])), t[start], t[k - 1] + 0.5))
            start = k
    for name, a, b in seq:
        print(f"  {a:6.1f} ~ {b:6.1f} µs : {name}")
    # 평균 벡터 = 듀티가 만드는 평균 극전압의 공간벡터
    avg = np.mean([state_voltages(s)[3] for s in S])
    target = (2 / 3) * (V_DC / 2) * (duty[0] + A * duty[1] + A**2 * duty[2])
    check("한 주기 평균 벡터 크기", abs(avg), abs(target), 5e-3)
    if getattr(args, "emt", False):
        from gfm_gfl_emt import Params, Scenario, Inverter
        inv = Inverter("GFM", Params(), Scenario())
        inv.duty = duty
        print("  시뮬레이션 모델 Inverter.pwm():")
        for tt in (0.0, 50e-6, 100e-6):
            inv.pwm(tt)
            print(f"    t = {tt*1e6:5.1f} µs → v_pole = {inv.vpole.real:+.3f} {inv.vpole.imag:+.3f}j, |v| = {abs(inv.vpole):.3f}")
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
        ax[0].plot(t, car, color=NAVY, label="반송파")
        for d, c, n in zip(duty, (BLUE, ORANGE, GREEN), "abc"):
            ax[0].axhline(d, color=c, ls="--", label=f"d{n} = {d}")
        ax[0].legend(ncol=4, fontsize=9, loc="upper right")
        for k, (c, n) in enumerate(zip((BLUE, ORANGE, GREEN), "abc")):
            ax[1].step(t, S[:, k] * 0.8 + (2 - k), where="post", color=c)
        ax[1].set_yticks([2.4, 1.4, 0.4]); ax[1].set_yticklabels(["Sa", "Sb", "Sc"]); ax[1].set_xlabel("시간 [µs]")
        savefig(fig, "lec02_2_PWM_상태.png")


def practice_3(args):
    header("실습 3 · 6스텝 파형과 기본파")
    th = np.linspace(0, 360, 3600, endpoint=False)
    order = ["100", "110", "010", "011", "001", "101"]
    st = [order[int(((x + 30) % 360) // 60)] for x in th]
    va_pole = np.array([(1 if s[0] == "1" else -1) * V_DC / 2 for s in st])
    vn0 = np.array([state_voltages(tuple(int(c) for c in s))[1] for s in st])
    van = va_pole - vn0
    print(f"  상전압 값의 종류: {sorted(float(v) for v in set(np.round(van, 3)))}")
    print("  (6스텝은 영벡터를 쓰지 않아 0 이 없다. 영벡터를 쓰는 PWM 에서는 0 까지 다섯 값)")
    fund = 2 * np.mean(van * np.cos(np.deg2rad(th)))            # 푸리에 cos 계수
    check("기본파 진폭 2V_dc/π", fund, 2 * V_DC / np.pi, 2e-3)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
        ax[0].plot(th, va_pole, color=BLUE); ax[0].set_ylabel("극전압 va0")
        ax[1].plot(th, vn0, color=GREEN); ax[1].set_ylabel("영상분 vn0")
        ax[2].plot(th, van, color=BLUE); ax[2].plot(th, fund * np.cos(np.deg2rad(th)), color=MUTED, ls="--")
        ax[2].set_ylabel("상전압 van"); ax[2].set_xlabel("전기각 [°]")
        savefig(fig, "lec02_3_6스텝.png")


def practice_4(args):
    header("실습 4 · 평균 벡터와 선형 한계")
    V1, V2 = state_voltages((1, 0, 0))[3], state_voltages((1, 1, 0))[3]
    target = 1.0 * np.exp(1j * np.deg2rad(20))
    d2 = target.imag / V2.imag
    d1 = (target.real - d2 * V2.real) / V1.real
    print(f"  1.0∠20° = {d1:.3f}·V1 + {d2:.3f}·V2 + {1 - d1 - d2:.3f}·영벡터")
    check("t1/Ts", d1, 0.4935, 1e-3)
    check("최대 상전압 V_dc/√3 (내접원)", V_DC / np.sqrt(3), 1.303, 1e-3)


def try_a(args):
    header("해보기 A · 상태 (011)의 영상분과 공간벡터")
    v_pole, v_n0, v_ph, vec = state_voltages((0, 1, 1))
    print(f"  영상분 = {v_n0:+.3f}, |v| = {abs(vec):.3f}, 각도 = {np.degrees(np.angle(vec)):.0f}°")
    if args.answers:
        print("  답: 극전압 (−, +, +)1.128, 영상분 +0.376, V4 = 1.504∠180°")


def try_b(args):
    header("해보기 B · V_dc 를 10 % 낮추면 최대 상전압은?")
    v = 0.9 * V_DC / np.sqrt(3)
    print(f"  V_dc = {0.9 * V_DC:.3f} pu → 최대 상전압 = {v:.3f} pu")
    if args.answers:
        print("  답: 1.303 × 0.9 ≈ 1.173 pu. 계통 1 pu 에 대한 여유가 0.30 에서 0.17 로 준다.")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, try_a, try_b):
        fn(args)
