// 피드포워드는 또 하나의 되먹임: 제어기 → 컨버터 → i → PCC 전압 v_pcc = e_g + Z_g·i → 측정·지연 → k_ff → 제어기
const F = Fig(1300, 520), C = FC, y = 150;
F.block(170, y, 220, 96, "전류 제어기", { size: 28 });
F.arrow(282, y, 356, y, { color: C.navy, width: 3.5, head: 16 });
F.block(460, y, 200, 96, "컨버터 + $L_f$", { size: 28 });
F.arrow(562, y, 676, y, { color: C.navy, width: 3.5, head: 16 });
F.label(620, y - 36, "$i$", { size: 30, color: C.navy, weight: 700 });
F.node(690, y, { r: 11 }); F.label(690, y - 44, "PCC", { size: 26, color: C.navy, weight: 800 });
F.arrow(700, y, 820, y, { color: C.navy, width: 3.5, head: 16 });
F.inductor(820, y, 940, { n: 4 }); F.label(880, y - 44, "$Z_g = 1/\\mathrm{SCR}$", { size: 26, color: C.navy });
F.wire([[940, y], [1040, y], [1040, 200]]); F.source(1040, 230, 30); F.wire([[1040, 260], [1040, 300]]); F.ground(1040, 300);
F.label(1085, 230, "$e_g$ (계통)", { anchor: "l", size: 26, color: C.navy, weight: 700 });
// 되먹임 경로 (주황)
F.wire([[690, y], [690, 340]], { color: C.orange });
F.block(690, 380, 280, 80, "측정 + 지연 1.5 Ts", { size: 26, color: C.orange, tcolor: C.orange, fill: "#fde3d6" });
F.arrow(550, 380, 470, 380, { color: C.orange, width: 3.5, head: 16 });
F.block(390, 380, 160, 80, "$k_{ff}$", { size: 30, color: C.orange, tcolor: C.orange, fill: "#fde3d6" });
F.wire([[310, 380], [170, 380], [170, 240]], { color: C.orange });
F.arrow(170, 260, 170, 200, { color: C.orange, width: 3.5, head: 16 });
F.label(712, 290, "$v_{pcc}$", { anchor: "l", size: 30, color: C.orange, weight: 700 });
F.label(230, 300, "+ 지령에 더함", { anchor: "l", size: 22, color: C.orange });
// 핵심 식
F.rect(60, 440, 1180, 64, { r: 14, fill: "#e9f0f6" });
F.label(650, 472, "$v_{pcc} = e_g + Z_g\\, i$ → 측정 전압은 내 전류의 함수 → 피드포워드 = $Z_g$를 거친 또 하나의 되먹임 (약계통일수록 이득 ↑)", { size: 24, color: C.navy, weight: 700 });
F.done();
