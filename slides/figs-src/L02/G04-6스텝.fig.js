// 6스텝(V1→V6, 각 60°)에서 극전압, 영상분, 상전압(a상)과 기본파
const F = Fig(1150, 630), C = FC, h = VDC / 2;
const st = (th) => { const t = ((th + 30) % 360 + 360) % 360; return ["100", "110", "010", "011", "001", "101"][Math.floor(t / 60)]; };
const pole = (th, k) => (st(th)[k] === "1" ? h : -h);
const vn0 = (th) => (pole(th, 0) + pole(th, 1) + pole(th, 2)) / 3;
const box = (y, hh) => [150, y, 900, hh];
const A1 = F.frame(box(40, 140), [0, 360], [-1.5, 1.5]).axes({ xticks: [0, 60, 120, 180, 240, 300, 360], yticks: [-1.128, 0, 1.128], tick: 22, yfmt: (v) => (v ? (v > 0 ? "+" : "−") + "1.128" : "0"), xfmt: () => "" });
const A2 = F.frame(box(225, 90), [0, 360], [-0.6, 0.6]).axes({ xticks: [0, 60, 120, 180, 240, 300, 360], yticks: [-0.376, 0.376], tick: 22, yfmt: (v) => (v > 0 ? "+" : "−") + "0.376", xfmt: () => "" });
const A3 = F.frame(box(360, 180), [0, 360], [-1.75, 1.75]).axes({ xticks: [0, 60, 120, 180, 240, 300, 360], yticks: [-1.504, -0.752, 0, 0.752, 1.504], tick: 22, xfmt: (v) => String(v),
  yfmt: (v) => (Math.abs(v) < 1e-9 ? "0" : (v > 0 ? "+" : "−") + Math.abs(v).toFixed(3)), xlabel: "전기각 [°]" });
const N = 1440;
const step = (f) => { const xs = [], ys = []; for (let i = 0; i <= N; i++) { const t = (360 * i) / N; xs.push(t); ys.push(f(t)); } return [xs, ys]; };
[[1, C.b, 3], [2, C.c, 3], [0, C.a, 4.5]].forEach(([k, col, w]) => { const [xs, ys] = step((t) => pole(t, k) * (k === 0 ? 1 : 0.94)); A1.plot(xs, ys, { color: col, width: w, opacity: k === 0 ? 1 : 0.55 }); });
{ const [xs, ys] = step(vn0); A2.plot(xs, ys, { color: C.teal, width: 4.5 }); }
A3.fn((t) => (2 / Math.PI) * VDC * Math.cos((t * Math.PI) / 180), 600, { color: C.muted, width: 3, dash: "10 8" });
{ const [xs, ys] = step((t) => pole(t, 0) - vn0(t)); A3.plot(xs, ys, { color: C.a, width: 5 }); }
F.label(1060, 110, "극전압<br>$v_{a0}$", { anchor: "l", size: 24, color: C.slate });
F.label(1060, 270, "영상분<br>$v_{n0}$", { anchor: "l", size: 24, color: C.teal });
F.label(1060, 450, "상전압<br>$v_{an}$", { anchor: "l", size: 24, color: C.a });
F.label(A3.x(100), A3.y(1.45), "점선: 기본파 진폭 $2V_{dc}/\\pi = 1.436$", { anchor: "l", size: 22, color: C.muted });
// 상태 띠
[["100", -30], ["110", 30], ["010", 90], ["011", 150], ["001", 210], ["101", 270], ["100", 330]].forEach(([s, a0]) => {
  const xa = A1.x(Math.max(0, a0)), xb = A1.x(Math.min(360, a0 + 60));
  F.label((xa + xb) / 2, 24, s, { anchor: "c", size: 20, color: C.muted, weight: 600 });
});
F.done();
