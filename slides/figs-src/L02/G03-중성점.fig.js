// 극전압 세 개(DC 중점 0 기준)가 같은 임피던스 Z를 지나 부하 중성점 n에서 만난다
const F = Fig(760, 520), C = FC;
const x0 = 90, xn = 640, ys = [90, 235, 380], ph = ["a", "b", "c"], col = [C.a, C.b, C.c];
F.wire([[x0, ys[0]], [x0, ys[2]]]); F.node(x0, ys[1]);
F.label(x0 - 16, ys[1], "$0$", { anchor: "r", size: 32, color: C.navy, weight: 700 });
F.wire([[xn, ys[0]], [xn, ys[2]]]); F.node(xn, ys[1]);
F.label(xn + 16, ys[1], "$n$", { anchor: "l", size: 32, color: C.navy, weight: 700 });
ys.forEach((y, k) => {
  F.wire([[x0, y], [190, y]]); F.source(220, y, 30, { color: col[k] }); F.wire([[250, y], [400, y]]);
  F.rect(400, y - 24, 110, 48, { r: 8, color: C.navy, width: 3.5, fill: "#ffffff" });
  F.label(455, y, "$Z$", { size: 30, color: C.navy });
  F.wire([[510, y], [xn, y]]);
  F.label(220, y - 40, `$v_{${ph[k]}0}$`, { anchor: "b", size: 28, color: col[k], weight: 700 });
  F.arrow(285, y - 16, 365, y - 16, { color: C.slate, width: 2.5, head: 12 });
  F.label(325, y - 22, `$i_${ph[k]}$`, { anchor: "b", size: 24, color: C.slate });
});
F.path(`M${x0},${ys[2] + 30} Q ${(x0 + xn) / 2},${ys[2] + 90} ${xn},${ys[2] + 30}`, { color: C.teal, width: 3, dash: "8 7" });
F.label((x0 + xn) / 2, ys[2] + 70, "$v_{n0}$", { anchor: "t", size: 30, color: C.teal, weight: 700 });
F.done();
