// 평형 3상의 Clarke 결과: vα = cos, vβ = sin
const F = Fig(840, 360), C = FC, w = 2 * Math.PI * 60 / 1000;
const A = F.frame([96, 60, 710, 222], [0, 33.33], [-1.25, 1.4]).axes({
  xticks: [0, 5, 10, 15, 20, 25, 30], yticks: [-1, 0, 1], xlabel: "시간 [ms]", ylabel: "[pu]" });
A.fn((t) => Math.cos(w * t), 800, { color: C.blue, width: 4.5 });
A.fn((t) => Math.sin(w * t), 800, { color: C.orange, width: 4.5 });
A.label(16.67, 1.12, "$v_\\alpha$", { color: C.blue, size: 32, anchor: "b" });
A.label(20.83, 1.12, "$v_\\beta$", { color: C.orange, size: 32, anchor: "b" });
F.done();
