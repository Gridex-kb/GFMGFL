"""3강 실습 · 필터·변압기·측정점

실행 (저장소 루트에서):
    python practice/lec03_filter_measurement.py           # 해석 실습
    python practice/lec03_filter_measurement.py --plot    # 보드 선도 등 그림 저장
    python practice/lec03_filter_measurement.py --emt     # EMT: 실측 리플, 측정점별 σ(P) (약 6 s)
    python practice/lec03_filter_measurement.py --answers

실습 목록
    1. LCL 공진 주파수: 강계통과 SCR별
    2. 컨버터 전압 → 변압기 전류 이득: L 필터, LCL(Rd=0), LCL(Rd=2), 5 kHz 감쇠
    3. 스위칭 리플 상한 V_dc/(4·L·f_sw)
    4. (EMT) 실제 리플과 측정점별 전력 잡음
    해보기 A. Lf 를 0.3 pu 로 키우면 리플 상한과 공진은?
    해보기 B. 공진이 전류 제어 대역 800 Hz 아래로 내려오는 SCR 은?
"""
import numpy as np

from common import header, check, parse, plt_ready, savefig, BLUE, ORANGE, MUTED

from gfm_gfl_emt import Params

P = Params()
VDC = P.V_dc / P.V_base_peak


def f_res(Lf=P.Lf, Lg=P.Lt, Cf=P.Cf):
    return P.f0 * np.sqrt((Lf + Lg) / (Lf * Lg * Cf))


def gain_db(f, Rd=None, Lf=P.Lf, Lg=P.Lt):
    """컨버터 전압 → 계통측(변압기) 전류. Rd=None 이면 L 필터(Lf + Lg)."""
    h = np.asarray(f) / P.f0
    if Rd is None:
        return 20 * np.log10(1 / np.abs(P.Rf + P.Rt + 1j * h * (Lf + Lg)))
    Zf, Zg = P.Rf + 1j * h * Lf, P.Rt + 1j * h * Lg
    Zc = Rd + 1 / (1j * h * P.Cf)
    i_f = 1 / (Zf + Zc * Zg / (Zc + Zg))
    return 20 * np.log10(np.abs(i_f * Zc / (Zc + Zg)))


def ripple_bound(Lf=P.Lf):
    return VDC / (4 * (Lf / P.wb) * P.f_sw)


def practice_1(args):
    header("실습 1 · LCL 공진 주파수")
    check("강계통 (Lg = Lt)", f_res(), 1039, 1)
    for scr in (10, 5, 3, 2, 1.5):
        print(f"  SCR {scr:>4}: Lg = {P.Lt + 1/scr:.3f} → f_res = {f_res(Lg=P.Lt + 1/scr):5.0f} Hz")


def practice_2(args):
    header("실습 2 · 주파수 응답과 5 kHz 감쇠")
    for name, rd in (("L 필터 0.3 pu", None), ("LCL Rd = 0", 0.0), ("LCL Rd = 2", P.Rd)):
        print(f"  {name:14s}: 5 kHz 이득 = {gain_db(P.f_sw, rd):6.1f} dB")
    print(f"  공진에서 Cf 리액턴스 1/(h·B) = {1 / (f_res() / P.f0 * P.Cf):.2f} pu  (Rd = {P.Rd} 보다 작다)")
    if args.plot:
        plt = plt_ready()
        f = np.logspace(1, 4.3, 2000)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.semilogx(f, gain_db(f, None), color=MUTED, ls="--", label="L 필터 (0.3 pu)")
        ax.semilogx(f, gain_db(f, 0.0), color=ORANGE, label="LCL, Rd = 0")
        ax.semilogx(f, gain_db(f, P.Rd), color=BLUE, lw=2.5, label="LCL, Rd = 2 (모델)")
        ax.axvline(f_res(), color=MUTED, ls=":"); ax.axvline(P.f_sw, color=MUTED, ls=":")
        ax.set_ylim(-80, 45); ax.set_xlabel("주파수 [Hz]"); ax.set_ylabel("|i_t / v_c| [dB]"); ax.legend()
        savefig(fig, "lec03_2_보드.png")


def practice_3(args):
    header("실습 3 · 리플 상한")
    print(f"  V_dc = {VDC:.3f} pu, L = Lf/ωb = {P.Lf / P.wb * 1e3:.3f} ms(pu 기준)")
    check("Δi_pp 상한", ripple_bound(), 0.213, 1e-3)
    m = np.linspace(-1, 1, 5)
    print("  변조 지수 m 에 따른 리플 (1 − m²) 배:", np.round(ripple_bound() * (1 - m**2), 3))


def practice_4(args):
    header("실습 4 · (EMT) 실제 리플과 측정점별 전력 잡음")
    if not getattr(args, "emt", False):
        print("  --emt 옵션을 주면 실행한다 (약 6 s).")
        return
    import gfm_gfl_emt as emt
    from gfm_gfl_emt import Scenario, simulate, steady_state, replace
    log, fine = [], []

    class Logged(emt.Inverter):
        def sample(self, t, x):
            v_term, v_pcc, i_t = self.network(t, x)[:3]
            i_f = complex(x[emt.IF_RE], x[emt.IF_IM])
            log.append(((v_pcc * i_t.conjugate()).real, (v_term * i_f.conjugate()).real))
            super().sample(t, x)

        def pcc_voltage(self, t, x):
            fine.append(x[emt.IF_RE])
            return super().pcc_voltage(t, x)

    orig = emt.Inverter
    emt.Inverter = Logged
    try:
        pa = Params(converter="average", scr=10.0)
        x0 = steady_state("GFM", pa, t_init=1.5, dt=1e-5)
        simulate("GFM", replace(pa, converter="switching"), Scenario(t_end=0.2), x0=x0, hires=(0.15, 0.2))
    finally:
        emt.Inverter = orig
    Pm = np.array(log[1000:])
    ia = np.array(fine)
    rip = (ia - np.convolve(ia, np.ones(100) / 100, mode="same"))[100:-100]
    check("실측 리플 [pu p-p]", rip.max() - rip.min(), 0.111, 0.01)
    print(f"  σ(P) 변압기·PCC = {Pm[:, 0].std():.4f} pu, Lf·필터 단자 = {Pm[:, 1].std():.4f} pu")


def try_a(args):
    header("해보기 A · Lf = 0.3 pu 이면?")
    print(f"  리플 상한 = {ripple_bound(0.3):.3f} pu, 강계통 공진 = {f_res(Lf=0.3):.0f} Hz")
    if args.answers:
        print("  답: 0.142 pu (2/3 배), 980 Hz. 대가: 기본파 전압강하가 커져 1.303 pu 여유를 더 쓴다.")


def try_b(args):
    header("해보기 B · 공진이 800 Hz 아래로 내려오는 SCR")
    scr = np.linspace(1.0, 20.0, 19001)
    fr = f_res(Lg=P.Lt + 1 / scr)
    below = scr[fr < 800]
    print(f"  공진 < 800 Hz 인 SCR 범위: SCR ≤ {below.max():.2f}" if below.size else "  없음")
    if args.answers:
        print("  답: SCR 약 6.4 이하. 강계통 설계만 보면 놓치는 영역이다 (8강 약계통).")


if __name__ == "__main__":
    args = parse(__doc__.splitlines()[0], emt=True)
    for fn in (practice_1, practice_2, practice_3, practice_4, try_a, try_b):
        fn(args)
