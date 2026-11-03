// VSM 스윙식 블록선도: P* − P_f → 1/(2Hs + D) → Δω → +1 → ωb/s → θ. 되먹임: θ → δ → P (회로) → 측정 20 Hz → P_f
const F = Fig(1400, 440), C = FC, y = 150;
F.label(40, y, "$P^*$", { anchor: "l", size: 32, color: C.navy, weight: 700 });
harrow(F, 110, 176, y); F.sum(200, y); F.label(182, y - 38, "+", { size: 26, color: C.navy }); F.label(220, y + 44, "−", { size: 28, color: C.navy });
harrow(F, 222, 300, y);
blkRow(F, 420, y, 240, 96, "$\\dfrac{1}{2Hs + D}$", { size: 30, fill: "#fde3d6", color: C.orange, tcolor: C.orange });
F.label(420, 80, "관성 $H$ 4 s · 댐핑 $D$ 50", { size: 24, color: C.orange, weight: 700 });
harrow(F, 540, 620, y);
F.label(580, y - 38, "$\\Delta\\omega$", { size: 28, color: C.navy, weight: 700 });
F.sum(644, y); F.label(644, 86, "+1", { size: 26, color: C.navy, weight: 700 }); varrow(F, 644, 98, 126);
harrow(F, 666, 740, y);
blkRow(F, 820, y, 150, 96, "$\\dfrac{\\omega_b}{s}$", { size: 30 });
harrow(F, 895, 980, y);
F.label(1010, y, "$\\theta$", { anchor: "l", size: 34, color: C.orange, weight: 700 });
// 회로 → P → 필터 → 되먹임
F.wire([[1070, y], [1130, y], [1130, 330]]);
blkRow(F, 1130, 240, 240, 80, "회로: δ → P", { size: 24, fill: C.light });
F.label(1130, 300, "$P \\approx (EV/X)\\sin\\delta$", { size: 22, color: C.slate });
F.wire([[1130, 330], [200, 330], [200, 230]]); varrow(F, 200, 260, 226);
blkRow(F, 660, 330, 240, 70, "측정 20 Hz 필터", { size: 24, fill: C.light });
F.label(430, 318, "$P_f$", { anchor: "b", size: 28, color: C.navy, weight: 700 });
F.rect(60, 380, 1280, 50, { r: 12, fill: "#fde3d6" });
F.label(700, 405, "정상상태 $\\dot{\\Delta\\omega} = 0$: $\\Delta\\omega = (P^* - P)/D$ → 드룹 $m_p = 1/D = 2\\,\\%$ · 동기기 회전자를 제어기가 대신한다", { size: 23, color: C.orange, weight: 700 });
F.done();
