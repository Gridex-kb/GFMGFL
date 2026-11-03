# 강의 실습 파일

슬라이드 강의(`slides/decks/`)와 교재(`docs/09-강좌-3상컨버터에서-GFM까지/`)에 맞춘 Python 실습이다. 모든 값은 pu이다.

| 강의 | 파일 | 내용 |
|---|---|---|
| 1강 3상 표현·공간벡터·dq | `lec01_space_vector_dq.py` | 3상 순시전력, Clarke = 공간벡터, 예제 id·iq·P·Q, dq로 본 전압 변화, 5고조파 → 360 Hz |
| 2강 2레벨 VSC | `lec02_two_level_vsc.py` | 상태 8개 표, 반송파 PWM 상태 순서, 6스텝 기본파 1.436 pu, 평균 벡터·1.303 pu |
| 3강 필터·변압기·측정점 | `lec03_filter_measurement.py` | LCL 공진과 SCR, 보드 선도·5 kHz 감쇠, 리플 상한, (EMT) 실측 리플·측정점별 잡음 |
| 4강 디지털 제어와 지연 | `lec04_digital_delay.py` | 1.5 Ts 지연 vs 1차 근사, 영차 홀드, 위상 예산, (EMT) 연속 θ 버그 61.35 → 60.00 Hz |
| 5강 전류 제어 | `lec05_current_control.py` | Kp·Ki 공식, 교차 815 Hz·위상여유 34.9°, 계단 응답(지연·디커플링), anti-windup, (EMT) 피드포워드 σ(P) 0.004/0.117/0.004 |
| 6강 GFL: PLL로 따라가기 | `lec06_gfl_pll.py` | PLL 이득, −20° 점프 직후 주파수·54 Hz 제한, P/Q → 전류 지령, FRT 여유·ΔV, (EMT) 위상 점프 PLL 10/20/50 Hz·FRT 모드 순환 |
| 7강 GFM: 위상을 만들기 | `lec07_gfm_vsm.py` | P–δ·동기화 토크·페이저 0.48, 스윙 모드 1.34 Hz·ζ 0.37, 드룹 등가, 가상 인덕턴스 16 ms, (EMT) 위상 점프 GFM +0.64 / GFL +0.007, 주파수 계단 H 1/4/8 |
| 8강 약계통과 제어 상호작용 | `lec08_weak_grid.py` | Zg = 1/SCR, PLL 유효 이득 cos δ, 음저항 −V²/P, GFM ζ vs SCR, (EMT) 선로 트립 판정 GFL 10/20/50 Hz·GFM (90 Hz 상호작용형, 10 Hz 동기화 상실형) |
| 9강 전류 제한과 고장 | `lec09_current_limit.py` | 고장 시 가상 임피던스 전류 2.8 pu, 원형 포화·전력 상한 |v|·Imax, 평형점 조건 E·Vg/X, 2.0 pu 전압 여유 0.75, (EMT) 보정 유무 회복 457/659 ms·GFL 108 ms, PCC 지락 전류 정격 1.2/2.0 → 2.0 pu 199/197 ms |

## 실행

저장소 루트에서 실행한다 (필요: Python 3.10+, numpy, matplotlib).

```bash
python practice/lec01_space_vector_dq.py             # 계산 실습
python practice/lec01_space_vector_dq.py --plot      # 그림을 practice/out/ 에 PNG로 저장
python practice/lec03_filter_measurement.py --emt    # EMT 시뮬레이션 실습 포함 (수 초~수십 초)
python practice/lec04_digital_delay.py --answers     # '해보기' 문제의 답까지 출력
```

- 각 실습은 결과를 출력하고, 교재·슬라이드의 기대값과 비교해 `[OK]`/`[확인 필요]`를 표시한다.
- `해보기` 문제는 코드 안의 `바꿔 보기` 주석을 따라 값을 바꿔 보면서 푼다. `--answers`로 답을 확인한다.
- EMT 실습은 `simulation/emt/gfm_gfl_emt.py` 모델을 그대로 쓴다. 처음 실행할 때는 정상상태 초기화가 포함되어 조금 더 걸린다.
