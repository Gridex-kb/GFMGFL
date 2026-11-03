// 평균값 EMT, SCR 3, P* 0.5, −20° 위상 점프: GFM(VSM) vs GFL(PLL 20 Hz). 위 P, 아래 내부 주파수(VSM ω / PLL 측정)
const F = Fig(1100, 730), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 250], [-50, 800], [0.2, 1.25]).axes({ xticks: [0, 200, 400, 600, 800], yticks: [0.25, 0.5, 0.75, 1.0], tick: 22, xfmt: () => "", ylabel: "유효전력 $P$ [pu]" });
F.rect(A.x(0), 60, A.x(10) - A.x(0), 250, { fill: "#fde3d6", opacity: 0.8 });
A.plot(D.GFL.t, D.GFL.P, { color: C.orange, width: 3.5, dash: "12 8" });
A.plot(D.GFM.t, D.GFM.P, { color: C.blue, width: 4 });
A.vline(0);
F.label(895, A.y(1.08), `GFM (VSM)<br>10 ms 내 +${D.GFM.dP10.toFixed(2)} pu`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(0.72), `10~30 ms 평균<br>+${D.GFM.dP10_30.toFixed(2)} (페이저 ${D.phasor.dP.toFixed(2)})`, { anchor: "l", size: 20, color: C.slate });
F.label(895, A.y(0.42), `GFL (PLL 20 Hz)<br>+${D.GFL.dP10.toFixed(3)} pu`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(A.x(14), 72, "← 처음 10 ms", { anchor: "tl", size: 20, color: C.orange });
const B = F.frame([120, 370, 760, 250], [-50, 800], [53, 61]).axes({ xticks: [0, 200, 400, 600, 800], yticks: [54, 56, 58, 60], tick: 22, xlabel: "위상 점프 (−20°) 후 시간 [ms]", ylabel: "제어기 내부 주파수 [Hz]" });
B.hline(54, { color: C.red, width: 2, dash: "6 6" });
B.plot(D.GFL.t, D.GFL.f, { color: C.orange, width: 3.5, dash: "12 8" });
B.plot(D.GFM.t, D.GFM.f, { color: C.blue, width: 4 });
B.vline(0);
F.label(895, B.y(59.3), `GFM: VSM ω<br>최저 ${D.GFM.fmin.toFixed(1)} Hz (관성)`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, B.y(55.2), "GFL: PLL 측정<br>54 Hz 한계", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.done();
