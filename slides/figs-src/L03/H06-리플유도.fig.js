// 하프브리지 리플: 극전압 펄스(듀티 D)와 인덕터 전류 삼각파, 듀티 0.5에서 최대
const F = Fig(900, 500), C = FC, Dd = 0.5;
const A1 = F.frame([110, 40, 700, 160], [0, 2], [-1.4, 1.4]).axes({ xticks: [0, 0.5, 1, 1.5, 2], yticks: [-1.128, 1.128], tick: 22, xfmt: () => "", yfmt: (v) => (v > 0 ? "+" : "−") + "1.128" });
const sq = [], sqx = [];
for (let k = 0; k < 2; k++) { sqx.push(k, k, k + Dd, k + Dd, k + 1); sq.push(-1.128, 1.128, 1.128, -1.128, -1.128); }
A1.plot(sqx, sq, { color: C.navy, width: 4 });
const A2 = F.frame([110, 270, 700, 170], [0, 2], [-0.7, 0.7]).axes({ xticks: [0, 0.5, 1, 1.5, 2], yticks: [], tick: 22, xfmt: (v) => (v === 0 ? "0" : v === 1 ? "$T_s$" : v === 2 ? "$2T_s$" : ""), zero: false });
const ix = [0, 0.5, 1, 1.5, 2], iy = [-0.5, 0.5, -0.5, 0.5, -0.5];
A2.plot(ix, iy, { color: C.orange, width: 5 });
A2.hline(0, { color: C.axis, dash: "6 6" });
A2.arrow(0.62, -0.5, 0.62, 0.5, { color: C.slate, width: 2.5, head: 12, both: true });
A2.label(0.66, 0, "$\\Delta i_{pp}$", { anchor: "l", size: 28, color: C.slate });
A1.label(0.25, 1.25, "$DT_s$", { anchor: "b", size: 24, color: C.navy });
F.label(820, 120, "극전압<br>$v_{x0}$", { anchor: "l", size: 24, color: C.navy });
F.label(820, 355, "인덕터<br>전류", { anchor: "l", size: 24, color: C.orange });
A2.label(0.25, 0.55, "기울기 $\\tfrac{V_{dc}/2 - v}{L}$", { anchor: "b", size: 22, color: C.orange });
F.done();
