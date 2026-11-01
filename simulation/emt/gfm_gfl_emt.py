"""
GFM / GFL 인버터 평균값 EMT 시뮬레이터 (교육·비교용)
=====================================================

- 3상 순시값을 복소 αβ 공간벡터로 다룬다 (x = xα + j·xβ, 진폭 불변 변환).
  |v| = 1 pu 이면 상전압 진폭이 정격이다. P = Re(v·i*), Q = Im(v·i*).
- 2레벨 전압형 컨버터(VSC) + LC 필터(커패시터 직렬 댐핑저항) + 변압기 + PCC(변압기 고압측) 모선
  + 테브난 등가 계통(SCR, X/R) + 계통 차단기. 국부 부하와 PCC 고장은 PCC 모선에 연결한다.
- 측정: 제어용 P, Q, V 와 PLL·가상 어드미턴스 전압은 변압기 전류와 PCC 전압으로 측정한다.
  전류 제어·전류 제한만 컨버터측 전류(Lf)를 쓴다. 스위칭 리플이 큰 Lf 전류로 전력을 재지 않기 위함이다.
  * converter="switching"(기본): 5 kHz 삼각파 PWM(min-max 영상분 주입 = SVPWM 등가),
    DC 700 V / AC 380 V, 반송파 꼭짓점 동기 샘플링(10 kHz, 2회 갱신), 1샘플 계산 지연.
  * converter="average": 스위칭 평균화 + 1차 지연 근사 (빠른 검토·회귀 테스트용).
- 같은 하드웨어·같은 내부 전류제어기에 외부 루프만 바꿔 GFL / GFM 을 비교한다.
    * GFL : SRF-PLL → P/Q(또는 V) 지령 → dq 전류 지령 (+선택: 합성관성)
    * GFM : VSM(가상동기기, 관성 H·댐핑 D) → 내부 기전력 E∠θ →
            동적 가상 인덕턴스(가상 어드미턴스) → 전류 지령 (원형 전류제한)
- 고정 스텝 RK4 적분, 기본 해석 시간 간격(solution time step) dt = 2 µs, 기록 간격 100 µs
  (반송파 꼭짓점과 동기되므로 기록값은 리플 평균값에 해당).
  단위는 인버터 정격 기준 pu, 시간은 초.

이 모델은 개념 검증·교육용이다. 계통연계 검토에는 제조사 EMT 모델(PSCAD 등)을 써야 한다.
"""
from __future__ import annotations

import cmath
import hashlib
import math
import os
import pickle
from dataclasses import asdict, dataclass, field, replace
from typing import Callable

TWO_PI = 2.0 * math.pi
A120 = cmath.exp(-1j * TWO_PI / 3)   # b상 추출: Re(v·A120)
A240 = cmath.exp(1j * TWO_PI / 3)    # c상 추출: Re(v·A240)
DT_DEFAULT = 2e-6        # 해석 시간 간격 [s]
RECORD_DT_DEFAULT = 1e-4 # 결과 기록 간격 [s]


