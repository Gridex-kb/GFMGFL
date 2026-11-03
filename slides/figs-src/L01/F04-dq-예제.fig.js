// θ = ωt 고정, 25 ms 진폭 1→0.7, 50 ms 위상 +30° 일 때 vd, vq (배경: va)
const F = Fig(1500, 420), C = FC, w = 2 * Math.PI * 60 / 1000;
const amp = (t) => (t < 25 ? 1 : 0.7), ph = (t) => (t < 50 ? 0 : Math.PI / 6);
const A = F.frame([96, 56, 1360, 290], [0, 75], [-1.15, 1.3]).axes({
  xticks: [0, 10, 20, 30, 40, 50, 60, 70], yticks: [-1, 0, 1], xlabel: "시간 [ms]", ylabel: "[pu]" });
A.fn((t) => amp(t) * Math.cos(w * t + ph(t)), 3000, { color: C.axis, width: 2.5, opacity: 0.8 });
A.vline(25); A.vline(50);
A.fn((t) => amp(t) * Math.cos(ph(t)), 3000, { color: C.blue, width: 6 });
A.fn((t) => amp(t) * Math.sin(ph(t)), 3000, { color: C.orange, width: 6 });
A.label(12.5, 1.08, "$v_d = 1.0$", { color: C.blue, size: 28, anchor: "b" });
A.label(37.5, 0.78, "$v_d = 0.7$", { color: C.blue, size: 28, anchor: "b" });
A.label(62.5, 0.69, "$v_d = 0.61$", { color: C.blue, size: 28, anchor: "b" });
A.label(62.5, 0.28, "$v_q = 0.35$", { color: C.orange, size: 28, anchor: "t" });
A.label(12.5, 0.08, "$v_q = 0$", { color: C.orange, size: 28, anchor: "b" });
A.label(25.6, 1.22, "진폭 1 → 0.7", { anchor: "l", size: 24, color: C.slate, bg: "#ffffff" });
A.label(50.6, 1.22, "위상 +30°", { anchor: "l", size: 24, color: C.slate, bg: "#ffffff" });
A.label(73.5, -0.95, "회색: $v_a$", { anchor: "r", size: 22, color: C.muted });
F.done();
