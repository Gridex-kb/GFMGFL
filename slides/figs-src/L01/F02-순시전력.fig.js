// 상별 순시전력(역률 0.8)과 그 합
const F = Fig(1080, 461), C = FC, w = 2 * Math.PI * 60 / 1000, phi = Math.acos(0.8);
const A = F.frame([96, 70, 920, 310], [0, 33.33], [-0.4, 1.6]).axes({
  xticks: [0, 5, 10, 15, 20, 25, 30], yticks: [0, 0.5, 1, 1.5], xlabel: "시간 [ms]", ylabel: "순시전력 [pu]" });
const sh = { a: 0, b: -2 * Math.PI / 3, c: 2 * Math.PI / 3 };
for (const p of ["a", "b", "c"]) A.fn((t) => Math.cos(w * t + sh[p]) * Math.cos(w * t + sh[p] - phi), 800, { color: C[p], width: 3, opacity: 0.9 });
A.fn(() => 1.2, 10, { color: C.navy, width: 7 });
A.label(3.63, 0.98, "$p_c$", { color: C.c, size: 28, anchor: "b" });
A.label(6.41, 0.98, "$p_b$", { color: C.b, size: 28, anchor: "b" });
A.label(9.19, 0.98, "$p_a$", { color: C.a, size: 28, anchor: "b" });
A.label(14, 1.3, "$p_a+p_b+p_c = \\tfrac{3}{2}\\hat V\\hat I\\cos\\varphi = 1.2$", { color: C.navy, size: 28, anchor: "bl", weight: 700 });
F.done();
