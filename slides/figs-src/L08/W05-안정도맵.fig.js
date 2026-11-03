// 약계통 안정도 맵 (스위칭 모델, 2 µs, P 0.8, FRT 진입 0.5): 행 = 구성, 열 = SCR. simulation/emt/results/summary.md
const F = Fig(1500, 480), C = FC;
const scrs = ["5.0", "3.0", "2.0", "1.5", "1.3", "1.2"];
const rows = [["GFL · PLL 10 Hz", [1, 1, 1, 1, 0, 0], "SCR 1.3 이하 · ~10 Hz 대진폭"], ["GFL · PLL 35 Hz", [1, 1, 1, 1, 0, 0], "SCR 1.3 이하 · 상호작용형"], ["GFL · PLL 50 Hz", [1, 1, 1, 0, 0, 0], "SCR 1.5 이하 · ~90 Hz 지속"], ["GFM · VSM", [1, 1, 1, 1, 1, 1], "1.2까지 안정"]];
const x0 = 340, cw = 120, y0 = 110, rh = 76;
F.label(x0 - 20, 70, "SCR →", { anchor: "r", size: 24, color: C.muted, weight: 700 });
scrs.forEach((s, j) => F.label(x0 + j * cw + cw / 2, 70, s, { size: 26, color: C.navy, weight: 800 }));
rows.forEach(([name, ok, note], i) => {
  const y = y0 + i * rh;
  F.label(x0 - 20, y + rh / 2, name, { anchor: "r", size: 26, color: i === 3 ? C.blue : C.orange, weight: 700 });
  ok.forEach((v, j) => {
    const x = x0 + j * cw;
    F.rect(x + 4, y + 4, cw - 8, rh - 8, { r: 10, fill: v ? "#d5efe6" : "#fde3d6", color: v ? C.green : C.orange, width: 2.5 });
    F.label(x + cw / 2, y + rh / 2, v ? "안정" : "불안정", { size: 22, color: v ? C.green : C.orange, weight: 700 });
  });
  F.label(x0 + 6 * cw + 20, y + rh / 2, note, { anchor: "l", size: 22, color: C.slate });
});
F.label(750, 440, "스위칭 모델 2 µs, P = 0.8 pu, FRT 진입 0.5 pu(순환 배제) · 빠른 PLL일수록 불안정 경계 SCR이 높다 · 평균값 모델은 경계가 다르다(경향만)", { anchor: "b", size: 21, color: C.muted });
F.done();
