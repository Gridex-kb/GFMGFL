// 한 스위칭 주기 안에서 V1, V2, 영벡터를 시간 비율로 섞으면 섹터 안의 평균 벡터가 된다
const F = Fig(700, 560), C = FC, P = F.plane(110, 450, 270);
const v1 = P.pol(R6, 0), v2 = P.pol(R6, 60), tgt = P.pol(1.0, 20);
const d2 = tgt[1] / v2[1], d1 = (tgt[0] - d2 * v2[0]) / v1[0];
P.axis(0, 1.75, "$\\alpha$", { color: C.axis, size: 28, width: 2 });
F.poly([P.xy([0, 0]), P.xy(v1), P.xy(v2)], { closed: true, fill: "rgba(36,99,200,0.06)", color: C.navy, width: 2.5 });
P.arc(RIN, -2, 64, { color: C.teal, width: 2.5, dash: "8 7" });
P.vec(v1, { color: C.navy, width: 4 }); P.vec(v2, { color: C.navy, width: 4 });
P.label(P.pol(R6 + 0.12, 0), "$\\vec V_1$", { anchor: "l", size: 30, color: C.navy });
P.label([R6 * 0.5 - 0.07, R6 * 0.866], "$\\vec V_2$", { anchor: "r", size: 30, color: C.navy });
const a1 = [d1 * v1[0], d1 * v1[1]], a2 = [d2 * v2[0], d2 * v2[1]];
P.vec(a1, { color: C.blue, width: 6 });
P.vec(a2, { color: C.orange, width: 6 }, a1);
P.vec(tgt, { color: C.navy, width: 7, head: 26 });
P.label([a1[0] * 0.5, -0.09], "$\\tfrac{t_1}{T_s}\\vec V_1$", { anchor: "t", size: 28, color: C.blue, weight: 700 });
P.label([a1[0] + a2[0] * 0.5 + 0.06, a2[1] * 0.5], "$\\tfrac{t_2}{T_s}\\vec V_2$", { anchor: "l", size: 28, color: C.orange, weight: 700 });
P.label(P.pol(0.62, 32), "$\\bar{\\vec v}$", { size: 34, color: C.navy, weight: 700 });
F.label(690, 16, `예: $|\\bar{\\vec v}| = 1.0\\,\\angle 20^\\circ$ → $t_1/T_s = ${d1.toFixed(2)}$, $t_2/T_s = ${d2.toFixed(2)}$, 영벡터 $${(1 - d1 - d2).toFixed(2)}$`, { anchor: "tr", size: 22, color: C.slate });
F.done();
