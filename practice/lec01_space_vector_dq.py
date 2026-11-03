"""1강 실습 · 3상 계통의 표현과 공간벡터·dq 변환

실행 (저장소 루트에서):
    python practice/lec01_space_vector_dq.py            # 계산 실습만
    python practice/lec01_space_vector_dq.py --plot     # 그림도 practice/out/ 에 저장
    python practice/lec01_space_vector_dq.py --answers  # '해보기' 답 확인

실습 목록
    1. 평형 3상과 3상 순시전력 (합이 일정함을 확인)
    2. 공간벡터와 Clarke 변환 (두 계산이 같은지, 길이가 피크와 같은지)
    3. 예제 1: 30° 늦은 전류의 id, iq, P, Q
    4. 예제 2: 전압 진폭·위상 변화를 dq로 보기
    해보기 A. 평형 5고조파를 더하면 dq에 몇 Hz 리플이 생기나?
    해보기 B. PLL이 θ를 10° 늦게 잡으면 vq의 부호는?
모든 값은 pu (1 pu = 정격 상전압 진폭).
"""
import numpy as np

from common import header, check, parse, plt_ready, savefig, PHASE, BLUE, ORANGE, NAVY

F0 = 60.0
WB = 2 * np.pi * F0
A = np.exp(2j * np.pi / 3)          # 120° 회전 연산자 a


def abc(amp: float, phase: float, t: np.ndarray):
    """평형 3상 (a상 = amp·cos(ωt + phase))."""
    return (amp * np.cos(WB * t + phase),
            amp * np.cos(WB * t + phase - 2 * np.pi / 3),
            amp * np.cos(WB * t + phase + 2 * np.pi / 3))


def space_vector(xa, xb, xc):
    """진폭 불변 공간벡터 x = (2/3)(xa + a·xb + a²·xc)."""
    return (2 / 3) * (xa + A * xb + A**2 * xc)


def clarke(xa, xb, xc):
    """Clarke 행렬 (진폭 불변): α, β, 0 성분."""
    alpha = (2 / 3) * (xa - 0.5 * xb - 0.5 * xc)
    beta = (xb - xc) / np.sqrt(3)
    zero = (xa + xb + xc) / 3
    return alpha, beta, zero


def park(x, theta):
    """Park 변환 x_dq = x·e^{-jθ}."""
    return x * np.exp(-1j * theta)


def practice_1(args):
    header("실습 1 · 평형 3상과 순시전력")
    t = np.linspace(0, 2 / F0, 2001)
    va, vb, vc = abc(1.0, 0.0, t)
    phi = np.arccos(0.8)                       # 역률 0.8
    ia, ib, ic = abc(1.0, -phi, t)
    print(f"  va + vb + vc 의 최대 절댓값 = {np.max(np.abs(va + vb + vc)):.2e}  (평형이면 0)")
    p = va * ia + vb * ib + vc * ic
    print(f"  3상 순시전력: 최소 {p.min():.4f}, 최대 {p.max():.4f}  (일정)")
    check("p = (3/2)·V·I·cosφ", p.mean(), 1.5 * 0.8, 1e-6)
    vab = va - vb
    check("선간전압 진폭 √3", np.max(vab), np.sqrt(3), 1e-3)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
        for k, (x, n) in enumerate(((va, "a"), (vb, "b"), (vc, "c"))):
            ax[0].plot(t * 1e3, x, color=PHASE[n], label=f"v{n}")
        ax[0].set_ylabel("상전압 [pu]"); ax[0].legend(ncol=3, loc="upper right")
        for x, i, n in ((va, ia, "a"), (vb, ib, "b"), (vc, ic, "c")):
            ax[1].plot(t * 1e3, x * i, color=PHASE[n], lw=1.2, label=f"p{n}")
        ax[1].plot(t * 1e3, p, color=NAVY, lw=3, label="합")
        ax[1].set_ylabel("순시전력 [pu]"); ax[1].set_xlabel("시간 [ms]"); ax[1].legend(ncol=4, loc="upper right")
        savefig(fig, "lec01_1_3상_순시전력.png")


def practice_2(args):
    header("실습 2 · 공간벡터와 Clarke 변환")
    t = np.linspace(0, 1 / F0, 721)
    va, vb, vc = abc(1.0, 0.0, t)
    v = space_vector(va, vb, vc)
    al, be, z = clarke(va, vb, vc)
    print(f"  |공간벡터 − (α + jβ)| 최대 = {np.max(np.abs(v - (al + 1j * be))):.2e}  (같은 것)")
    check("공간벡터 길이 (= 상전압 피크)", np.mean(np.abs(v)), 1.0, 1e-9)
    check("영상분 (평형이면 0)", np.max(np.abs(z)), 0.0, 1e-9)
    ang = np.unwrap(np.angle(v))
    rate = (ang[-1] - ang[0]) / (t[-1] - t[0]) / (2 * np.pi)
    check("회전 속도 [Hz]", rate, F0, 1e-6)
    # 공통 성분 k 는 공간벡터에서 사라진다
    k = 0.37
    print(f"  세 상에 같은 값 {k}를 더해도 공간벡터 변화 = {np.max(np.abs(space_vector(va + k, vb + k, vc + k) - v)):.2e}")


