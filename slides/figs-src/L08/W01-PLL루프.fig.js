// 약계통 GFL: PLL이 자기 전류가 만든 PCC 전압을 추종한다. θc → 전류 방향 → v_pcc = e_g + Z_g·i → PLL
const F = Fig(1300, 520), C = FC, y = 150;
blkRow(F, 150, y, 200, 96, "SRF-PLL", { size: 30, fill: "#fde3d6", color: C.orange, tcolor: C.orange, weight: 800 });
harrow(F, 250, 330, y); F.label(290, y - 36, "$\\theta_c$", { size: 30, color: C.orange, weight: 700 });
blkRow(F, 440, y, 220, 96, "전류 지령 · 전류 루프", { size: 24 });
harrow(F, 550, 640, y); F.label(595, y + 40, "$i = I e^{j\\theta_c}$", { size: 26, color: C.navy, weight: 700 });
F.node(690, y, { r: 11 }); F.label(690, y - 46, "PCC", { size: 26, color: C.navy, weight: 800 });
F.arrow(700, y, 820, y, { color: C.navy, width: 3.5, head: 16 });
F.inductor(820, y, 940, { n: 4 }); F.label(880, y - 44, "$Z_g = 1/\\mathrm{SCR}$", { size: 26, color: C.navy });
F.wire([[940, y], [1040, y], [1040, 200]]); F.source(1040, 230, 30); F.wire([[1040, 260], [1040, 300]]); F.ground(1040, 300);
F.label(1085, 230, "$e_g$ (계통)", { anchor: "l", size: 26, color: C.navy, weight: 700 });
// 되먹임: PCC 전압 → PLL
F.wire([[690, y], [690, 340]], { color: C.orange });
F.block(690, 380, 300, 80, "$v_{pcc} = e_g + Z_g\\, i$", { size: 26, color: C.orange, tcolor: C.orange, fill: "#fde3d6" });
F.wire([[540, 380], [150, 380], [150, 240]], { color: C.orange });
F.arrow(150, 260, 150, 200, { color: C.orange, width: 3.5, head: 16 });
F.label(715, 290, "$v_{pcc}$ 측정", { anchor: "l", size: 26, color: C.orange, weight: 700 });
F.label(305, 366, "PLL이 보는 위상의 일부는 <b>내 전류</b>가 만든 것", { anchor: "b", size: 22, color: C.orange, weight: 700 });
F.rect(60, 440, 1180, 64, { r: 14, fill: "#e9f0f6" });
F.label(650, 472, "θ<b>c</b> 이동 → 전류 방향 변화 → PCC 전압 위상 변화 → PLL이 다시 따라감 · 루프 이득 ∝ $Z_g$ (약계통일수록 크다)", { size: 24, color: C.navy, weight: 700 });
F.done();
