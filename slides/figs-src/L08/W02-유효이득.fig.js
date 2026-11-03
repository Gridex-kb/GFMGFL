// GFL 정적 운전점 (i_d = 0.8 pu, V_g = 1): sin δ = X_g·i_d → 운전점 각 δ와 PLL 유효 이득 cos δ, SCR의 함수
const F = Fig(1100, 620), C = FC, lg = Math.log10;
const xl = [lg(0.8), lg(10)], xt = [lg(0.8), 0, lg(1.5), lg(2), lg(3), lg(5), lg(10)];
const xf = (v) => { for (const [k, s] of [[0.8, "0.8"], [1, "1"], [1.5, "1.5"], [2, "2"], [3, "3"], [5, "5"], [10, "10"]]) if (Math.abs(v - lg(k)) < 1e-9) return s; return ""; };
const A = F.frame([120, 60, 760, 440], xl, [0, 1.05]).axes({ xticks: xt, yticks: [0, 0.25, 0.5, 0.75, 1.0], tick: 22, xfmt: xf, xlabel: "SCR (i<b>d</b> = 0.8 pu, V<b>g</b> = 1)", ylabel: "PLL 유효 이득 cos δ  ·  δ/90°" });
A.fn((x) => pllGain(10 ** x).cos, 600, { color: C.orange, width: 5 });
A.fn((x) => pllGain(10 ** x).delta / 90, 600, { color: C.blue, width: 4, dash: "12 8" });
[5, 3, 2, 1.5, 1.2, 1].forEach((s) => { const g = pllGain(s); F.dot(A.x(lg(s)), A.y(g.cos), { r: 8, color: C.orange }); A.label(lg(s), g.cos + 0.06, `${g.cos.toFixed(2)}`, { anchor: "b", size: 20, color: C.orange, weight: 700 }); });
A.label(lg(1.55), 0.40, "δ = 32°", { anchor: "bl", size: 22, color: C.blue, weight: 700 });
A.label(lg(0.86), 0.12, "SCR 0.8: δ = 90°, 평형점 소멸", { anchor: "l", size: 22, color: C.red, weight: 700 });
F.label(895, A.y(0.9), "cos δ<br>(설계 이득의 몇 배)", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(895, A.y(0.3), "δ / 90°<br>운전점 각", { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(895, A.y(0.08), "sin δ = X<b>g</b> i<b>d</b>", { anchor: "l", size: 22, color: C.slate });
F.done();
