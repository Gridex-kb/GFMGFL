// 강계통 SRF-PLL, −20° 위상 점프: 위상 오차(위)와 측정 주파수(아래), 10/20/50 Hz
const F = Fig(1100, 730), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 250], [0, 100], [-22, 6]).axes({ xticks: [0, 20, 40, 60, 80, 100], yticks: [-20, -10, 0], tick: 22, xfmt: () => "", ylabel: "위상 오차 $\\theta_g - \\theta_c$ [°]" });
A.plot(D["10"].t, D["10"].e, { color: C.teal, width: 3.5, dash: "12 8" });
A.plot(D["20"].t, D["20"].e, { color: C.orange, width: 4.5 });
A.plot(D["50"].t, D["50"].e, { color: C.blue, width: 3.5 });
F.label(895, A.y(-3), `50 Hz: ${D["50"].settle_ms} ms`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(-9), `20 Hz: ${D["20"].settle_ms} ms`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(-15), `10 Hz: ${D["10"].settle_ms} ms`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.label(895, A.y(-20), "(|오차| < 1° 정착)", { anchor: "l", size: 20, color: C.muted });
const B = F.frame([120, 370, 760, 250], [0, 100], [53, 61.5]).axes({ xticks: [0, 20, 40, 60, 80, 100], yticks: [54, 56, 58, 60], tick: 22, xlabel: "위상 점프 후 시간 [ms]", ylabel: "PLL 측정 주파수 [Hz]" });
B.hline(54, { color: C.red, width: 2.5, dash: "6 6" });
B.plot(D["10"].t, D["10"].f, { color: C.teal, width: 3.5, dash: "12 8" });
B.plot(D["20"].t, D["20"].f, { color: C.orange, width: 4.5 });
B.plot(D["50"].t, D["50"].f, { color: C.blue, width: 3.5 });
F.label(895, B.y(54), "제한 54 Hz (−10 %)", { anchor: "l", size: 22, color: C.red, weight: 700 });
F.label(895, B.y(57.5), `10 Hz: 최저 ${D["10"].fmin} Hz<br>제한에 안 닿음`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.label(895, B.y(60.3), "20·50 Hz:<br>제한에 붙음", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.done();
