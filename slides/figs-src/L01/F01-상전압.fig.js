// 평형 3상 상전압 두 주기, 120° 간격 표시
const F = Fig(1060, 452), C = FC, w = 2 * Math.PI * 60 / 1000;
const A = F.frame([96, 70, 900, 300], [0, 33.33], [-1.25, 1.45]).axes({
  xticks: [0, 5, 10, 15, 20, 25, 30], yticks: [-1, 0, 1], xlabel: "시간 [ms]", ylabel: "상전압 [pu]" });
[["a", 0], ["b", -2 * Math.PI / 3], ["c", 2 * Math.PI / 3]].forEach(([p, sh]) =>
  A.fn((t) => Math.cos(w * t + sh), 800, { color: C[p], width: 4.5 }));
A.label(16.67, 1.2, "$v_a$", { color: C.a, size: 32, anchor: "b" });
A.label(22.22, 1.2, "$v_b$", { color: C.b, size: 32, anchor: "b" });
A.label(27.78, 1.2, "$v_c$", { color: C.c, size: 32, anchor: "b" });
A.arrow(0.25, 1.18, 5.3, 1.18, { color: C.slate, width: 3, head: 14, both: true });
A.label(2.78, 1.24, "120° = 5.56 ms", { anchor: "bl", size: 24, color: C.slate });
F.done();
