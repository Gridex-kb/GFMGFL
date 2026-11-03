// 전력 동기화의 음의 되먹임: P > P* → Δω < 0 → θ 뒤처짐 → δ 감소 → P 감소 (PLL 없이 계통과 같은 속도로 돈다)
const F = Fig(1500, 330), C = FC, y = 120;
const steps = [["계통이 더 끌어감", "$P > P^*$", C.orange], ["스윙식", "$\\Delta\\omega < 0$", C.navy], ["θ가 뒤처짐", "$\\dot\\theta < \\omega_b$", C.navy], ["위상차 감소", "$\\delta \\downarrow$", C.navy], ["회로 법칙", "$P \\downarrow$", C.teal]];
steps.forEach(([t, eq, col], k) => {
  const x = 150 + k * 300;
  F.rect(x - 120, y - 70, 240, 140, { r: 16, fill: k === 0 ? "#fde3d6" : k === 4 ? "#d5efe6" : C.light, color: col, width: 3 });
  F.label(x, y - 24, t, { size: 26, color: col, weight: 800 });
  F.label(x, y + 26, eq, { size: 30, color: col, weight: 700 });
  if (k < 4) F.arrow(x + 124, y, x + 176, y, { color: C.slate, width: 4, head: 18 });
});
F.path(`M${1350},${y + 70} L${1350},${y + 130} L${150},${y + 130} L${150},${y + 74}`, { color: C.slate, width: 3.5, dash: "10 8" });
F.arrow(150, y + 100, 150, y + 72, { color: C.slate, width: 3.5, head: 16 });
F.label(750, y + 118, "음의 되먹임 → 되돌아온다 (반대 방향도 같다)", { anchor: "b", size: 24, color: C.slate, weight: 700 });
F.rect(80, 270, 1340, 50, { r: 12, fill: "#e9f0f6" });
F.label(750, 295, "계통 위상·주파수가 바뀌면 δ가 <b>먼저</b> 바뀌고 전력은 그 순간 회로 법칙으로 바뀐다. 제어기는 그 뒤에 θ를 천천히 맞춘다", { size: 23, color: C.navy });
F.done();
