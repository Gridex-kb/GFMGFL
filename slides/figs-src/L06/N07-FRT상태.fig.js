// FRT 상태 전이: 정상(유효 우선) ⇄ FRT(무효 1.14 pu 고정). 진입 |v|f < 0.85, 해제 |v|f > 0.92 AND 30 ms 경과
const F = Fig(1500, 420), C = FC, y = 170;
F.rect(80, y - 80, 480, 160, { r: 20, fill: "#d9e6fa", color: C.blue, width: 3.5 });
F.label(320, y - 34, "정상 운전", { size: 34, color: C.blue, weight: 800 });
F.label(320, y + 14, "$i_d^* = P^*/v_d$, 전압 제어 → $Q^*$", { size: 24, color: C.navy });
F.label(320, y + 50, "제한: 유효 우선", { size: 22, color: C.slate });
F.rect(940, y - 80, 480, 160, { r: 20, fill: "#fde3d6", color: C.orange, width: 3.5 });
F.label(1180, y - 34, "FRT (저전압 통과)", { size: 34, color: C.orange, weight: 800 });
F.label(1180, y + 14, "$i_q^* = -0.95 \\times 1.2 = -1.14$ 고정", { size: 24, color: C.navy });
F.label(1180, y + 50, "$i_d^*$ 여유 ≈ 0.37 pu 이내", { size: 22, color: C.slate });
// 전이 화살표
F.arrow(560, y - 40, 940, y - 40, { color: C.orange, width: 4.5, head: 20 });
F.label(750, y - 62, "진입: $|v|_f < 0.85$ pu", { anchor: "b", size: 26, color: C.orange, weight: 700 });
F.arrow(940, y + 22, 560, y + 22, { color: C.blue, width: 4.5, head: 20 });
F.label(750, y + 52, "해제: $|v|_f > 0.92$ pu <b>그리고</b> 진입 후 30 ms 경과", { anchor: "t", size: 26, color: C.blue, weight: 700 });
F.rect(80, 300, 1340, 90, { r: 14, fill: "#e9f0f6" });
F.label(750, 326, "약계통(SCR 1.5, $X_g$ ≈ 0.67)에서 고정 1.14 pu 무효전류는 PCC 전압을 약 $0.67 \\times 1.14 \\approx 0.76$ pu 올린다", { size: 24, color: C.navy, weight: 700 });
F.label(750, 366, "→ 과전압으로 해제 → 지지가 사라져 다시 저전압 → 재진입 … <b>FRT 모드 순환</b> (주입량이 측정 전압과 무관해 스스로 멈추지 못함)", { size: 22, color: C.slate });
F.done();
