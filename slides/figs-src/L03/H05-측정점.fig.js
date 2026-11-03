// 같은 샘플 시점(10 kHz)에서 두 측정점으로 계산한 P: 위 시간 파형, 아래 스펙트럼
const F = Fig(1100, 640), C = FC, D = DATA;
const mean = D.Pp.reduce((a, b) => a + b, 0) / D.Pp.length;
const A1 = F.frame([110, 40, 800, 210], [0, 100], [mean - 0.035, mean + 0.035]).axes({ xticks: [0, 20, 40, 60, 80, 100], yticks: [+(mean - 0.03).toFixed(2), +mean.toFixed(2), +(mean + 0.03).toFixed(2)], tick: 22, xlabel: "시간 [ms]" });
A1.plot(D.t, D.Pl, { color: C.orange, width: 1.6, opacity: 0.9 }); A1.plot(D.t, D.Pp, { color: C.blue, width: 2.6 });
const A2 = F.frame([110, 370, 800, 190], [0, 2000], [0, Math.max(...D.Fl) * 1.1]).axes({ xticks: [0, 360, 720, 1080, 1440, 1800], yticks: [0, 1, 2], tick: 22, xlabel: "주파수 [Hz]" });
[360, 720, 1080, 1440, 1800].forEach((f) => A2.vline(f, { color: C.axis, width: 2, dash: "4 6" }));
A2.plot(D.f, D.Fl, { color: C.orange, width: 2.4 }); A2.plot(D.f, D.Fp, { color: C.blue, width: 2.8 });
F.label(120, 24, "샘플 시점 P [pu]", { anchor: "l", size: 22, color: C.slate });
F.label(120, 354, "스펙트럼 [10⁻³ pu] · 점선: 360 Hz 배수", { anchor: "l", size: 22, color: C.slate });
F.label(930, 100, `$L_f$ · 필터 단자<br>σ = ${D.sl.toFixed(4)}`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(930, 190, `변압기 · PCC<br>σ = ${D.sp.toFixed(4)}`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.done();
