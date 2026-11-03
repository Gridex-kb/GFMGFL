// EMT GFM, SCR 2: PCC 전압 피드포워드 없음 / 순시 / 100 Hz LPF. 위 전체 200 ms, 아래 150~170 ms 확대
const F = Fig(1100, 690), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 240], [0, 200], [0, 1.2]).axes({ xticks: [0, 50, 100, 150, 200], yticks: [0, 0.5, 1.0], tick: 22, xlabel: "시간 [ms]", ylabel: "$P$ [pu]" });
A.plot(D.inst.t, D.inst.P, { color: C.orange, width: 2.5 });
A.plot(D.lpf.t, D.lpf.P, { color: C.teal, width: 3.5 });
A.plot(D.none.t, D.none.P, { color: C.blue, width: 3.5, dash: "10 6" });
F.label(895, A.y(1.0), `순시 피드포워드<br>σ(P) ${D.inst.std.toFixed(3)} pu`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.55), `피드포워드 없음<br>σ(P) ${D.none.std.toFixed(3)} pu`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(0.15), `100 Hz 저역통과<br>σ(P) ${D.lpf.std.toFixed(3)} pu`, { anchor: "l", size: 22, color: C.teal, weight: 700 });
const sel = (s) => { const t = [], P = []; s.t.forEach((v, i) => { if (v >= 150 && v <= 170) { t.push(v); P.push(s.P[i]); } }); return [t, P]; };
const B = F.frame([120, 380, 760, 190], [150, 170], [0, 1.2]).axes({ xticks: [150, 155, 160, 165, 170], yticks: [0, 0.5, 1.0], tick: 22, xlabel: "시간 [ms] (20 ms 확대)", ylabel: "" });
B.plot(...sel(D.inst), { color: C.orange, width: 3 });
B.plot(...sel(D.lpf), { color: C.teal, width: 3.5 });
B.plot(...sel(D.none), { color: C.blue, width: 3.5, dash: "10 6" });
F.label(895, B.y(0.6), `진동 약 ${D.inst.f_osc.toFixed(0)} Hz<br>(주기 ≈ ${(1000 / D.inst.f_osc).toFixed(1)} ms)`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.done();