# ----------------------------------------------------------------------------
# 파라미터
# ----------------------------------------------------------------------------
@dataclass
class Params:
    # 계통
    f0: float = 60.0              # 정격 주파수 [Hz] (한국 60 Hz)
    scr: float = 3.0              # 단락비 (인버터 정격 기준)
    xr: float = 10.0              # 계통 X/R
    # 필터·변압기 [pu]
    Lf: float = 0.20              # 컨버터측 필터 [pu]
    Rf: float = 0.005
    Cf: float = 0.05              # 커패시터 서셉턴스 [pu]
    Rd: float = 2.0               # 커패시터 직렬 댐핑 저항 [pu]
    Lt: float = 0.10              # 변압기 누설 리액턴스 [pu]
    Rt: float = 0.005
    # 국부 부하 (PCC, 저항성). 0 이면 부하 없음.
    P_load: float = 0.0
    G_bus: float = 0.03           # PCC 모선 상시 저항성 분로 [pu] (보조 부하·손실 등가, 수치 안정용)
    # 공통 내부 전류제어
    f_cc: float = 800.0           # 전류제어 대역폭 [Hz]
    I_max: float = 1.2            # 전류 한계 [pu]
    # 전압 기준: DC 링크 700 V, AC 380 V(선간 실효). 1 pu = 상전압 진폭 380·√2/√3 = 310.3 V
    V_dc: float = 700.0           # DC 링크 전압 [V] (이상적 직류원으로 가정)
    V_ac_ll: float = 380.0        # AC 정격 선간전압 실효값 [V]
    modulation: str = "svpwm"     # "svpwm": 최대 상전압 진폭 V_dc/√3, "spwm": V_dc/2
    converter: str = "switching"  # "switching" 또는 "average"
    f_sw: float = 5000.0          # 스위칭(반송파) 주파수 [Hz]. 샘플링은 2 × f_sw (2회 갱신)
    t_delay: float = 150e-6       # average 모델 전용: 계산·PWM 지연 1차 근사 [s] (= 1.5 / 10 kHz)
    # 공통 지령
    P_ref: float = 0.5
    V_ref: float = 1.0
    droop: float = 0.02           # P-f 드룹 (2 % → D = 50 pu)
    # GFL
    f_pll: float = 20.0           # PLL 고유주파수 [Hz]
    pll_zeta: float = 0.707
    pll_dw_max: float = 0.1       # PLL 주파수 제한 [pu]
    gfl_vctrl_ki: float = 20.0    # PCC 전압 → Q 지령 적분이득 [pu/s/pu]
    gfl_q_max: float = 0.6
    gfl_droop: bool = False       # GFL P-f 드룹 (PLL 측정 주파수 기반). RoCoF 시나리오에서만 켬
    gfl_H_syn: float = 0.0        # 합성관성 상수 [s] (0 이면 사용 안 함)
    gfl_fmeas_hz: float = 2.0     # 드룹·합성관성용 주파수 측정 필터 [Hz] (5 Hz 이상이면 합성관성 루프 불안정)
    gfl_dfdt_hz: float = 2.0      # 합성관성 df/dt 추가 필터 [Hz]
    gfl_frt_enter: float = 0.85   # FRT 진입 전압 [pu]
    gfl_frt_exit: float = 0.92    # FRT 해제 전압 [pu] (히스테리시스)
    gfl_frt_hold: float = 0.03    # FRT 최소 유지시간 [s]
    gfl_frt_iq: float = 0.95      # FRT 중 무효전류 = gfl_frt_iq × I_max (고정, 측정전압 되먹임 없음)
    # GFM (VSM)
    H: float = 4.0                # 가상 관성상수 [s]
    Xv: float = 0.30              # 가상 리액턴스 [pu]
    Rv: float = 0.05              # 가상 저항 [pu]
    gfm_vctrl_ki: float = 5.0     # PCC 전압 → E 적분이득 [pu/s/pu]
    gfm_limit_freeze: bool = True # 전류제한 중 VSM 가속 억제(동기 유지 보정)
    # 측정 필터
    f_meas: float = 20.0          # P, Q, |V| 측정 LPF [Hz]
    ff_gain: float = 0.0          # 전류제어 전압 피드포워드 이득. 지연이 있는 약계통에서 순시 피드포워드는
                                  # 공통 내부루프 불안정(100~200 Hz)을 일으키므로 기본은 끔 (README 참고)
    f_vff: float = 100.0          # 전압 피드포워드 LPF (dq 좌표) [Hz]. 0 이면 순시값

    @property
    def V_base_peak(self) -> float:
        """1 pu 상전압 진폭 [V]."""
        return self.V_ac_ll * math.sqrt(2.0 / 3.0)

    @property
    def V_conv_max(self) -> float:
        """선형 변조 영역에서 컨버터가 낼 수 있는 최대 상전압 진폭 [pu] (700 V/380 V, SVPWM → 1.302)."""
        vmax = self.V_dc / math.sqrt(3.0) if self.modulation == "svpwm" else self.V_dc / 2.0
        return vmax / self.V_base_peak

    @property
    def wb(self) -> float:
        return TWO_PI * self.f0

    @property
    def D(self) -> float:
        return 1.0 / self.droop


@dataclass
class Scenario:
    """시간 함수로 주어지는 외란. 기본값은 '아무 일도 없음'."""
    name: str = "base"
    t_end: float = 2.0
    grid_f: Callable[[float], float] = lambda t: 1.0           # 계통 주파수 [pu]
    grid_phase: Callable[[float], float] = lambda t: 0.0       # 계통 위상 오프셋 [rad]
    grid_v: Callable[[float], float] = lambda t: 1.0           # 계통 전압 크기 [pu]
    scr: Callable[[float], float] | None = None                # 단락비 (None 이면 Params.scr)
    breaker_closed: Callable[[float], bool] = lambda t: True   # 계통 차단기
    p_ref: Callable[[float], float] | None = None              # 유효전력 지령
    pcc_fault_g: Callable[[float], float] | None = None        # PCC 지락(3상) 고장 컨덕턴스 [pu], 0 이면 없음


