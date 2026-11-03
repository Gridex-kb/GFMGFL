// SRF-PLL 블록선도: v_αβ → e^{-jθc} → v_q → PI → Δω (±0.1 제한) → +1 → ωb → ∫ → θc (되먹임)
const F = Fig(1380, 440), C = FC, y = 160;
F.label(40, y, "$v_{\\alpha\\beta}$", { anchor: "l", size: 32, color: C.navy, weight: 700 });
harrow(F, 150, 230, y);
blkRow(F, 310, y, 160, 96, "$e^{-j\\theta_c}$", { size: 32 });
F.label(310, 86, "dq 변환", { size: 24, color: C.muted, weight: 700 });
harrow(F, 390, 470, y);
F.label(430, y - 38, "$v_q$", { size: 30, color: C.orange, weight: 700 });
F.label(430, y + 40, "$v_d$ (안 씀)", { size: 20, color: C.muted });
blkRow(F, 580, y, 220, 96, "$K_p + \\dfrac{K_i}{s}$", { size: 30 });
F.label(580, 86, "PI", { size: 24, color: C.muted, weight: 700 });
harrow(F, 690, 760, y);
blkRow(F, 840, y, 160, 96, "", { fill: "#ffffff" });
F.poly([[792, y + 26], [822, y + 26], [858, y - 26], [888, y - 26]], { color: C.navy, width: 4 });
F.label(840, 86, "±0.1 pu (54~66 Hz)", { size: 22, color: C.muted, weight: 700 });
harrow(F, 920, 990, y);
F.label(955, y - 38, "$\\Delta\\omega$", { size: 28, color: C.navy, weight: 700 });
F.sum(1014, y); F.label(1014, 96, "+1", { size: 26, color: C.navy, weight: 700 }); varrow(F, 1014, 108, 136);
harrow(F, 1036, 1090, y);
blkRow(F, 1160, y, 140, 96, "$\\dfrac{\\omega_b}{s}$", { size: 30 });
F.label(1160, 86, "적분 → 각도", { size: 22, color: C.muted, weight: 700 });
// θc 출력 + 되먹임
F.wire([[1230, y], [1270, y], [1270, 330], [310, 330], [310, 210]]);
varrow(F, 310, 260, 210);
F.label(1290, y, "$\\theta_c$", { anchor: "l", size: 32, color: C.orange, weight: 700 });
F.label(790, 318, "$\\theta_c$로 되먹임: $v_q = V\\sin(\\theta_g - \\theta_c) \\to 0$이면 d축 = 전압 벡터", { anchor: "b", size: 24, color: C.navy });
F.rect(60, 370, 1260, 54, { r: 12, fill: "#fde3d6" });
F.label(690, 397, "$\\omega = 1 + \\Delta\\omega$ (pu) → 측정 주파수 $f = 60\\,\\omega$ · 제한에 걸리면 적분기 정지 (anti-windup)", { size: 23, color: C.orange, weight: 700 });
F.done();
