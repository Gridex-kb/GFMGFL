"""
EMT 모델 회귀 테스트 (pytest 또는 `python test_emt.py` 로 실행, 약 1분)

물리적으로 반드시 성립해야 하는 성질만 검사한다.
속도를 위해 dt = 10 µs 로 돌린다. 1 µs 결과와의 차이는 convergence.py 로 확인한다.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfm_gfl_emt import Params, Scenario, simulate, steady_state  # noqa: E402

T_EV = 0.2
DT = 10e-6


def _run(mode, p, **ev):
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
    """GFL 정상상태 PCC–계통 위상차가 P = V²/X·sin δ 와 일치 (X = Lt + 1/SCR)."""
    p = Params(P_ref=0.6, scr=3.0)
    t, r = _run("GFL", p, t_end=0.3)
    X = p.Lt + 1.0 / p.scr
    delta_theory = math.degrees(math.asin(0.6 * X / 1.0))
    # delta_deg 는 컨트롤러(PLL) 각 - 계통 각 = PCC 전압각 - 계통 각
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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
