// EMT(GFM, SCR 3): Lf 전류 리플과 반송파 꼭짓점 샘플 — 샘플이 리플의 가운데를 잡는다
const F = Fig(1100, 560), C = FC, D = DATA;
const lo = Math.min(...D.i) - 0.01, hi = Math.max(...D.i) + 0.01;
const A = F.frame([120, 70, 860, 380], [0, 600], [lo, hi]).axes({ xticks: [0, 100, 200, 300, 400, 500, 600], yticks: [+(lo + 0.02).toFixed(2), +(hi - 0.02).toFixed(2)], tick: 22, xlabel: "시간 [µs]", ylabel: "a상 $L_f$ 전류 [pu]" });
D.ts.forEach((t) => A.vline(t, { color: C.axis, width: 2, dash: "4 6" }));
A.plot(D.t, D.i, { color: C.orange, width: 3.5 });
const avg = []; for (let k = 0; k + 1 < D.ts.length; k++) avg.push([D.ts[k], D.is[k]]);
A.plot(D.ts, D.is, { color: C.blue, width: 3, dash: "10 8" });
D.ts.forEach((t, k) => F.dot(A.x(t), A.y(D.is[k]), { r: 10, color: C.blue }));
F.label(995, A.y(D.is[D.is.length - 1]), "샘플<br>(10 kHz)", { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(995, 140, "$L_f$ 전류<br>(2 µs)", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.done();
