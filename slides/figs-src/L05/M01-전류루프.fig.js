// dq 전류루프 블록선도: PI → (+디커플링, +점선 피드포워드) → 포화 1.303 → 지연 e^{-1.5sTs} → 플랜트 ωb/(sLf), 외란 −jωLf·i − v_t
const F = Fig(1600, 500), C = FC, y = 200;
const blk = (x, w, t, s = {}) => F.block(x, y, w, 96, t, Object.assign({ size: 30 }, s));
const arr = (x1, x2, yy = y, s = {}) => F.arrow(x1, yy, x2, yy, Object.assign({ color: C.navy, width: 3.5, head: 16 }, s));
// 지령 → 합산점 1
F.label(40, y, "$i^*_{dq}$", { anchor: "l", size: 32, color: C.navy, weight: 700 });
arr(130, 196); F.sum(220, y); F.label(200, y - 38, "+", { size: 26, color: C.navy }); F.label(240, y + 44, "−", { size: 28, color: C.navy });
F.label(282, y - 34, "$e$", { size: 28, color: C.navy });
arr(242, 320); blk(420, 200, "$K_p + \\dfrac{K_i}{s}$", { size: 30 });
F.label(420, y - 76, "PI", { size: 26, color: C.muted, weight: 700 });
// 합산점 2: 디커플링과 피드포워드
arr(520, 596); F.sum(620, y);
F.label(650, y + 44, "+", { size: 26, color: C.blue });
F.label(650, y - 40, "+", { size: 26, color: C.orange });
F.arrow(620, 380, 620, 224, { color: C.blue, width: 3.5, head: 16 });
F.rect(500, 380, 240, 60, { r: 12, fill: "#d9e6fa" }); F.label(620, 410, "$j\\omega L_f\\, i_{dq}$", { size: 28, color: C.blue, weight: 700 });
F.label(620, 462, "교차결합 디커플링 (항상 켬)", { size: 22, color: C.blue });
F.arrow(620, 98, 620, 176, { color: C.orange, width: 3.5, head: 16, dash: "10 8" });
F.rect(520, 44, 200, 54, { r: 12, fill: "#fde3d6" }); F.label(620, 71, "$k_{ff}\\, v_{dq}$", { size: 26, color: C.orange, weight: 700 });
F.label(748, 71, "전압 피드포워드 (기본 0, 점선)", { anchor: "l", size: 22, color: C.orange });
// 포화 → 지연
arr(642, 720); blk(800, 160, "", { fill: "#ffffff" });
F.poly([[752, y + 26], [782, y + 26], [818, y - 26], [848, y - 26]], { color: C.navy, width: 4 });
F.label(800, y - 76, "포화 |v| ≤ 1.303", { size: 24, color: C.muted, weight: 700 });
arr(880, 956); blk(1040, 170, "$e^{-1.5\\,sT_s}$", { size: 30 });
F.label(1040, y - 76, "지연 150 µs", { size: 24, color: C.muted, weight: 700 });
F.label(918, y - 34, "$v^*_{c,dq}$", { size: 26, color: C.navy });
// 합산점 3: 외란 → 플랜트
arr(1125, 1196); F.sum(1220, y); F.label(1200, y - 38, "+", { size: 26, color: C.navy }); F.label(1250, y + 44, "−", { size: 28, color: C.orange });
F.arrow(1220, 380, 1220, 224, { color: C.orange, width: 3.5, head: 16 });
F.rect(1070, 380, 300, 60, { r: 12, fill: "#fde3d6" }); F.label(1220, 410, "$j\\omega L_f\\, i_{dq} + v_{t,dq}$", { size: 28, color: C.orange, weight: 700 });
F.label(1220, 462, "플랜트의 외란 (결합 + 계통 전압)", { size: 22, color: C.orange });
arr(1242, 1320); blk(1420, 180, "$\\dfrac{\\omega_b}{s L_f}$", { size: 30 });
F.label(1420, y - 76, "플랜트 $L_f$", { size: 24, color: C.muted, weight: 700 });
arr(1510, 1585); F.label(1555, y - 38, "$i_{dq}$", { size: 32, color: C.navy, weight: 700 });
// 되먹임
F.node(1548, y, { r: 6 });
F.poly([[1548, y], [1548, 330], [220, 330], [220, 250]], { color: C.navy, width: 3.5 });
F.arrow(220, 300, 220, 226, { color: C.navy, width: 3.5, head: 16 });
F.label(880, 318, "측정 $i_{dq}$ (샘플 시점 $\\theta_k$, 4강)", { anchor: "b", size: 24, color: C.navy });
F.done();
