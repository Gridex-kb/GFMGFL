// EMT(GFM, SCR 10, 2 µs): a상 Lf 전류와 변압기 전류. 위: 한 주기, 아래: 1 ms 확대
const F = Fig(1100, 620), C = FC, D = DATA;
const A1 = F.frame([110, 40, 820, 200], [0, 16.67], [-1.0, 1.0]).axes({ xticks: [0, 4, 8, 12, 16], yticks: [-1, 0, 1], tick: 22, ylabel: "" });
A1.plot(D.cyc.t, D.cyc.if, { color: C.orange, width: 1.6 }); A1.plot(D.cyc.t, D.cyc.it, { color: C.blue, width: 4 });
const z = D.zoom, ylo = Math.min(...z.if) - 0.03, yhi = Math.max(...z.if) + 0.03;
const A2 = F.frame([110, 330, 820, 200], [0, 1], [ylo, yhi]).axes({ xticks: [0, 0.2, 0.4, 0.6, 0.8, 1.0], yticks: [+(ylo + 0.05).toFixed(2), +(yhi - 0.05).toFixed(2)], tick: 22, xlabel: "시간 [ms]" });
A2.plot(z.t, z.if, { color: C.orange, width: 3 }); A2.plot(z.t, z.it, { color: C.blue, width: 4.5 });
F.label(120, 26, "한 주기 (16.7 ms) · a상 전류 [pu]", { anchor: "l", size: 22, color: C.slate });
F.label(120, 316, "1 ms 확대 — 반송파 5주기", { anchor: "l", size: 22, color: C.slate });
F.label(950, 110, "$L_f$ 전류", { anchor: "l", size: 24, color: C.orange, weight: 700 });
F.label(950, 150, "변압기 전류", { anchor: "l", size: 24, color: C.blue, weight: 700 });
F.label(950, 400, `리플<br>${D.ripple_pp.toFixed(2)} p-p`, { anchor: "l", size: 24, color: C.orange, weight: 700 });
F.done();
