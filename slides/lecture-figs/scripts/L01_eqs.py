"""1강 슬라이드용 수식 그림 (matplotlib mathtext). 슬라이드에 원래 크기(1:1)로 넣는다.
실행: python slides/lecture-figs/scripts/L01_eqs.py  (저장소 루트)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eq")
os.makedirs(OUT, exist_ok=True)
NAVY = "#013364"
plt.rcParams.update({"mathtext.fontset": "cm", "text.color": NAVY})

EQS = {
    # 3상 평형 상전압
    "E01-상전압": [
        r"$v_a = \hat{V}\cos(\omega t)$",
        r"$v_b = \hat{V}\cos(\omega t - 2\pi/3)$",
        r"$v_c = \hat{V}\cos(\omega t + 2\pi/3)$",
    ],
    # 선간전압과 실효값
    "E02-선간": [
        r"$v_{ab} = v_a - v_b = \sqrt{3}\,\hat{V}\cos(\omega t + 30\degree)$",
        r"$V_{rms} = \hat{V}/\sqrt{2}$",
    ],
    # 3상 순시전력
    "E03-순시전력": [
        r"$p(t) = v_a i_a + v_b i_b + v_c i_c = \frac{3}{2}\,\hat{V}\hat{I}\cos\varphi$",
    ],
    # 공간벡터 정의
    "E04-공간벡터": [
        r"$\vec{x} = \frac{2}{3}\left(x_a + a\,x_b + a^2 x_c\right),\quad a = e^{\,j2\pi/3}$",
    ],
    # 평형 3상의 공간벡터
    "E05-회전": [
        r"$\vec{v} = \hat{V} e^{\,j\omega t}$",
    ],
    # Clarke (성분 형태, mathtext는 행렬을 지원하지 않음)
    "E06-Clarke": [
        r"$x_\alpha = \frac{2}{3}\left(x_a - \frac{1}{2}x_b - \frac{1}{2}x_c\right)$",
        r"$x_\beta = \frac{1}{\sqrt{3}}\left(x_b - x_c\right)$",
        r"$x_0 = \frac{1}{3}\left(x_a + x_b + x_c\right)$",
    ],
    # 진폭 불변일 때 전력
    "E07-전력-SI": [
        r"$p = \frac{3}{2}\,\mathrm{Re}(\vec{v}\,\vec{i}^{\,*}),\quad q = \frac{3}{2}\,\mathrm{Im}(\vec{v}\,\vec{i}^{\,*})$",
    ],
    "E07-전력-pu": [
        r"$P = \mathrm{Re}(\vec{v}\,\vec{i}^{\,*}),\quad Q = \mathrm{Im}(\vec{v}\,\vec{i}^{\,*})\quad[\mathrm{pu}]$",
    ],
    # Park
    "E08-Park": [
        r"$x_{dq} = x_d + j\,x_q = \vec{x}\,e^{-j\theta}$",
    ],
    # 인덕터 식 유도
    "E09a-abc": [
        r"$\vec{v} = \frac{x_L}{\omega_b}\frac{d\vec{i}}{dt} + \vec{e}$",
    ],
    "E09b-치환": [
        r"$\vec{i} = i_{dq}\,e^{\,j\theta},\quad \frac{d\vec{i}}{dt} = \left(\frac{di_{dq}}{dt} + j\,\omega_b\,\omega\, i_{dq}\right)e^{\,j\theta}$",
    ],
    "E09c-dq": [
        r"$v_{dq} = \frac{x_L}{\omega_b}\frac{di_{dq}}{dt} + j\,\omega\,x_L\,i_{dq} + e_{dq}$",
    ],
    "E09d-성분": [
        r"$v_d = \frac{x_L}{\omega_b}\frac{di_d}{dt} - \omega x_L\, i_q + e_d$",
        r"$v_q = \frac{x_L}{\omega_b}\frac{di_q}{dt} + \omega x_L\, i_d + e_q$",
    ],
    # dq 전력
    "E10-dq전력": [
        r"$P = v_d i_d + v_q i_q$",
        r"$Q = v_q i_d - v_d i_q$",
    ],
    "E10-d정렬": [
        r"$v_q = 0 \;\Rightarrow\; P = v_d\, i_d,\quad Q = -v_d\, i_q$",
    ],
    # 예제 풀이
    "E11-예제": [
        r"$\vec{i} = e^{\,j(\omega t - 30\degree)}$",
        r"$i_{dq} = \vec{i}\,e^{-j\omega t} = e^{-j30\degree} = 0.866 - j\,0.5$",
    ],
}


def render(name, lines, fs=46, gap=2.5):
    fig = plt.figure(figsize=(1, 1), dpi=100)
    for k, s in enumerate(lines):
        fig.text(0, -k * gap * fs / 100, s, fontsize=fs, va="top", ha="left")
    path = os.path.join(OUT, f"{name}.png")
    fig.savefig(path, dpi=100, transparent=True, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return path


if __name__ == "__main__":
    from PIL import Image
    for n, ls in EQS.items():
        p = render(n, ls)
        print(n, Image.open(p).size)
