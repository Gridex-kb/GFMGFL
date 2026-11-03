// 단선도: VSC → Lf → (Cf + Rd) → 변압기 Lt → PCC(분로 0.03) → 계통 리액턴스 → 계통 전원. 측정점 표시
const F = Fig(1560, 560), C = FC, y = 200, yg = 430;
F.rect(40, 130, 150, 140, { r: 14, fill: "#e9f0f6", color: C.navy, width: 3.5 });
F.label(115, 182, "VSC", { size: 34, color: C.navy, weight: 800 });
F.label(115, 228, "PWM 펄스", { size: 22, color: C.slate });
F.wire([[190, y], [300, y]]); F.inductor(300, y, 440, { n: 4 });
F.label(370, y - 46, "$L_f$ 0.20", { size: 28, color: C.navy });
F.wire([[440, y], [640, y]]); F.node(520, y);
F.label(520, y - 40, "필터 단자", { size: 22, color: C.muted });
F.wire([[520, y], [520, 250]]); resV(F, 520, 250, 320); F.wire([[520, 320], [520, 352]]); F.cap(520, 365); F.wire([[520, 378], [520, yg]]); F.ground(520, yg);
F.label(548, 285, "$R_d$ 2.0", { anchor: "l", size: 26, color: C.navy });
F.label(552, 365, "$C_f$ 0.05", { anchor: "l", size: 26, color: C.navy });
// 변압기: 겹친 원 두 개
F.circle(675, y, 38, { color: C.navy, width: 3.5, fill: "#ffffff" }); F.circle(725, y, 38, { color: C.navy, width: 3.5 });
F.label(700, y - 64, "변압기 $L_t$ 0.10", { size: 26, color: C.navy });
F.wire([[763, y], [900, y]]); F.node(900, y, { r: 8 });
F.label(900, y - 44, "PCC", { size: 30, color: C.navy, weight: 800 });
F.wire([[900, y], [900, 260]]); resV(F, 900, 260, 340); F.wire([[900, 340], [900, yg]]); F.ground(900, yg);
F.label(928, 300, "분로 0.03", { anchor: "l", size: 24, color: C.slate });
F.wire([[900, y], [1080, y]]); F.inductor(1080, y, 1220, { n: 4 });
F.label(1150, y - 46, "$X_g = 1/\\mathrm{SCR}$", { size: 26, color: C.navy });
F.wire([[1220, y], [1380, y], [1380, 270]]); F.source(1380, 300, 30); F.wire([[1380, 330], [1380, yg]]); F.ground(1380, yg);
F.label(1420, 300, "계통", { anchor: "l", size: 28, color: C.navy, weight: 700 });
// 측정점
const sensor = (x, col, t) => { F.circle(x, y, 16, { color: col, width: 4, fill: "#ffffff" }); F.arrow(x - 9, y, x + 12, y, { color: col, width: 3, head: 10 }); F.label(x, y + 38, t, { size: 30, color: col, weight: 700 }); };
sensor(245, C.orange, "$i_f$"); sensor(830, C.blue, "$i_t$");
F.arrow(900, 115, 900, 160, { color: C.blue, width: 3.5, head: 14 });
F.label(900, 102, "$v_{pcc}$", { anchor: "b", size: 30, color: C.blue, weight: 700 });
// 범례 상자
F.rect(150, 480, 420, 56, { r: 12, fill: "#fde3d6" }); F.label(360, 508, "$i_f$ → 전류 제어 · 전류 제한", { size: 26, color: C.orange, weight: 700 });
F.rect(640, 480, 640, 56, { r: 12, fill: "#d9e6fa" }); F.label(960, 508, "$i_t$, $v_{pcc}$ → P · Q · |V| · PLL · 가상 어드미턴스", { size: 26, color: C.blue, weight: 700 });
F.done();
