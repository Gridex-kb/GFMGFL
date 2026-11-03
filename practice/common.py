"""강의 실습 공통 도우미.

- 저장소 루트를 기준으로 경로를 잡아, 어느 폴더에서 실행해도 EMT 모델(`simulation/emt`)을 불러올 수 있게 한다.
- 그림은 `practice/out/`에 PNG로 저장한다 (화면이 없는 환경에서도 동작).
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMT_DIR = os.path.join(ROOT, "simulation", "emt")
OUT_DIR = os.path.join(ROOT, "practice", "out")
if EMT_DIR not in sys.path:
    sys.path.insert(0, EMT_DIR)

# Windows 콘솔(cp949)에서도 −, ω 같은 문자가 깨지지 않게 출력을 UTF-8로 맞춘다
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass

# 강좌 색 (슬라이드와 같음)
NAVY, BLUE, ORANGE, GREEN, SLATE, MUTED = "#013364", "#2463c8", "#eb6834", "#3aa150", "#45546b", "#7d8ca2"
PHASE = {"a": BLUE, "b": ORANGE, "c": GREEN}


def header(title: str) -> None:
    """실습 구분용 머리글."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def check(name: str, value: float, expected: float, tol: float) -> bool:
    """값이 기대치와 맞는지 확인하고 결과를 한 줄로 출력한다."""
    ok = abs(value - expected) <= tol
    print(f"  [{'OK' if ok else '확인 필요'}] {name}: {value:.4g} (기대 {expected:.4g} ± {tol:g})")
    return ok


def plt_ready():
    """matplotlib를 화면 없이 쓰도록 설정하고 pyplot을 돌려준다."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import logging
    from matplotlib import font_manager
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    have = {f.name for f in font_manager.fontManager.ttflist}
    kor = [n for n in ("Pretendard", "Apple SD Gothic Neo", "Malgun Gothic", "NanumGothic", "Noto Sans CJK KR",
                       "WenQuanYi Zen Hei") if n in have]
    plt.rcParams.update({
        "font.family": kor[:1] + ["DejaVu Sans"],
        "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "lines.linewidth": 1.8, "font.size": 11,
    })
    return plt


def savefig(fig, name: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    print(f"  그림 저장: {os.path.relpath(path, ROOT)}")
    return path


def parse(description: str, emt: bool = False) -> argparse.Namespace:
    """공통 실행 옵션: --plot(그림 저장), --emt(EMT 시뮬레이션 실습 포함), --answers(해보기 답 보기)."""
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--plot", action="store_true", help="그림을 practice/out/ 에 PNG로 저장")
    ap.add_argument("--answers", action="store_true", help="'해보기' 문제의 답을 함께 출력")
    if emt:
        ap.add_argument("--emt", action="store_true", help="EMT 시뮬레이션 실습도 실행 (수 초~수십 초)")
    return ap.parse_args()
