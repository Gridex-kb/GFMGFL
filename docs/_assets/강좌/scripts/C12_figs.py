"""C12 표준 시험으로 비교 — 그림 생성 (저장소 루트에서 실행: python docs/_assets/강좌/scripts/C12_figs.py)

시뮬레이션 결과가 아니라 규격의 시간 기준을 한 축에 모은 개념 그림이다.
"""
import logging
import os

import matplotlib
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "_assets", "강좌")
SURF, INK, INK2, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, VIOLET, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#898781"
plt.rcParams.update({
    "font.family": ["WenQuanYi Zen Hei", "DejaVu Sans"], "axes.unicode_minus": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "font.size": 9, "legend.frameon": False, "legend.fontsize": 8.5,
})

# (라벨, 시간 [ms], 종류)  종류: "within" 이내 도달, "hold" 이상 유지, "own" 본 보고서 기준
ITEMS = [
    ("GB GC0137 — 위상 점프 자연 응답", 5, "within"),
    ("ENTSO-E TG GFC — 위상 점프 유효전류 (≥ 정격 25 %)", 10, "within"),
    ("ERCOT AGS #7 — 초기 유효전력 변화 90 % 도달", 15, "within"),
    ("ENTSO-E TG GFC — 전압 스텝 무효전류 90 % 도달", 30, "within"),
    ("ENTSO-E TG GFC — 전압 스텝 정착", 60, "within"),
    ("한전 연계기준안(초안) — 고장전류 ≥ 2.0 pu 유지", 140, "hold"),
    ("고장 후 유효전력 회복 (본 보고서 기준)", 1000, "own"),
]
STY = {"within": (BLUE, "이 시간 이내에 응답"), "hold": (AQUA, "이 시간 이상 유지"), "own": (VIOLET, "규격이 정성적 → 보고서가 정한 수치")}


def main():
    fig, ax = plt.subplots(figsize=(7.8, 4.3))
    ys = list(range(len(ITEMS)))[::-1]
    seen = set()
    for y, (lab, ms, kind) in zip(ys, ITEMS):
        c, leg = STY[kind]
        ax.barh(y, ms, left=0.1, height=0.55, color=c, label=None if kind in seen else leg)
        seen.add(kind)
        ax.text(ms * 1.12, y, f"{ms:g} ms", va="center", fontsize=8, color=INK2)
    ax.set_yticks(ys, [it[0] for it in ITEMS])
    ax.set_xscale("log")
    ax.set_xlim(0.1, 6000)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    for x, lab in ((0.15, "제어 지연\n약 1.5 샘플"), (16.7, "기본파\n1주기"), (150, "시험 고장\n150 ms")):
        ax.axvline(x, color=GREY, lw=0.8, ls=":")
        ax.text(x * 1.08, len(ITEMS) + 0.55, lab, fontsize=7.5, color=INK2, va="top")
    ax.set_xlabel("외란 후 시간 [ms] (로그 축)")
    ax.set_title("시험 판정의 시간 기준")
    ax.set_ylim(-0.6, len(ITEMS) + 0.65)
    ax.legend(loc="upper center", bbox_to_anchor=(0.35, -0.2), ncol=3)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "C12-판정-시간기준.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
    print("saved to", OUT)
