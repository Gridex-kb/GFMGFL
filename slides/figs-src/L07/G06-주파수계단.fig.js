// 계통 주파수 −0.2 Hz 계단에 대한 GFM 유효전력: H = 1 / 4 / 8 s. 정상상태 ΔP = D·Δf/f0 = 0.167 (드룹 2 %), 관성이 오버슈트·스윙 주파수를 정한다
const F = Fig(1100, 600), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 440], [-100, 1900], [0.4, 0.95]).axes({ xticks: [0, 500, 1000, 1500], yticks: [0.5, 0.6, 0.7, 0.8, 0.9], tick: 22, xlabel: "주파수 계단 (−0.2 Hz) 후 시간 [ms]", ylabel: "유효전력 $P$ [pu]" });
A.hline(0.5 + D.droop, { color: C.red, width: 2.5, dash: "6 6" });
A.plot(D.H1.t, D.H1.P, { color: C.teal, width: 3.5, dash: "10 8" });
A.plot(D.H8.t, D.H8.P, { color: C.orange, width: 3.5 });
A.plot(D.H4.t, D.H4.P, { color: C.blue, width: 4.5 });
A.vline(0);
F.label(895, A.y(0.5 + D.droop), `드룹 예측<br>0.5 + ${D.droop.toFixed(3)}`, { anchor: "l", size: 22, color: C.red, weight: 700 });
F.label(895, A.y(0.88), `H = 1 s<br>최대 +${D.H1.dP_max.toFixed(2)}`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.label(895, A.y(0.79), `H = 4 s (모델)<br>최대 +${D.H4.dP_max.toFixed(2)}`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(0.57), `H = 8 s<br>최대 +${D.H8.dP_max.toFixed(2)}`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.47), "정상상태는 같은 곳으로<br>(드룹 D = 50)", { anchor: "l", size: 20, color: C.slate });
F.done();
