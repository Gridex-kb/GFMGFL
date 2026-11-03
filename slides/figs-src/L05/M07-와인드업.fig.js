// 1 pu id 계단: 조건부 적분(anti-windup) 있음 vs 없음
const F = Fig(1100, 560), C = FC, D = DATA;
const A = F.frame([120, 60, 760, 420], [-0.5, 11], [0, 1.8]).axes({ xticks: [0, 2, 4, 6, 8, 10], yticks: [0, 0.5, 1.0, 1.5], tick: 22, xlabel: "계단 이후 시간 [ms]", ylabel: "$i_d$ [pu]" });
A.plot([-0.5, 0, 0, 11], [0, 0, 1, 1], { color: C.muted, width: 2.5, dash: "10 8" });
A.hline(PR.Imax, { color: C.red, width: 2.5, dash: "6 6" });
A.plot(D.t, D.noaw, { color: C.orange, width: 4 });
A.plot(D.t, D.aw, { color: C.blue, width: 4.5 });
F.label(895, A.y(1.62), `anti-windup 없음<br>오버슈트 ${D.os_noaw.toFixed(0)} %`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(1.2), "전류 한계 1.2 pu", { anchor: "l", size: 22, color: C.red, weight: 700 });
F.label(895, A.y(0.85), `조건부 적분 (모델)<br>오버슈트 ${D.os_aw.toFixed(0)} %`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(0.4), "포화 중 적분 정지 →<br>풀린 뒤 튀지 않는다", { anchor: "l", size: 20, color: C.slate });
F.done();
