// T13 한국 연계기준안 고장전류 (PCC 3상 지락 0.05 pu × 200 ms, SCR 3, P0 0.8, 스위칭 2 µs): 전류 한계 1.2 / 2.0, GFL / GFM
const F = Fig(1100, 560), C = FC, D = DATA, xl = [-20, 400];
const A = F.frame([120, 60, 760, 420], xl, [0, 2.8]).axes({ xticks: [0, 100, 200, 300, 400], yticks: [0, 0.5, 1.0, 1.5, 2.0, 2.5], tick: 22, xlabel: "고장 시작 후 시간 [ms] (음영: PCC 지락)", ylabel: "컨버터측 전류 |i| [pu]" });
shade(F, A, 0, 200);
A.hline(2.0, { color: C.red, width: 2, dash: "6 6" });
A.plot(D["GFL_1.2"].t_ms, D["GFL_1.2"].I, { color: C.orange, width: 3 });
A.plot(D["GFM_1.2"].t_ms, D["GFM_1.2"].I, { color: C.blue, width: 3.5 });
A.plot(D["GFL_2.0"].t_ms, D["GFL_2.0"].I, { color: C.purple, width: 3, dash: "10 8" });
A.plot(D["GFM_2.0"].t_ms, D["GFM_2.0"].I, { color: C.teal, width: 3.5, dash: "10 8" });
F.arrow(A.x(0), A.y(2.6), A.x(140), A.y(2.6), { color: C.navy, width: 3, head: 14, both: true });
A.label(70, 2.66, "기준안: 2.0 pu 이상 140 ms", { anchor: "b", size: 22, color: C.navy, weight: 700 });
F.label(895, A.y(2.45), `한계 2.0 사양<br>GFM ${D["GFM_2.0"].dur_ms} ms<br>GFL ${D["GFL_2.0"].dur_ms} ms<br>→ 크기 조건 적합`, { anchor: "l", size: 20, color: C.teal, weight: 700 });
F.label(895, A.y(1.45), `한계 1.2 사양<br>최대 ${D["GFM_1.2"].Imax_fault.toFixed(2)} / ${D["GFL_1.2"].Imax_fault.toFixed(2)}<br>→ 2.0 에 못 닿음`, { anchor: "l", size: 20, color: C.blue, weight: 700 });
F.label(895, A.y(0.5), "전압원 동작은<br>구조로 판정:<br>GFM 적합<br>GFL 부적합", { anchor: "l", size: 20, color: C.slate });
F.done();
