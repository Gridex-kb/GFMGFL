"""
EMT 모델 회귀 테스트 (pytest 또는 `python test_emt.py` 로 실행, 약 2분)

물리적으로 반드시 성립해야 하는 성질만 검사한다.
- 물리 성질 검사: 속도를 위해 평균값 모델(converter="average"), dt = 10 µs
- 스위칭 모델 검사: 기본 설정(5 kHz PWM, dt = 2 µs)으로 정상상태·리플·변조 한계 확인
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfm_gfl_emt import Params, Scenario, replace, simulate, steady_state  # noqa: E402

T_EV = 0.2
DT = 10e-6


def _run(mode, p, **ev):
    p = replace(p, converter="average")
    x0 = steady_state(mode, p, dt=DT)
    r = simulate(mode, p, Scenario(**ev), x0=x0, dt=DT)
    t = np.asarray(r["t"]) - T_EV
    return t, {k: np.asarray(v) for k, v in r.items() if isinstance(v, list)}


def test_steady_state_tracks_reference():
    """정상상태에서 두 방식 모두 P 지령과 PCC 전압 1 pu 를 지킨다."""
    for mode in ("GFL", "GFM"):
        p = Params(P_ref=0.6, scr=3.0)
        t, r = _run(mode, p, t_end=0.5)
        assert abs(r["P"].mean() - 0.6) < 0.02, mode
        assert abs(r["V"].mean() - 1.0) < 0.02, mode
        assert r["P"].std() < 0.01, mode


def test_power_flow_matches_phasor_theory():
    """GFL 정상상태 PCC–계통 위상차가 P = V²/X·sin δ 와 일치 (X = 1/SCR, PCC 분로 G_bus 소비분 제외)."""
    p = Params(P_ref=0.6, scr=3.0)
    t, r = _run("GFL", p, t_end=0.3)
    X = 1.0 / p.scr
    P_grid = r["P"].mean() - p.G_bus * r["V"].mean() ** 2
    delta_theory = math.degrees(math.asin(P_grid * X / 1.0))
    # delta_deg 는 컨트롤러(PLL) 각 - 계통 각 = PCC 전압각 - 계통 각 (PLL 은 PCC 전압에 동기)
    assert abs(r["delta_deg"].mean() - delta_theory) < 2.0


def test_gfm_phase_jump_power_is_immediate_gfl_is_not():
    """계통 위상 -20° 점프: GFM 은 10 ms 안에 ΔP > 0.3 pu, GFL 은 거의 0."""
    out = {}
    for mode in ("GFL", "GFM"):
        p = Params(P_ref=0.5, scr=3.0)
        t, r = _run(mode, p, t_end=0.3,
                    grid_phase=lambda tt: math.radians(-20) if tt >= T_EV else 0.0)
        m = (t >= 0) & (t < 0.01)
        out[mode] = r["P"][m].max() - 0.5
    assert out["GFM"] > 0.3
    assert out["GFL"] < 0.1


def test_islanding_gfm_holds_voltage_and_droop_frequency():
    """계통 분리 후 GFM 은 V≈1, f = f0 + 드룹 × (P* - P_load) 를 유지, GFL 은 실패."""
    res = {}
    for mode in ("GFL", "GFM"):
        p = Params(P_ref=0.5, P_load=0.8, scr=3.0)
        t, r = _run(mode, p, t_end=1.4, breaker_closed=lambda tt: tt < T_EV)
        m = t > 1.0
        res[mode] = (r["freq"][m].mean(), r["V"][m].mean())
    f_gfm, v_gfm = res["GFM"]
    f_expected = 60.0 * (1 + 0.02 * (0.5 - 0.8))
    assert abs(f_gfm - f_expected) < 0.1
    assert abs(v_gfm - 1.0) < 0.03
    assert abs(res["GFL"][0] - 60.0) > 1.0


def test_gfm_current_limit_during_fault():
    """고장 중 GFM 전류가 한계(1.2 pu) 근처로 제한되고 고장 후 동기를 유지한다."""
    p = Params(P_ref=0.8, scr=3.0)
    t, r = _run("GFM", p, t_end=1.6, grid_v=lambda tt: 0.3 if T_EV <= tt < T_EV + 0.15 else 1.0)
    m = (t > 0.02) & (t < 0.15)
    assert r["I"][m].max() < 1.3
    assert abs(r["P"][t > 1.2].mean() - 0.8) < 0.08


def test_switching_model_steady_state_and_ripple():
    """5 kHz 스위칭 모델: 샘플 평균은 지령을 추종하고, 순시 전류에는 스위칭 리플이 있다."""
    p = Params(P_ref=0.5, scr=3.0)                       # 기본 converter="switching"
    assert abs(p.V_conv_max - 700 / math.sqrt(3) / (380 * math.sqrt(2 / 3))) < 1e-9   # 1.303 pu
    for mode in ("GFL", "GFM"):
        r = simulate(mode, p, Scenario(t_end=1.0, p_ref=lambda t: 0.5 * min(1.0, t / 0.3)),
                     dt=2e-6, hires=(0.95, 0.97))
        t, P = np.asarray(r["t"]), np.asarray(r["P"])
        assert abs(P[t > 0.8].mean() - 0.5) < 0.05, mode
        h = r["hires"]
        th, ia = np.asarray(h["t"]), np.asarray(h["ia"])
        A = np.vstack([np.cos(2 * np.pi * 60 * th), np.sin(2 * np.pi * 60 * th)]).T
        c, *_ = np.linalg.lstsq(A, ia, rcond=None)
        ripple = np.ptp(ia - A @ c)
        assert 0.03 < ripple < 0.3, (mode, ripple)       # 5 kHz 리플 존재 (Lf 0.2 pu 기준 약 0.1 pu)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
