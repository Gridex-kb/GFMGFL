// 개념 두 패널: 왼쪽 원형 포화(요구 전류 수 pu → 원 위, 각도 유지), 오른쪽 전달 가능 전력 P(δ) — 고장 중(Vg 0.3)에는 어떤 δ에서도 P* 0.8에 못 미친다
const F = Fig(1500, 560), C = FC, R = 82, Imax = 1.2;
const P = F.plane(300, 270, R);
P.axis(0, 2.9, "$i_d$", { color: C.axis, width: 2.5, size: 26, back: 1.6 });
P.axis(90, 1.9, "$i_q$", { color: C.axis, width: 2.5, size: 26, back: 2.4 });
P.circle(Imax, { color: C.muted, width: 3, dash: "10 8" });
P.label([-1.0, 1.45], "|i| = 1.2", { size: 22, color: C.muted });
const req = [1.6, -2.2], n = Math.hypot(...req), lim = [req[0] * Imax / n, req[1] * Imax / n];
P.vec(req, { color: C.orange, width: 3.5, dash: "10 8", head: 16 });
P.vec(lim, { color: C.blue, width: 6, head: 24 });
F.dot(...P.xy(lim), { r: 10, color: C.blue });
P.label([req[0] + 0.1, req[1] + 0.05], "요구 전류 $i_v$<br>(고장 시 수 pu)", { anchor: "l", size: 22, color: C.orange, weight: 700 });
P.label([lim[0] + 0.15, lim[1] + 0.35], "제한 후 (각도 유지)", { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.label(300, 40, "원형 포화", { size: 28, color: C.navy, weight: 800 });
// 오른쪽: P(δ)
const X = 0.3 + 0.1 + 1 / 3;
const A = F.frame([800, 110, 600, 380], [0, 180], [0, 1.5]).axes({ xticks: [0, 45, 90, 135, 180], yticks: [0, 0.5, 1.0, 1.5], tick: 22, xlabel: "위상차 δ [°]", ylabel: "전달 가능 전력 $P(\\delta)$ [pu]" });
A.fn((d) => 1.0 / X * Math.sin(d * Math.PI / 180), 400, { color: C.blue, width: 4 });
A.fn((d) => 0.3 / X * Math.sin(d * Math.PI / 180), 400, { color: C.orange, width: 4 });
A.hline(0.8, { color: C.navy, width: 2.5, dash: "8 6" });
A.label(178, 0.84, "$P^*$ = 0.8", { anchor: "br", size: 22, color: C.navy, weight: 700 });
A.label(120, 1.3, "계통 전압 1.0: 최대 1.36", { anchor: "l", size: 22, color: C.blue, weight: 700 });
A.label(90, 0.47, "고장 0.3: 최대 0.41 < $P^*$<br>→ 평형점 없음, δ 가속", { anchor: "t", size: 22, color: C.orange, weight: 700 });
F.label(1100, 34, "전달 가능 전력 (개념, X = 0.3 + 0.1 + 1/3)", { size: 28, color: C.navy, weight: 800 });
F.done();
