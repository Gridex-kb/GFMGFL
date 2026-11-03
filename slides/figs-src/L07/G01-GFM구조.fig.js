// GFM 제어 구조: P_f → VSM 스윙식 → θ; |v|_f → Q–V 적분 → E; PCC v → 동적 가상 인덕턴스 → i*(원형 제한 1.2) → 전류 PI(5강) → PWM
const F = Fig(1600, 560), C = FC;
F.label(40, 130, "$P_f$ (20 Hz 필터)", { anchor: "l", size: 26, color: C.navy, weight: 700 });
harrow(F, 270, 340, 130);
blkRow(F, 480, 130, 280, 96, "VSM 스윙식", { fill: "#fde3d6", color: C.orange, tcolor: C.orange, size: 30, weight: 800 });
F.label(480, 56, "만든다: $2H\\,\\dot{\\Delta\\omega} = P^* - P_f - D\\Delta\\omega$", { size: 24, color: C.orange, weight: 700 });
F.label(480, 192, "$H$ 4 s, $D$ 50 (드룹 2 %)", { size: 22, color: C.muted });
harrow(F, 620, 760, 130);
F.label(690, 98, "$\\theta$", { size: 32, color: C.orange, weight: 700 });
F.label(40, 300, "$|v|_f$ (20 Hz 필터)", { anchor: "l", size: 26, color: C.navy, weight: 700 });
harrow(F, 270, 340, 300);
blkRow(F, 480, 300, 280, 96, "Q–V 적분 → $E$", { size: 28 });
F.label(480, 362, "$V^* = 1$, $E = 1 \\pm 0.3$", { size: 22, color: C.muted });
harrow(F, 620, 760, 300);
F.label(690, 268, "$E$", { size: 32, color: C.navy, weight: 700 });
F.label(40, 470, "PCC 전압 $v$ (θ 좌표)", { anchor: "l", size: 26, color: C.navy, weight: 700 });
F.wire([[330, 470], [900, 470], [900, 404]]); varrow(F, 900, 440, 404);
// 동적 가상 인덕턴스
F.rect(760, 196, 280, 208, { r: 16, fill: "#d9e6fa", color: C.blue, width: 3.5 });
F.label(900, 240, "동적 가상 인덕턴스", { size: 28, color: C.blue, weight: 800 });
F.label(900, 290, "$\\dfrac{X_v}{\\omega_b}\\dot i_v = E - v - R_v i_v - j\\omega X_v i_v$", { size: 22, color: C.navy });
F.label(900, 350, "$X_v$ 0.3, $R_v$ 0.05 pu", { size: 22, color: C.muted });
F.label(900, 384, "출력 $i_v$ → 전류 지령", { size: 22, color: C.blue, weight: 700 });
harrow(F, 1040, 1120, 300);
F.rect(1120, 252, 180, 96, { r: 12, fill: C.light, color: C.navy, width: 3 });
F.label(1210, 288, "원형 제한", { size: 24, color: C.navy, weight: 700 });
F.label(1210, 320, "1.2 pu + AW", { size: 22, color: C.navy });
harrow(F, 1300, 1370, 300);
F.label(1335, 268, "$i^*_{dq}$", { size: 28, color: C.navy, weight: 700 });
blkRow(F, 1470, 300, 200, 96, "전류 PI (5강)", { size: 24 });
F.label(1470, 362, "→ PWM (12강)", { size: 22, color: C.muted });
F.line(1570, 300, 1600, 300, { color: C.navy, width: 3.5 });
// θ → dq 변환 표시
F.wire([[760, 130], [1470, 130], [1470, 252]], { color: C.orange }); varrow(F, 1470, 220, 252, { color: C.orange });
F.label(1120, 98, "θ로 dq 변환 (측정 전류·전압) — PLL 없음", { size: 22, color: C.orange, weight: 700 });
F.rect(400, 504, 1160, 50, { r: 12, fill: "#e9f0f6" });
F.label(980, 529, "계통에서 본 모습: 가상 임피던스 $R_v + jX_v$ 뒤의 <b>전압원</b> $E\\angle\\theta$ · 전류 루프·제한은 GFL과 같은 자리", { size: 23, color: C.navy });
F.done();
