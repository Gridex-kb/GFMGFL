// 스위칭 상태 8개의 αβ 벡터: 유효 벡터 6개가 육각형 꼭짓점(1.504 pu), 영벡터 2개는 원점
const F = Fig(700, 640), C = FC, P = F.plane(350, 320, 165);
hexagon(F, P, { circle: true });
P.label(P.pol(1.78, 213), "$\\hat V_{\\max} = 1.303$", { anchor: "c", size: 24, color: C.teal, weight: 700 });
P.label(P.pol(R6 * 0.55, -30), "$1.504$", { anchor: "c", size: 22, color: C.navy, bg: "#ffffff" });
F.done();
