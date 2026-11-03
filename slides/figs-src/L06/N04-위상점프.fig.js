// 평균값 EMT GFL, SCR 3, P* 0.5, PLL 20 Hz, −20° 위상 점프: P·Q(위), 측정 주파수(아래)
const F = Fig(1100, 730), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 250], [-30, 250], [-0.2, 0.8]).axes({ xticks: [0, 50, 100, 150, 200, 250], yticks: [0, 0.25, 0.5, 0.75], tick: 22, xfmt: () => "", ylabel: "전력 [pu]" });
A.plot(D.t, D.Q, { color: C.teal, width: 3.5, dash: "12 8" });
A.plot(D.t, D.P, { color: C.orange, width: 4.5 });
A.vline(0);
F.label(895, A.y(0.55), `P: 10 ms 내 ΔP<br>${D.dP10 >= 0 ? "+" : ""}${D.dP10.toFixed(3)} pu`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.08), "Q (전압 제어)", { anchor: "l", size: 22, color: C.teal, weight: 700 });
const B = F.frame([120, 370, 760, 250], [-30, 250], [53, 62]).axes({ xticks: [0, 50, 100, 150, 200, 250], yticks: [54, 56, 58, 60], tick: 22, xlabel: "위상 점프 (−20°) 후 시간 [ms]", ylabel: "PLL 측정 주파수 [Hz]" });
B.hline(54, { color: C.red, width: 2.5, dash: "6 6" });
B.plot(D.t, D.f, { color: C.orange, width: 4.5 });
B.vline(0);
F.label(895, B.y(54.6), `54 Hz 한계에<br>약 ${D.t54_ms.toFixed(0)} ms 체류`, { anchor: "l", size: 22, color: C.red, weight: 700 });
F.label(895, B.y(59.3), "계통 주파수는<br>60 Hz 그대로", { anchor: "l", size: 22, color: C.slate });
F.done();
