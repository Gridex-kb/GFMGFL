// T10 계통 전압 −5 % 스텝 (SCR 3, P0 0.5, 스위칭 2 µs): 무효전력과 PCC 전압 — ENTSO-E 30 ms 내 90 %
const F = Fig(1100, 730), C = FC, D = DATA, xl = [-10, 300];
const A = F.frame([120, 50, 760, 300], xl, [-0.08, 0.12]).axes({ xticks: [0, 50, 100, 150, 200, 250, 300], yticks: [-0.05, 0, 0.05, 0.1], tick: 22, xfmt: () => "", ylabel: "무효전력 $Q$ [pu]" });
A.vline(30, { color: C.green, width: 2.5, dash: "8 6" });
A.vline(100, { color: C.muted, width: 2, dash: "6 6" });
A.plot(D.GFL.t_ms, D.GFL.Q, { color: C.orange, width: 3 });
A.plot(D.GFM.t_ms, D.GFM.Q, { color: C.blue, width: 3.5 });
F.dot(A.x(D.GFM.t90_ms), A.y(D.GFM.Q90), { r: 9, color: C.navy });
F.dot(A.x(D.GFL.t90_ms), A.y(D.GFL.Q90), { r: 9, color: C.navy });
A.label(32, -0.07, "기준 30 ms", { anchor: "l", size: 20, color: C.green, weight: 700 });
A.label(102, -0.07, "100 ms 기준값", { anchor: "l", size: 20, color: C.muted });
F.label(895, A.y(0.1), `GFM: 90 % 도달<br>${D.GFM.t90_ms} ms (회로가<br>먼저 응답)`, { anchor: "l", size: 20, color: C.blue, weight: 700 });
F.label(895, A.y(-0.01), `GFL: ${D.GFL.t90_ms} ms<br>(Q 제어 루프가<br>따라감)`, { anchor: "l", size: 20, color: C.orange, weight: 700 });
const B = F.frame([120, 390, 760, 300], xl, [0.92, 1.04]).axes({ xticks: [0, 50, 100, 150, 200, 250, 300], yticks: [0.92, 0.96, 1.0, 1.04], tick: 22, xlabel: "스텝 후 시간 [ms]", ylabel: "PCC 전압 [pu]" });
B.plot(D.GFL.t_ms, D.GFL.V, { color: C.orange, width: 3 });
B.plot(D.GFM.t_ms, D.GFM.V, { color: C.blue, width: 3.5 });
F.label(895, B.y(1.01), "GFM: 즉시 무효<br>전류 → 전압<br>하락이 작다", { anchor: "l", size: 20, color: C.blue, weight: 700 });
F.label(895, B.y(0.945), "GFL: 먼저 떨어진<br>뒤 제어가 되돌림", { anchor: "l", size: 20, color: C.orange, weight: 700 });
F.done();