def practice_3(args):
    header("실습 3 · 예제 1: 30° 늦은 전류의 id, iq, P, Q")
    t = np.arange(0, 0.05, 1e-5)
    theta = WB * t                              # d축을 a상 전압에 맞춤
    i_sv = space_vector(*abc(1.0, -np.pi / 6, t))
    v_sv = space_vector(*abc(1.0, 0.0, t))
    i_dq, v_dq = park(i_sv, theta), park(v_sv, theta)
    id_, iq = i_dq.real.mean(), i_dq.imag.mean()
    s = v_dq * np.conj(i_dq)                    # pu 에서 P + jQ = v·i*
    check("id", id_, 0.866, 1e-3)
    check("iq", iq, -0.5, 1e-3)
    check("P = vd·id", s.real.mean(), 0.866, 1e-3)
    check("Q = −vd·iq", s.imag.mean(), 0.5, 1e-3)
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(3, 1, figsize=(8, 6.5), sharex=True)
        m = t <= 2 / F0
        for x, n in zip(abc(1.0, -np.pi / 6, t), "abc"):
            ax[0].plot(t[m] * 1e3, x[m], color=PHASE[n], label=f"i{n}")
        ax[1].plot(t[m] * 1e3, i_sv.real[m], color=BLUE, label="iα"); ax[1].plot(t[m] * 1e3, i_sv.imag[m], color=ORANGE, label="iβ")
        ax[2].plot(t[m] * 1e3, i_dq.real[m], color=BLUE, label="id"); ax[2].plot(t[m] * 1e3, i_dq.imag[m], color=ORANGE, label="iq")
        for a_, lab in zip(ax, ("abc", "αβ", "dq")):
            a_.set_ylabel(lab); a_.legend(ncol=3, loc="upper right"); a_.set_ylim(-1.3, 1.3)
        ax[2].set_xlabel("시간 [ms]")
        savefig(fig, "lec01_3_abc_ab_dq.png")


def practice_4(args):
    header("실습 4 · 예제 2: 전압 진폭·위상 변화를 dq로 보기")
    t = np.arange(0, 0.075, 1e-5)
    amp = np.where(t < 0.025, 1.0, 0.7)
    ph = np.where(t < 0.05, 0.0, np.pi / 6)
    va = amp * np.cos(WB * t + ph)
    vb = amp * np.cos(WB * t + ph - 2 * np.pi / 3)
    vc = amp * np.cos(WB * t + ph + 2 * np.pi / 3)
    v_dq = park(space_vector(va, vb, vc), WB * t)
    for lo, hi, name in ((0.0, 0.025, "처음"), (0.025, 0.05, "진폭 0.7"), (0.05, 0.075, "위상 +30°")):
        m = (t > lo + 1e-3) & (t < hi)
        print(f"  {name:8s}: vd = {v_dq.real[m].mean():.3f}, vq = {v_dq.imag[m].mean():.3f}")
    if args.plot:
        plt = plt_ready()
        fig, ax = plt.subplots(figsize=(8, 3.6))
        ax.plot(t * 1e3, va, color="#b8c2ce", lw=1, label="va")
        ax.plot(t * 1e3, v_dq.real, color=BLUE, lw=2.5, label="vd")
        ax.plot(t * 1e3, v_dq.imag, color=ORANGE, lw=2.5, label="vq")
        ax.set_xlabel("시간 [ms]"); ax.set_ylabel("[pu]"); ax.legend(ncol=3)
        savefig(fig, "lec01_4_dq_예제.png")


def try_a(args):
    header("해보기 A · 평형 5고조파 0.1 pu 를 더하면 dq 에 몇 Hz 리플이 생기나?")
    t = np.arange(0, 0.1, 1e-5)
    ia, ib, ic = abc(1.0, 0.0, t)
    # 평형 5고조파: a, b, c 각각 cos(5(ωt − 0, 120°, 240°))
    h5 = [0.1 * np.cos(5 * (WB * t - k * 2 * np.pi / 3)) for k in range(3)]
    # 바꿔 보기: 7고조파(정상분)로 바꾸면 몇 Hz가 될까? cos(7(ωt − k·120°))
    i_dq = park(space_vector(ia + h5[0], ib + h5[1], ic + h5[2]), WB * t)
    x = i_dq.real - i_dq.real.mean()
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freq = np.fft.rfftfreq(len(x), 1e-5)
    f_peak = freq[np.argmax(spec)]
    print(f"  dq 리플의 주된 주파수 = {f_peak:.0f} Hz")
    if args.answers:
        print("  답: 360 Hz. 평형 5고조파는 역상(시계 방향)으로 5ω로 돈다. 공간벡터는 e^{-j5ωt},")
        print("      Park 의 e^{-jωt}를 곱하면 e^{-j6ωt} → 6 × 60 = 360 Hz 로 보인다.")


def try_b(args):
    header("해보기 B · PLL 이 θ 를 10° 늦게 잡으면 vq 의 부호는?")
    t = np.arange(0, 0.05, 1e-5)
    v = space_vector(*abc(1.0, 0.0, t))
    theta_err = np.deg2rad(-10.0)
    # 바꿔 보기: theta_err 를 +10° 로 바꾸면 부호가 어떻게 되나?
    vq = park(v, WB * t + theta_err).imag.mean()
    print(f"  vq = {vq:+.3f} pu")
    if args.answers:
        print("  답: 양수(+0.174). d축이 전압보다 10° 뒤에 있으니 전압 벡터가 d축보다 앞서 보인다.")
        print("      PLL 은 이 vq 를 0 으로 만들도록 θ 를 앞당긴다 (6강).")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0])
    for fn in (practice_1, practice_2, practice_3, practice_4, try_a, try_b):
        fn(args)
