// 평균값 EMT GFL, SCR 5 → 1.5, P* 0.8: FRT 진입 0.85(기본) vs 0.5 — PCC 전압(위), 측정 주파수(아래)
const F = Fig(1100, 730), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 250], [-50, 600], [0.2, 1.4]).axes({ xticks: [0, 100, 200, 300, 400, 500, 600], yticks: [0.4, 0.8, 1.2], tick: 22, xfmt: () => "", ylabel: "PCC 전압 |v| [pu]" });
A.hline(0.85, { color: C.muted, width: 2, dash: "6 6" }); A.hline(0.92, { color: C.muted, width: 2, dash: "6 6" });
A.plot(D.e085.t, D.e085.V, { color: C.orange, width: 3.5 });
A.plot(D.e050.t, D.e050.V, { color: C.teal, width: 4, dash: "12 8" });
A.vline(0);
F.label(895, A.y(1.25), `진입 0.85 pu (기본)<br>${D.e085.vmin}~${D.e085.vmax} pu 순환`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.85), `진입 0.5 pu<br>최저 ${D.e050.vmin_all} → 1.00 pu`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.label(895, A.y(0.45), "점선: 진입 0.85<br>해제 0.92", { anchor: "l", size: 20, color: C.muted });
const B = F.frame([120, 370, 760, 250], [-50, 600], [52, 68]).axes({ xticks: [0, 100, 200, 300, 400, 500, 600], yticks: [54, 60, 66], tick: 22, xlabel: "SCR 5 → 1.5 전환 후 시간 [ms]", ylabel: "PLL 측정 주파수 [Hz]" });
B.hline(54, { color: C.red, width: 2, dash: "6 6" }); B.hline(66, { color: C.red, width: 2, dash: "6 6" });
B.plot(D.e085.t, D.e085.f, { color: C.orange, width: 3.5 });
B.plot(D.e050.t, D.e050.f, { color: C.teal, width: 4, dash: "12 8" });
B.vline(0);
F.label(895, B.y(63), `${D.e085.fmin}~${D.e085.fmax} Hz<br>제한 사이를 오간다`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, B.y(57), "진입 0.5: 60 Hz 유지", { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.done();