def ramp_p(p_final: float, t_ramp: float = 0.25):
    """초기화용: 0 → p_final 로 t_ramp 동안 램프."""
    return lambda t: p_final * min(1.0, t / t_ramp)


# ----------------------------------------------------------------------------
# 상태 인덱스
# ----------------------------------------------------------------------------
IF_RE, IF_IM, VC_RE, VC_IM, IG_RE, IG_IM = range(6)   # IG = 변압기 전류
TH_G, TH_C, X_W, XCC_RE, XCC_IM, PF, QF, VF, X_V, IV_RE, IV_IM, F_MEAS, VFF_D, VFF_Q, DFDT, VD_RE, VD_IM, IS_RE, IS_IM = range(6, 25)
N_STATES = 25   # IS = 계통(테브난) 지로 전류


class Inverter:
    """mode = 'GFL' 또는 'GFM'."""

    def __init__(self, mode: str, p: Params, sc: Scenario):
        if mode not in ("GFL", "GFM"):
            raise ValueError(mode)
        self.mode = mode
        self.p = p
        self.sc = sc
        wb = p.wb
        # 전류제어 PI (dq): Kp = ωcc·L/ωb, Ki = Kp·ωcc/5
        wcc = TWO_PI * p.f_cc
        self.kp_c = wcc * p.Lf / wb
        self.ki_c = self.kp_c * wcc / 5.0
        # PLL PI
        wn = TWO_PI * p.f_pll
        self.kp_pll = 2.0 * p.pll_zeta * wn / wb
        self.ki_pll = wn * wn / wb
        self.w_meas = TWO_PI * p.f_meas
        self.w_fm = TWO_PI * p.gfl_fmeas_hz
        self.w_vff = TWO_PI * p.f_vff
        self.w_dfdt = TWO_PI * p.gfl_dfdt_hz
        self.frt = False  # GFL FRT 모드 (스텝마다 갱신되는 이산 상태)
        self.t_frt = -1.0
        self.G_L = p.P_load  # 저항 부하 컨덕턴스 (1 pu 전압에서 P_load)
        # 스위칭·디지털 제어 상태
        self.sw = p.converter == "switching"
        self.Ts = 1.0 / (2.0 * p.f_sw)          # 샘플링 주기 (반송파 꼭짓점)
        self.Tc = 1.0 / p.f_sw                  # 반송파 주기
        self.vdc = p.V_dc / p.V_base_peak       # DC 전압 [pu]
        self.meas = (1 + 0j, 0j, 0j)            # 샘플-홀드된 (v_pcc, i_변압기, i_f)
        self.v_pending = 1 + 0j                 # 이번 샘플에서 계산된 전압 지령 (다음 샘플에 적용)
        self.v_applied = 1 + 0j                 # 현재 PWM 에 적용 중인 지령 (αβ, pu)
        self.vpole = 1 + 0j                     # 현재 스위치 상태가 만드는 컨버터 전압 (αβ, pu)
        self.next_sample = 0.0
        self.duty = (0.0, 0.0, 0.0)
        self.th_hold = 0.0                      # 샘플 시점의 제어 각 (dq 변환은 이 각으로)
        # 출력 버퍼
        self.aux: dict = {}

    # ---- 계통 파라미터 ----
    def grid_impedance(self, t: float) -> tuple[float, float]:
        scr = self.sc.scr(t) if self.sc.scr else self.p.scr
        X = 1.0 / scr
        return X, X / self.p.xr

    # ---- 스텝 후 이산 상태 갱신 ----
    def post_step(self, t: float, x: list[float]) -> None:
        if self.mode == "GFL":
            if not self.frt and x[VF] < self.p.gfl_frt_enter:
                self.frt, self.t_frt = True, t
            elif self.frt and x[VF] > self.p.gfl_frt_exit and t - self.t_frt > self.p.gfl_frt_hold:
                self.frt = False

    # ---- 디지털 제어 샘플링과 PWM ----
    G_MIN = 1e-6  # G_bus 를 0 으로 두면 변압기·계통을 직렬로 처리

    def network(self, t: float, x: list[float]):
        """필터 단자 전압, PCC 전압, 변압기·계통 지로 전류와 그 미분을 계산한다."""
        p, sc, wb = self.p, self.sc, self.p.wb
        i_f = complex(x[IF_RE], x[IF_IM])
        i_t = complex(x[IG_RE], x[IG_IM])
        i_s = complex(x[IS_RE], x[IS_IM])
        closed = sc.breaker_closed(t)
        v_term = complex(x[VC_RE], x[VC_IM]) + p.Rd * (i_f - i_t)    # 필터 커패시터 단자 (변압기 저압측)
        G = p.G_bus + self.G_L + (sc.pcc_fault_g(t) if sc.pcc_fault_g else 0.0)
        Xth, Rth = self.grid_impedance(t)
        e_g = sc.grid_v(t) * cmath.exp(1j * (x[TH_G] + sc.grid_phase(t)))
        if not closed:
            i_s = 0j
            if G >= self.G_MIN:
                v_pcc = i_t / G
                di_t = (v_term - p.Rt * i_t - v_pcc) * (wb / p.Lt)
            else:
                v_pcc, di_t, i_t = v_term, 0j, 0j
            di_s = 0j
        elif G >= self.G_MIN:
            v_pcc = (i_t - i_s) / G
            di_t = (v_term - p.Rt * i_t - v_pcc) * (wb / p.Lt)
            di_s = (v_pcc - Rth * i_s - e_g) * (wb / Xth)
        else:  # 부하·고장 없음: 변압기와 계통이 직렬, i_s = i_t
            di_t = (v_term - (p.Rt + Rth) * i_t - e_g) * (wb / (p.Lt + Xth))
            v_pcc = e_g + Rth * i_t + di_t * (Xth / wb)
            di_s = di_t
            i_s = i_t
        return v_term, v_pcc, i_t, i_s, di_t, di_s, G, e_g, closed

    def pcc_voltage(self, t: float, x: list[float]) -> complex:
        return self.network(t, x)[1]

    def sample(self, t: float, x: list[float]) -> None:
        """반송파 꼭짓점에서 측정을 샘플-홀드하고, 지령을 계산해 다음 샘플에 적용 (1샘플 지연)."""
        net = self.network(t, x)
        self.meas = (net[1], net[2], complex(x[IF_RE], x[IF_IM]))
        self.th_hold = x[TH_C]
        self.v_applied = self.v_pending
        self.deriv(t, x)
        self.v_pending = self.aux["v_cmd"]
        # min-max 영상분 주입 (SVPWM 등가) → 상별 듀티 [-1, 1]
        v = self.v_applied
        va = v.real
        vb = (v * A120).real
        vc = (v * A240).real
        v0 = -0.5 * (max(va, vb, vc) + min(va, vb, vc))
        h = 0.5 * self.vdc
        self.duty = tuple(max(-1.0, min(1.0, (vx + v0) / h)) for vx in (va, vb, vc))

    def pwm(self, t: float) -> None:
        """삼각파 반송파(-1~1, t=0 에서 골)와 비교해 스위치 상태 → 극전압 αβ."""
        ph = (t / self.Tc) % 1.0
        c = 4.0 * ph - 1.0 if ph < 0.5 else 3.0 - 4.0 * ph
        h = 0.5 * self.vdc
        sa, sb, sc_ = (h if d > c else -h for d in self.duty)
        # 진폭 불변 Clarke: (2/3)(va + vb·e^{j2π/3} + vc·e^{-j2π/3}), 영상분은 자동 제거
        self.vpole = (2.0 / 3.0) * (sa + sb * A120.conjugate() + sc_ * A240.conjugate())

    # ---- 미분방정식 ----
    def deriv(self, t: float, x: list[float]) -> list[float]:
        p, sc, wb = self.p, self.sc, self.p.wb
        i_f = complex(x[IF_RE], x[IF_IM])
        v_term, v_pcc, i_t, i_s, di_t, di_s, G, e_g, closed = self.network(t, x)

        # 측정: 스위칭 모델은 샘플-홀드 값, 평균 모델은 순시값을 제어기에 넣는다
        #   전력·전압·위상 = PCC 전압 × 변압기 전류, 전류제어 = 컨버터측 전류
        v_m, it_m, i_m = self.meas if self.sw else (v_pcc, i_t, i_f)
        s_m = v_m * it_m.conjugate()
        P, Q = s_m.real, s_m.imag
        Vmag = abs(v_m)
        s_inst = v_pcc * i_t.conjugate()
        P_ref = sc.p_ref(t) if sc.p_ref else p.P_ref

        dx = [0.0] * N_STATES
        th_c = x[TH_C]
        # 디지털 제어: 샘플-홀드된 측정은 샘플 시점의 각으로 dq 변환한다
        th_ctl = self.th_hold if self.sw else th_c
        rot = cmath.exp(-1j * th_ctl)
        i_dq = i_m * rot
        v_dq = v_m * rot
        # 전류제어 피드포워드용 전압: dq 좌표에서 LPF (f_vff <= 0 이면 순시값)
        v_ff = complex(x[VFF_D], x[VFF_Q]) if p.f_vff > 0 else v_dq
        saturated = False

        if self.mode == "GFL":
            # --- SRF-PLL ---
            vq = v_dq.imag
            dw = self.kp_pll * vq + x[X_W]
            if dw > p.pll_dw_max:
                dw = p.pll_dw_max
            elif dw < -p.pll_dw_max:
                dw = -p.pll_dw_max
            dx[X_W] = self.ki_pll * vq
            if (x[X_W] >= p.pll_dw_max and vq > 0) or (x[X_W] <= -p.pll_dw_max and vq < 0):
                dx[X_W] = 0.0  # 적분기 anti-windup
            w_c = 1.0 + dw
            dx[TH_C] = wb * w_c
            # 주파수 측정 필터 (드룹·합성관성)
            dx[F_MEAS] = self.w_fm * (dw - x[F_MEAS])
            p_cmd = P_ref
            if p.gfl_droop:
                p_cmd += -p.D * x[F_MEAS]
            # 합성관성: 필터된 측정 주파수의 미분을 한 번 더 필터 (측정 기반 → 지연 존재)
            dx[DFDT] = self.w_dfdt * (dx[F_MEAS] - x[DFDT])
            if p.gfl_H_syn > 0:
                p_cmd += -2.0 * p.gfl_H_syn * x[DFDT]
            # --- 전압 제어 → Q 지령 ---
            dx[X_V] = p.gfl_vctrl_ki * (p.V_ref - x[VF])
            q_cmd = max(-p.gfl_q_max, min(p.gfl_q_max, x[X_V]))
            if (x[X_V] >= p.gfl_q_max and dx[X_V] > 0) or (x[X_V] <= -p.gfl_q_max and dx[X_V] < 0):
                dx[X_V] = 0.0
            vd = max(x[VF], 0.3)
            id_ref = p_cmd / vd
            iq_ref = -q_cmd / vd
            # --- FRT: 저전압 시 무효전류 우선 (고정 주입) ---
            if self.frt:
                iq_ref = -p.gfl_frt_iq * p.I_max
                id_room = math.sqrt(max(p.I_max ** 2 - iq_ref ** 2, 0.0))
                id_ref = max(-id_room, min(id_room, id_ref))
                saturated = True
            else:
                mag = math.hypot(id_ref, iq_ref)
                if mag > p.I_max:  # 유효전류 우선
                    id_ref = max(-p.I_max, min(p.I_max, id_ref))
                    iq_room = math.sqrt(max(p.I_max ** 2 - id_ref ** 2, 0.0))
                    iq_ref = max(-iq_room, min(iq_room, iq_ref))
                    saturated = True
            i_ref = complex(id_ref, iq_ref)
            self.aux = dict(w_c=w_c, E=float("nan"))
        else:
            # --- VSM: 2H dΔω/dt = P* - P - D·Δω ---
            dw = x[X_W]
            w_c = 1.0 + dw
            dx[TH_C] = wb * w_c
            # --- 전압 제어 → 내부 기전력 E ---
            dx[X_V] = p.gfm_vctrl_ki * (p.V_ref - x[VF])
            E = 1.0 + max(-0.3, min(0.3, x[X_V]))
            # anti-windup: E 가 한계에 걸리면 한계 밖으로 더 쌓지 않는다 (고장 후 과전압 방지)
            if (x[X_V] >= 0.3 and dx[X_V] > 0) or (x[X_V] <= -0.3 and dx[X_V] < 0):
                dx[X_V] = 0.0
            # --- 동적 가상 인덕턴스 (θ 회전좌표) ---
            #   (Xv/ωb) di/dt = E - v - Rv·i - j·ω·Xv·i
            i_v = complex(x[IV_RE], x[IV_IM])
            di_v = (E - v_dq - p.Rv * i_v - 1j * w_c * p.Xv * i_v) * (wb / p.Xv)
            mag = abs(i_v)
            if mag > p.I_max:
                i_ref = i_v * (p.I_max / mag)
                saturated = True
                # anti-windup: 한계 밖으로 커지는 방향 성분 제거
                radial = (di_v * i_v.conjugate()).real / mag
                if radial > 0:
                    di_v -= radial * i_v / mag
            else:
                i_ref = i_v
            dx[IV_RE], dx[IV_IM] = di_v.real, di_v.imag
            p_err = P_ref - x[PF]
            if saturated and p.gfm_limit_freeze and p_err > 0:
                p_err = 0.0  # 전류제한 중 가속(위상 이탈) 억제
            dx[X_W] = (p_err - p.D * dw) / (2.0 * p.H)
            self.aux = dict(w_c=w_c, E=E)

        # --- 공통 내부 전류제어 (θ_c 좌표) ---
        err = i_ref - i_dq
        x_cc = complex(x[XCC_RE], x[XCC_IM])
        v_conv_dq = p.ff_gain * v_ff + self.kp_c * err + x_cc + 1j * w_c * p.Lf * i_dq
        vm = abs(v_conv_dq)
        if vm > p.V_conv_max:
            v_conv_dq *= p.V_conv_max / vm
        else:
            d_cc = self.ki_c * err
            dx[XCC_RE], dx[XCC_IM] = d_cc.real, d_cc.imag
        # 출력: 샘플 시점 각 + 지연 보상(1.5 샘플 동안 회전할 각)으로 αβ 지령 생성
        th_out = th_ctl + (1.5 * self.Ts * wb * w_c if self.sw else 0.0)
        v_cmd = v_conv_dq * cmath.exp(1j * th_out)
        if self.sw:
            # 스위치 상태가 만든 극전압 (스텝 시작 시 결정, 스텝 동안 일정)
            v_conv = self.vpole
        # 계산·PWM 지연 (1차 지연): 실제 컨버터 출력은 지령을 늦게 따라간다
        elif p.t_delay > 0:
            v_conv = complex(x[VD_RE], x[VD_IM])
            d_vd = (v_cmd - v_conv) / p.t_delay
            dx[VD_RE], dx[VD_IM] = d_vd.real, d_vd.imag
        else:
            v_conv = v_cmd

        # --- 플랜트 ---
        di_f = (v_conv - p.Rf * i_f - v_term) * (wb / p.Lf)
        dv_c = (i_f - i_t) * (wb / p.Cf)
        dx[IF_RE], dx[IF_IM] = di_f.real, di_f.imag
        dx[VC_RE], dx[VC_IM] = dv_c.real, dv_c.imag
        dx[IG_RE], dx[IG_IM] = di_t.real, di_t.imag
        dx[IS_RE], dx[IS_IM] = di_s.real, di_s.imag
        dx[TH_G] = wb * sc.grid_f(t)
        # 측정 필터
        dx[PF] = self.w_meas * (P - x[PF])
        dx[QF] = self.w_meas * (Q - x[QF])
        dx[VF] = self.w_meas * (Vmag - x[VF])
        # dq 전압 필터 (회전좌표: 좌표 회전에 따른 항 포함 없이 dq 값 자체를 필터)
        d_vff = self.w_vff * (v_dq - v_ff) if p.f_vff > 0 else 0j
        dx[VFF_D], dx[VFF_Q] = d_vff.real, d_vff.imag

        self.aux.update(P=s_inst.real, Q=s_inst.imag, V=abs(v_pcc), v_p=v_pcc, v_term=v_term, i_f=i_f, i_g=i_t, e_g=e_g,
                        i_ref=i_ref, saturated=saturated, closed=closed, v_cmd=v_cmd, v_conv=v_conv)
        return dx


