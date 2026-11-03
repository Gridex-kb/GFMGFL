// 예제 답: 상태 110 = V2, 1.504 pu ∠60°
const F = Fig(640, 600), C = FC, P = F.plane(320, 300, 150);
hexagon(F, P, { hi: "110", zero: false });
P.arc(0.45, 0, 60, { color: C.orange, width: 3 });
P.label(P.pol(0.6, 30), "$60^\\circ$", { size: 26, color: C.orange });
F.done();
