// 내접원 반지름 = 꼭짓점 거리 × cos 30° = V_dc/√3
const F = Fig(640, 560), C = FC, P = F.plane(250, 280, 140);
hexagon(F, P, { circle: true, labels: false, arrows: false, zero: false });
const v1 = P.pol(R6, 0), v2 = P.pol(R6, 60), mid = P.pol(RIN, 30);
F.poly([P.xy([0, 0]), P.xy(v1), P.xy(v2)], { closed: true, fill: "rgba(235,104,52,0.10)", color: "none" });
P.vec(v1, { color: C.navy, width: 5 });
F.line(...P.xy([0, 0]), ...P.xy(mid), { color: C.teal, width: 5 });
F.line(...P.xy(v1), ...P.xy(v2), { color: C.orange, width: 5 });
// 직각 표시
const u = [Math.cos(Math.PI / 6), Math.sin(Math.PI / 6)], t = [-Math.sin(Math.PI / 6), Math.cos(Math.PI / 6)], q = 0.09;
const p1 = [mid[0] - u[0] * q, mid[1] - u[1] * q], p2 = [p1[0] + t[0] * q, p1[1] + t[1] * q], p3 = [mid[0] + t[0] * q, mid[1] + t[1] * q];
F.poly([P.xy(p1), P.xy(p2), P.xy(p3)], { color: C.teal, width: 2.5 });
P.arc(0.42, 0, 30, { color: C.slate, width: 2.5 });
P.label(P.pol(0.56, 13), "$30^\\circ$", { size: 24 });
P.label([-1.18, -0.45], "$R = \\tfrac{2}{3}V_{dc} = 1.504$", { anchor: "l", size: 24, color: C.navy, weight: 700 });
P.label(P.pol(RIN * 0.55, 30), "$r$", { anchor: "br", size: 30, color: C.teal, weight: 700 });
F.label(320, 548, "$r = R\\cos 30^\\circ = \\tfrac{V_{dc}}{\\sqrt3} = 1.303$", { anchor: "b", size: 26, color: C.teal, weight: 700 });
F.done();