# ----------------------------------------------------------------------------
# 적분기
# ----------------------------------------------------------------------------
def simulate(mode: str, p: Params, sc: Scenario, dt: float = DT_DEFAULT,
             record_every: int | None = None, x0: list[float] | None = None,
             record_dt: float = RECORD_DT_DEFAULT,
             hires: tuple[float, float] | None = None) -> dict:
    """RK4 고정 스텝. 결과는 리스트 dict (numpy 변환은 호출측).

    x0 를 주면 그 상태에서 이어서 시작한다(웜스타트). 결과의 'x_final' 을 다음 x0 로 쓸 수 있다.
    """
    inv = Inverter(mode, p, sc)
    if record_every is None:
        record_every = max(1, int(round(record_dt / dt)))
    if x0 is not None:
        x = list(x0)
        x[TH_G] = x[TH_G] % TWO_PI
        x[TH_C] = x[TH_G] + ((x0[TH_C] - x0[TH_G] + math.pi) % TWO_PI - math.pi)
    else:
        x = [0.0] * N_STATES
        x[VC_RE] = 1.0      # 커패시터 전압 = 계통 전압으로 초기화
        x[VF] = 1.0
        x[VFF_D] = 1.0
        x[VD_RE] = 1.0
    out = {k: [] for k in (
        "t", "P", "Q", "V", "I", "freq", "grid_freq", "delta_deg", "E",
        "ia", "ib", "ic", "va", "vb", "vc", "sat", "id_ref_mag")}
    n = int(round(sc.t_end / dt))
    a120 = A120
    hires_out = {k: [] for k in ("t", "ia", "ib", "ic", "va", "vb", "vc")} if hires else None
    if inv.sw:
        if x0 is not None:  # 웜스타트: 홀드 값을 현재 상태로 초기화
            net = inv.network(0.0, x)
            inv.meas = (net[1], net[2], complex(x[IF_RE], x[IF_IM]))
            inv.th_hold = x[TH_C]
            inv.deriv(0.0, x)
            inv.v_pending = inv.v_applied = inv.aux["v_cmd"]
        eps = 0.25 * dt
    for k in range(n + 1):
        t = k * dt
        if inv.sw:
            if t >= inv.next_sample - eps:
                inv.sample(t, x)
                inv.next_sample += inv.Ts
            inv.pwm(t)
        if hires and hires[0] <= t <= hires[1]:
            v_p = inv.pcc_voltage(t, x)
            i_f = complex(x[IF_RE], x[IF_IM])
            hires_out["t"].append(t)
            for nm, z in (("i", i_f), ("v", v_p)):
                hires_out[nm + "a"].append(z.real)
                hires_out[nm + "b"].append((z * a120).real)
                hires_out[nm + "c"].append((z * A240).real)
        if k % record_every == 0:
            inv.deriv(t, x)
            a = inv.aux
            v_p, i_f = a["v_p"], a["i_f"]
            out["t"].append(t)
            out["P"].append(a["P"])
            out["Q"].append(a["Q"])
            out["V"].append(a["V"])
            out["I"].append(abs(i_f))
            out["freq"].append(a["w_c"] * p.f0)
            out["grid_freq"].append(sc.grid_f(t) * p.f0)
            d = (x[TH_C] - x[TH_G] - sc.grid_phase(t) + math.pi) % TWO_PI - math.pi
            out["delta_deg"].append(math.degrees(d))
            out["E"].append(a["E"])
            # 순시 상값 (진폭 불변: a상 = Re, b/c 는 회전)
            out["ia"].append(i_f.real)
            out["ib"].append((i_f * a120).real)
            out["ic"].append((i_f * A240).real)
            out["va"].append(v_p.real)
            out["vb"].append((v_p * a120).real)
            out["vc"].append((v_p * A240).real)
            out["sat"].append(1.0 if a["saturated"] else 0.0)
            out["id_ref_mag"].append(abs(a["i_ref"]))
        if k == n:
            break
        k1 = inv.deriv(t, x)
        x2 = [xi + 0.5 * dt * ki for xi, ki in zip(x, k1)]
        k2 = inv.deriv(t + 0.5 * dt, x2)
        x3 = [xi + 0.5 * dt * ki for xi, ki in zip(x, k2)]
        k3 = inv.deriv(t + 0.5 * dt, x3)
        x4 = [xi + dt * ki for xi, ki in zip(x, k3)]
        k4 = inv.deriv(t + dt, x4)
        x = [xi + dt / 6.0 * (a1 + 2 * a2 + 2 * a3 + a4)
             for xi, a1, a2, a3, a4 in zip(x, k1, k2, k3, k4)]
        if not sc.breaker_closed(t + dt):
            x[IS_RE] = x[IS_IM] = 0.0   # 차단기 개방: 계통 지로 전류만 0 (변압기 전류는 PCC 부하로 계속 흐름)
        inv.post_step(t + dt, x)
        # 발산 감지 (수치 폭주 방지)
        if abs(x[IF_RE]) > 50 or abs(x[VC_RE]) > 50:
            out["diverged_at"] = t
            break
    out["mode"] = mode
    out["scenario"] = sc.name
    out["x_final"] = x
    if hires_out is not None:
        out["hires"] = hires_out
    return out


