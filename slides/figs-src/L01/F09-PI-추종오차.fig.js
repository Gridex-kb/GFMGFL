// 대역폭 100 Hz PI 전류 제어기로 60 Hz 지령을 추종: 정상상태 출력이 위상이 늦다
const F = Fig(1180, 488), C = FC, w = 2 * Math.PI * 60;
// 폐루프 T(jω), L 플랜트(0.2 pu) + PI(kp = ωc L, ki = kp ωc/5)
const L = 0.2 / w, wc = 2 * Math.PI * 100, kp = wc * L, ki = kp * wc / 5;
const cdiv = (a, b) => { const d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
const G = cdiv([kp, -ki / w], [0, L * w]); // (kp + ki/(jω)) / (jωL)
const T = cdiv(G, [1 + G[0], G[1]]), mag = Math.hypot(T[0], T[1]), ang = Math.atan2(T[1], T[0]);
const A = F.frame([96, 60, 1050, 340], [0, 33.33], [-1.3, 1.4]).axes({
  xticks: [0, 5, 10, 15, 20, 25, 30], yticks: [-1, 0, 1], xlabel: "시간 [ms]", ylabel: "전류 [pu]" });
const ref = (t) => Math.cos(w * t / 1000), out = (t) => mag * Math.cos(w * t / 1000 + ang);
const xs = [], up = [], dn = [];
for (let i = 0; i <= 800; i++) { const t = 33.33 * i / 800; xs.push(t); up.push(ref(t)); dn.push(out(t)); }
F.poly(xs.map((x, i) => [A.x(x), A.y(up[i])]).concat(xs.slice().reverse().map((x, i) => [A.x(x), A.y(dn[800 - i])])),
  { closed: true, fill: "#fbd9c8", g: A.g });
A.plot(xs, up, { color: C.navy, width: 5 });
A.plot(xs, dn, { color: C.orange, width: 5, dash: "16 10" });
const lag = (-ang * 180 / Math.PI), tl = 16.67 * (-ang) / (2 * Math.PI) * 1;
A.arrow(16.67, 1.12, 16.67 + (-ang) / w * 1000, 1.12, { color: C.orange, width: 3, head: 13 });
A.label(16.67 + (-ang) / w * 1000 + 0.4, 1.12, `${lag.toFixed(0)}° 늦음`, { anchor: "l", size: 26, color: C.orange, weight: 700 });
A.label(3.5, 1.2, "지령 $i^*$", { anchor: "bl", size: 26, color: C.navy, weight: 700 });
A.label(25.5, 1.2, "출력 $i$ (정상상태)", { anchor: "bl", size: 26, color: C.orange, weight: 700 });
console.log("PI |T|", mag.toFixed(3), "angle", (ang * 180 / Math.PI).toFixed(1));
F.done();
