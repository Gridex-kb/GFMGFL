// GFL 제어 구조: PCC 전압 → PLL(θ, ω) / |v| 필터 → 전압 제어 ∫ → Q*; P* → 전류 지령 계산 (제한·FRT) → 전류 PI(5강) → PWM
const F = Fig(1600, 560), C = FC;
// 입력: PCC 전압
F.label(40, 150, "PCC 전압 $v$", { anchor: "l", size: 28, color: C.navy, weight: 700 });
F.node(250, 150, { r: 7 });
F.line(250, 150, 250, 330, { color: C.navy, width: 3.5 });
// PLL
harrow(F, 250, 332, 150);
blkRow(F, 440, 150, 210, 96, "SRF-PLL", { fill: "#fde3d6", color: C.orange, tcolor: C.orange, size: 30, weight: 800 });
F.label(440, 76, "측정한다: $v_q \\to 0$", { size: 24, color: C.orange, weight: 700 });
harrow(F, 546, 640, 150);
F.label(592, 118, "$\\theta_c,\\ \\omega$", { size: 28, color: C.orange, weight: 700 });
blkRow(F, 760, 150, 230, 96, "dq 변환", { size: 28 });
F.label(760, 212, "측정 전류·전압", { size: 22, color: C.muted });
// |v| 필터 → 전압 제어
harrow(F, 250, 332, 330);
blkRow(F, 420, 330, 170, 80, "$|v|$ 필터 20 Hz", { size: 24 });
harrow(F, 506, 580, 330);
blkRow(F, 700, 330, 230, 80, "전압 제어 $\\int$", { size: 26 });
F.label(700, 392, "$V^* = 1$ → $Q^*$, |Q*| ≤ 0.6", { size: 22, color: C.muted });
harrow(F, 816, 900, 330);
// P*
F.label(700, 470, "$P^*$ (운전자·EMS)", { anchor: "r", size: 26, color: C.navy, weight: 700 });
F.wire([[720, 470], [1010, 470], [1010, 384]]); varrow(F, 1010, 420, 384);
// 전류 지령 계산
F.rect(900, 276, 220, 108, { r: 12, fill: C.light, color: C.navy, width: 3 });
F.label(1010, 312, "$i_d^* = P^*/v_d$", { size: 26, color: C.navy, weight: 700 });
F.label(1010, 352, "$i_q^* = -Q^*/v_d$", { size: 26, color: C.navy, weight: 700 });
harrow(F, 1120, 1190, 330);
F.rect(1190, 276, 200, 108, { r: 12, fill: C.light, color: C.navy, width: 3 });
F.label(1290, 312, "전류 제한 1.2", { size: 24, color: C.navy, weight: 700 });
F.label(1290, 352, "FRT 무효 우선", { size: 24, color: C.navy, weight: 700 });
F.wire([[1290, 276], [1290, 150]]); harrow(F, 1290, 150, 1390, 150);
F.label(1340, 118, "$i^*_{dq}$", { size: 28, color: C.navy, weight: 700 });
blkRow(F, 1480, 150, 180, 96, "전류 PI (5강)", { size: 24 });
F.line(1570, 150, 1600, 150, { color: C.navy, width: 3.5 });
F.label(1480, 212, "→ PWM (12강)", { size: 22, color: C.muted });
// 연결선 dq → 전류 PI (측정)
F.wire([[875, 150], [1190, 150]], { color: C.muted }); F.label(1030, 118, "$i_{dq}$, $v_{dq}$", { size: 24, color: C.muted });
// 아래 주석
F.rect(60, 500, 1480, 50, { r: 12, fill: "#e9f0f6" });
F.label(800, 525, "같은 하드웨어, 같은 전류 루프 — <b>외부 루프</b>만 다르다. GFL은 θ를 <b>측정</b>해서 전류원이 된다 · 측정점: PCC 전압과 변압기 전류 (3강)", { size: 23, color: C.navy });
F.done();
