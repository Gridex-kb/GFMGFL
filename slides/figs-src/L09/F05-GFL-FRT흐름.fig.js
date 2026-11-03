// GFL vs GFM 고장 중 동작 흐름: GFL 은 처음부터 전류원(FRT 고정 무효전류), GFM 은 전압원 → 포화 순간 크기 고정 전류원 → 동기 유지 보정
const F = Fig(1500, 420), C = FC;
const row = (y, col, title, steps) => {
  F.label(40, y, title, { anchor: "l", size: 28, color: col, weight: 800 });
  steps.forEach(([t, sub], k) => {
    const x = 330 + k * 300;
    F.rect(x - 130, y - 56, 260, 112, { r: 14, fill: k === steps.length - 1 ? (col === C.orange ? "#fde3d6" : "#d9e6fa") : C.light, color: col, width: 3 });
    F.label(x, y - 14, t, { size: 24, color: col, weight: 700 });
    F.label(x, y + 22, sub, { size: 20, color: C.slate });
    if (k < steps.length - 1) F.arrow(x + 134, y, x + 166, y, { color: C.slate, width: 3.5, head: 16 });
  });
};
row(110, C.orange, "GFL", [["전압 < 0.85", "FRT 진입"], ["무효 1.14 고정", "유효는 여유 0.37 안"], ["PLL이 계속 추종", "가속 문제 없음"], ["회복 ≈ 0.1 s", "측정 → 지령 → 전류"]]);
row(290, C.blue, "GFM", [["전압원 E − v", "|i*| ≈ 2.8 pu 요구"], ["원형 포화 1.2", "크기 고정 전류원"], ["P ≤ |v|·1.2 < P*", "VSM 가속 → freeze"], ["회복 ≈ 0.5 s", "관성 스윙으로 복귀"]]);
F.rect(40, 370, 1420, 44, { r: 12, fill: "#e9f0f6" });
F.label(750, 392, "제한에 걸린 순간 둘 다 <b>크기 고정 전류원</b>: 전압 지지는 방식이 아니라 전류의 크기와 각도가 정한다 (고장 중 평균 PCC 전압 GFL 0.70 / GFM 0.60 pu)", { size: 22, color: C.navy });
F.done();
