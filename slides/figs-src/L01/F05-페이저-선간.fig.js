// 상전압 페이저와 선간전압 Vab = Va − Vb
const F = Fig(600, 533), C = FC, P = F.plane(200, 280, 168);
const pol = P.pol, sq3 = Math.sqrt(3);
P.circle(1, { color: C.grid, width: 2.5, dash: "4 8" });
const Va = [1, 0], Vb = pol(1, -120), Vc = pol(1, 120), Vab = [1.5, sq3 / 2];
P.vec(Vc, { color: C.c, width: 5 }); P.vec(Vb, { color: C.b, width: 5 }); P.vec(Va, { color: C.a, width: 5 });
P.vec([-Vb[0], -Vb[1]], { color: C.b, width: 3.5, dash: "9 7" }, Va);
P.vec(Vab, { color: C.navy, width: 7, head: 26 });
P.arc(0.42, 0, 30, { color: C.slate, width: 2.5 });
P.label(pol(0.56, 15), "30°", { size: 24 });
P.label([1.08, -0.1], "$V_a$", { color: C.a, size: 32, anchor: "l" });
P.label(pol(1.16, -120), "$V_b$", { color: C.b, size: 32 });
P.label(pol(1.16, 120), "$V_c$", { color: C.c, size: 32 });
P.label([1.34, 0.3], "$-V_b$", { color: C.b, size: 26, anchor: "l" });
P.label([0.95, 1.06], "$V_{ab} = \\sqrt{3}\\,\\angle 30^\\circ$", { color: C.navy, size: 30, anchor: "b", weight: 700 });
F.done();