def _band_peak(t, x, fmin=5.0, fmax=300.0):
    """fmin~fmax 대역 최대 진폭 [pu]과 주파수. 스위칭 에일리어싱(360 Hz 배수 ±6 Hz)은 제외."""
    import numpy as np
    x = np.asarray(x) - np.mean(x)
    dt = t[1] - t[0]
    F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) * 4.0 / len(x)   # 해닝 창 진폭 보정
    f = np.fft.rfftfreq(len(x), dt)
    m = (f >= fmin) & (f <= fmax) & (np.abs(((f + 180.0) % 360.0) - 180.0) > 6.0)
    if not m.any():
        return 0.0, 0.0
    i = np.argmax(np.where(m, F, 0.0))
    return float(F[i]), float(f[i])


def oscillation_check(t, P, a, b=None, osc_tol=0.005, swing_tol=0.01):
    """외란 후 [a, b] 구간을 반으로 나눠 진동이 작거나 감쇠 중인지 판정한다.

    - 5~300 Hz 대역(제어 상호작용) 최대 진폭: 뒤 구간 < osc_tol 이거나 앞 구간의 70 % 미만
    - 20 ms 이동평균(저주파 스윙) 표준편차: 뒤 구간 < swing_tol 이거나 앞 구간의 70 % 미만
    반환: (안정 여부, 설명 dict)
    """
    import numpy as np
    t, P = np.asarray(t), np.asarray(P)
    b = t[-1] if b is None else b
    mid = a + 0.5 * (b - a)
    m1, m2 = (t >= a) & (t < mid), (t >= mid) & (t <= b)
    o1, _ = _band_peak(t[m1], P[m1])
    o2, fo = _band_peak(t[m2], P[m2])
    k = max(1, int(round(0.02 / (t[1] - t[0]))))
    Pl = np.convolve(P, np.ones(k) / k, mode="same")
    s1, s2 = Pl[m1][k:-k].std() if m1.sum() > 2 * k else 0.0, Pl[m2][k:-k].std() if m2.sum() > 2 * k else 0.0
    osc_ok = o2 < osc_tol or o2 < 0.7 * o1
    swing_ok = s2 < swing_tol or s2 < 0.7 * s1
    return bool(osc_ok and swing_ok), dict(osc_amp=o2, osc_f=fo, swing_std=s2, osc_ok=osc_ok, swing_ok=swing_ok)


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")


def steady_state(mode: str, p: Params, t_init: float = 2.5, dt: float = DT_DEFAULT,
                 cache: bool = True) -> list[float]:
    """P_ref 를 램프로 올린 뒤 정상상태까지 돌린 상태벡터를 돌려준다.

    같은 (mode, 파라미터, dt) 조합은 .cache/ 에 저장해 재사용한다 (1 µs 계산 시간 절약).
    """
    key = hashlib.sha1(repr((mode, sorted(asdict(p).items()), t_init, dt, N_STATES)).encode()).hexdigest()[:16]
    path = os.path.join(CACHE_DIR, f"ss_{key}.pkl")
    if cache and os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    sc = Scenario(name="init", t_end=t_init, p_ref=ramp_p(p.P_ref, 0.3))
    r = simulate(mode, p, sc, dt=dt, record_dt=0.01)
    if "diverged_at" in r:
        raise RuntimeError(f"{mode} 초기화 발산 (SCR={p.scr}, P={p.P_ref})")
    if cache:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(r["x_final"], f)
    return r["x_final"]


__all__ = ["Params", "Scenario", "simulate", "steady_state", "ramp_p", "replace", "DT_DEFAULT", "oscillation_check"]
