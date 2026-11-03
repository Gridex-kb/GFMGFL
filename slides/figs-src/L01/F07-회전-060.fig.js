// 공간벡터 합성: ωt = 60°에서 (2/3)(va + a·vb + a²·vc)를 화살표로 이어 붙인다 (gen: L01 sv 템플릿)
const F = Fig(460, 460), C = FC, P = F.plane(230, 230, 138), pol = P.pol;
const wt = 60, rad = (d) => (d * Math.PI) / 180;
[["a", 0], ["b", 120], ["c", 240]].forEach(([p, d]) => {
  P.axis(d, 1.22, p + "축", { color: C.grid, lcolor: C[p], back: 1.22, width: 3, size: 26 });
});
P.circle(1, { color: C.axis, width: 2.5, dash: "4 8" });
P.arc(1, 0, wt, { color: C.navy, width: 3, opacity: 0.35, arrow: true });
const vals = { a: Math.cos(rad(wt)), b: Math.cos(rad(wt - 120)), c: Math.cos(rad(wt + 120)) };
const v = pol(1, wt);
const [vx, vy] = P.xy(v);
F.line(P.cx, P.cy, vx, vy, { color: C.navy, width: 22, opacity: 0.13 });
let acc = [0, 0];
[["a", 0], ["b", 120], ["c", 240]].forEach(([p, d]) => {
  const t = pol((2 / 3) * vals[p], d);
  if (Math.hypot(t[0], t[1]) > 0.02) P.vec(t, { color: C[p], width: 5.5, head: 20 }, acc);
  acc = [acc[0] + t[0], acc[1] + t[1]];
});
P.label(pol(1.17, wt + 11), "$\\vec v$", { color: C.navy, size: 36, weight: 700 });
F.label(460 - 22, 460 - 22, "$\\omega t = 60^\\circ$", { anchor: "br", size: 30, color: C.navy, weight: 700 });
F.done();
