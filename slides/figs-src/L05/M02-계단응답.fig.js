// 독립 전류루프 0.1 pu id 계단: 위 id(지연 없음 / 지연+디커플링 / 디커플링 없음), 아래 iq 흔들림
const F = Fig(1100, 690), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 250], [-0.5, 6], [0, 0.17]).axes({ xticks: [0, 1, 2, 3, 4, 5, 6], yticks: [0, 0.05, 0.1, 0.15], tick: 22, xfmt: () => "", ylabel: "$i_d$ [pu]" });
A.plot([-0.5, 0, 0, 6], [0, 0, 0.1, 0.1], { color: C.muted, width: 2.5, dash: "10 8" });
A.plot(D.t, D.nodelay_d, { color: C.teal, width: 3.5 });
A.plot(D.t, D.nodec_d, { color: C.orange, width: 3.5 });
A.plot(D.t, D.base_d, { color: C.blue, width: 4.5 });
F.label(895, A.y(0.15), `지연 1.5 Ts + 디커플링<br>오버슈트 ${D.os_delay.toFixed(0)} %`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(0.085), "디커플링 없음", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.035), `지연 없음<br>오버슈트 ${D.os_nodelay.toFixed(0)} %`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
const B = F.frame([120, 370, 760, 200], [-0.5, 6], [-0.016, 0.004]).axes({ xticks: [0, 1, 2, 3, 4, 5, 6], yticks: [-0.015, -0.01, -0.005, 0], tick: 22, xlabel: "계단 이후 시간 [ms]", ylabel: "$i_q$ [pu]" });
B.plot(D.t, D.nodelay_q, { color: C.teal, width: 3.5 });
B.plot(D.t, D.nodec_q, { color: C.orange, width: 3.5 });
B.plot(D.t, D.base_q, { color: C.blue, width: 4.5 });
F.label(895, B.y(-0.012), `디커플링 없음<br>최대 ${Math.min(...D.nodec_q).toFixed(3)} pu`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, B.y(-0.004), `디커플링 있음<br>최대 ${Math.min(...D.base_q).toFixed(3)} pu`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.done();
