// 전력–위상차 곡선 P = (EV/X) sin δ, X = Xv + 1/SCR = 0.633 (SCR 3). 운전점 δ0 = 18.5°, −20° 점프 → δ 38.5°, ΔP ≈ 0.48 (측정 없이)
const F = Fig(1100, 620), C = FC;
const d0 = PR.d0 * 180 / Math.PI, d1 = d0 + 20, P1 = Pdelta(d1), Pmax = 1 / PR.X;
const A = F.frame([120, 60, 760, 460], [0, 180], [0, 1.85]).axes({ xticks: [0, 30, 60, 90, 120, 150, 180], yticks: [0, 0.5, 1.0, 1.5], tick: 22, xlabel: "δ = θ − θ<b>g</b> [°]", ylabel: "$P$ [pu]" });
A.fn((d) => Pdelta(d), 400, { color: C.navy, width: 5 });
A.hline(0.5, { color: C.muted, width: 2, dash: "6 6" });
A.hline(Pmax, { color: C.muted, width: 2, dash: "6 6" });
A.label(176, Pmax + 0.06, "$P_{max} = EV/X \\approx 1.58$", { anchor: "br", size: 22, color: C.muted });
// 운전점 → 점프
F.dot(A.x(d0), A.y(0.5), { r: 11, color: C.blue });
F.dot(A.x(d1), A.y(P1), { r: 11, color: C.orange });
A.arrow(d0 + 1.5, 0.5, d1 - 1.5, 0.5, { color: C.slate, width: 3, head: 14 });
A.arrow(d1, 0.52, d1, P1 - 0.03, { color: C.orange, width: 4, head: 16 });
A.label(d0 + 1, 0.36, `운전점 $\\delta_0$ = ${d0.toFixed(1)}°`, { anchor: "tl", size: 22, color: C.blue, weight: 700 });
A.label(d0 + 1, 0.47, "계통 −20° → δ +20°", { anchor: "tl", size: 22, color: C.slate });
A.label(d1 + 3, (0.5 + P1) / 2, `ΔP ≈ ${(P1 - 0.5).toFixed(2)} pu<br>측정 없이 즉시`, { anchor: "l", size: 24, color: C.orange, weight: 700 });
// 동기화 토크 = 기울기
const dd = 12;
A.plot([d0 - dd, d0 + dd], [0.5 - PR.Ks * dd * Math.PI / 180, 0.5 + PR.Ks * dd * Math.PI / 180], { color: C.teal, width: 3, dash: "8 6" });
A.label(d0 - 4, 0.16, `기울기 = 동기화 토크 $K_s$ ≈ ${PR.Ks.toFixed(2)} pu/rad`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
A.label(120, 1.0, "$P = \\dfrac{EV}{X}\\sin\\delta$", { size: 30, color: C.navy, weight: 700 });
A.label(120, 0.78, "E = V = 1, X = 0.3 + 1/3 = 0.633", { size: 22, color: C.slate });
F.done();
