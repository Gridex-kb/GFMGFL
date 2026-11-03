// 반송파 비교 PWM: 듀티 (0.5, −0.2, −0.3)일 때 한 반송파 주기의 스위칭 상태 순서
const F = Fig(1300, 560), C = FC, d = { a: 0.5, b: -0.2, c: -0.3 };
const car = (t) => (t <= 100 ? -1 + (2 * t) / 100 : 3 - (2 * t) / 100);
const A = F.frame([110, 50, 1000, 300], [0, 200], [-1.15, 1.15]).axes({ xticks: [0, 50, 100, 150, 200], yticks: [-1, 0, 1], xlabel: "시간 [µs]", ylabel: "반송파 · 듀티" });
A.fn(car, 400, { color: C.navy, width: 4 });
[["a", C.a], ["b", C.b], ["c", C.c]].forEach(([p, col]) => {
  A.fn(() => d[p], 4, { color: col, width: 4, dash: "14 9" });
  A.label(201.5, d[p] + (p === "b" ? 0.08 : p === "c" ? -0.08 : 0), `$d_${p} = ${d[p]}$`.replace("-", "−"), { anchor: "l", size: 24, color: col, weight: 700 });
});
const edges = [0, 35, 40, 75, 125, 160, 165, 200], names = ["111", "110", "100", "000", "100", "110", "111"];
const yb = 452, hb = 64;
names.forEach((s, k) => {
  const xa = A.x(edges[k]), xb = A.x(edges[k + 1]), zero = s === "000" || s === "111";
  F.rect(xa, yb, xb - xa, hb, { fill: zero ? "#eef1f5" : s === "100" ? "#d9e6fa" : "#fde3d6", color: "#ffffff", width: 2 });
  if (xb - xa > 60) F.label((xa + xb) / 2, yb + hb / 2, `${s}<br><span style="font-size:0.8em">${zero ? "영벡터" : s === "100" ? "$\\vec V_1$" : "$\\vec V_2$"}</span>`, { size: 24, color: C.navy, weight: 600 });
});
F.label(A.x(37.5), yb - 10, "110", { anchor: "b", size: 20, color: C.orange, weight: 700 });
F.label(A.x(162.5), yb - 10, "110", { anchor: "b", size: 20, color: C.orange, weight: 700 });
[0, 50, 100].forEach((t) => { A.vline(t, { color: C.slate, width: 2, dash: "4 6" }); F.dot(A.x(t), A.y(car(t)), { r: 9, color: C.navy }); });
F.label(100, yb + hb / 2, "상태", { anchor: "r", size: 24, color: C.slate, weight: 700 });
F.done();
