// 선로 트립 SCR 5 → 1.5 (P* 0.8, FRT 진입 0.5): GFM / GFL 20 Hz / GFL 50 Hz — 위 P, 아래 내부 주파수
const F = Fig(1100, 730), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 250], [-50, 600], [0.2, 1.05]).axes({ xticks: [0, 100, 200, 300, 400, 500, 600], yticks: [0.25, 0.5, 0.75, 1.0], tick: 22, xfmt: () => "", ylabel: "유효전력 $P$ [pu]" });
A.plot(D.GFL50.t, D.GFL50.P, { color: C.teal, width: 3 });
A.plot(D.GFL20.t, D.GFL20.P, { color: C.orange, width: 3.5, dash: "12 8" });
A.plot(D.GFM.t, D.GFM.P, { color: C.blue, width: 4 });
A.vline(0);
F.label(895, A.y(0.95), "GFL 50 Hz<br>약 90 Hz 지속 진동", { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.label(895, A.y(0.66), "GFL 20 Hz<br>짧은 과도 후 안정", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.38), `GFM (VSM)<br>최저 ${D.GFM.Pmin.toFixed(2)} → 회복`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
const B = F.frame([120, 370, 760, 250], [-50, 600], [52, 68]).axes({ xticks: [0, 100, 200, 300, 400, 500, 600], yticks: [54, 60, 66], tick: 22, xlabel: "SCR 5 → 1.5 전환 후 시간 [ms]", ylabel: "제어기 내부 주파수 [Hz]" });
B.hline(54, { color: C.red, width: 2, dash: "6 6" }); B.hline(66, { color: C.red, width: 2, dash: "6 6" });
B.plot(D.GFL50.t, D.GFL50.f, { color: C.teal, width: 3 });
B.plot(D.GFL20.t, D.GFL20.f, { color: C.orange, width: 3.5, dash: "12 8" });
B.plot(D.GFM.t, D.GFM.f, { color: C.blue, width: 4 });
B.vline(0);
F.label(895, B.y(64), "GFL PLL 측정", { anchor: "l", size: 22, color: C.teal, weight: 700 });
F.label(895, B.y(57), "GFM: VSM ω<br>느린 스윙만", { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.done();
