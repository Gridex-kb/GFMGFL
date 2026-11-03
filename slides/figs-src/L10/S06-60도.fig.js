// T09 위상각 −60° 내성 (SCR 3, P0 0.5, 스위칭 2 µs): 유효전력과 계통 대비 위상 — GFM 은 전류 제한에 갇힌다
const F = Fig(1100, 730), C = FC, D = DATA, xl = [-0.05, 1.5];
const A = F.frame([120, 50, 760, 300], xl, [-0.3, 0.7]).axes({ xticks: [0, 0.5, 1.0, 1.5], yticks: [-0.2, 0, 0.2, 0.4, 0.6], tick: 22, xfmt: () => "", ylabel: "유효전력 $P$ [pu]" });
A.hline(0.5, { color: C.muted, width: 2, dash: "6 6" });
A.vline(0, { color: C.navy, width: 2.5, dash: "8 6" });
A.plot(D.GFL.t, D.GFL.P, { color: C.orange, width: 3 });
A.plot(D.GFM.t, D.GFM.P, { color: C.blue, width: 3.5 });
A.label(0.02, 0.68, "−60° 점프", { anchor: "l", size: 20, color: C.navy, weight: 700 });
F.label(895, A.y(0.55), "GFL: 새 위상을<br>잡고 P 0.5 복귀<br>(적합)", { anchor: "l", size: 20, color: C.orange, weight: 700 });
F.label(895, A.y(0.0), `GFM: P ${D.GFM.P_end.toFixed(2)} pu<br>고착, |i| 1.20 pu<br>→ 부적합`, { anchor: "l", size: 20, color: C.blue, weight: 700 });
const B = F.frame([120, 390, 760, 300], xl, [-10, 80]).axes({ xticks: [0, 0.5, 1.0, 1.5], yticks: [0, 20, 40, 60, 80], tick: 22, xlabel: "점프 후 시간 [s]", ylabel: "위상 변화 Δδ [°]" });
B.hline(60, { color: C.muted, width: 2, dash: "6 6" });
B.vline(0, { color: C.navy, width: 2.5, dash: "8 6" });
B.plot(D.GFL.t, D.GFL.dd, { color: C.orange, width: 3 });
B.plot(D.GFM.t, D.GFM.dd, { color: C.blue, width: 3.5 });
F.label(895, B.y(72), "점선: 점프 크기 60°", { anchor: "l", size: 18, color: C.muted });
F.label(895, B.y(48), "GFL: 60° 따라가<br>원래 운전점", { anchor: "l", size: 20, color: C.orange, weight: 700 });
F.label(895, B.y(14), `GFM: 위상차 ${D.GFM.dd_end.toFixed(0)}°<br>남음. freeze 가<br>재동기 각도 이동<br>까지 막음`, { anchor: "l", size: 20, color: C.blue, weight: 700 });
F.done();
