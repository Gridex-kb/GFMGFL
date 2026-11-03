// 예제 1: i = cos(ωt − 30°)를 abc / αβ / dq 로 본 3단 그림
const F = Fig(884, 566), C = FC, w = 2 * Math.PI * 60 / 1000, ph = -Math.PI / 6;
const rows = [["abc", 30], ["αβ", 200], ["dq", 370]];
const mk = (y0, last) => F.frame([110, y0, 610, 128], [0, 33.33], [-1.3, 1.3]).axes({
  xticks: [0, 10, 20, 30], yticks: [-1, 0, 1], tick: 22, fmt: last ? undefined : () => "" });
const A1 = mk(30), A2 = mk(200), A3 = mk(370, true);
[["a", 0], ["b", -2 * Math.PI / 3], ["c", 2 * Math.PI / 3]].forEach(([p, s]) => A1.fn((t) => Math.cos(w * t + s + ph), 600, { color: C[p], width: 3.5 }));
A2.fn((t) => Math.cos(w * t + ph), 600, { color: C.blue, width: 3.5 });
A2.fn((t) => Math.sin(w * t + ph), 600, { color: C.orange, width: 3.5 });
A3.fn(() => Math.cos(ph), 10, { color: C.blue, width: 5 });
A3.fn(() => Math.sin(ph), 10, { color: C.orange, width: 5 });
F.label(14, 94, "abc", { anchor: "l", size: 28, color: C.navy, weight: 700 });
F.label(14, 264, "$\\alpha\\beta$", { anchor: "l", size: 30, color: C.navy, weight: 700 });
F.label(14, 434, "$dq$", { anchor: "l", size: 30, color: C.navy, weight: 700 });
F.label(736, 60, "$i_a, i_b, i_c$", { anchor: "l", size: 24, color: C.slate });
F.label(736, 230, "$i_\\alpha, i_\\beta$", { anchor: "l", size: 24, color: C.slate });
F.label(736, A3.y(0.866), "$i_d = 0.866$", { anchor: "l", size: 24, color: C.blue, weight: 700 });
F.label(736, A3.y(-0.5), "$i_q = -0.5$", { anchor: "l", size: 24, color: C.orange, weight: 700 });
F.label(874, 556, "시간 [ms]", { anchor: "br", size: 22, color: C.slate });
F.done();
