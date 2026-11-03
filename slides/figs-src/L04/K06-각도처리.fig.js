// 각도 처리: 측정은 샘플 시점 θk로 변환, 출력은 θk + 1.5ωTs로 되돌린다 (각도는 보기 좋게 과장)
const F = Fig(680, 560), C = FC, P = F.plane(150, 470, 360);
P.axis(0, 1.32, "$\\alpha$", { color: C.axis, size: 30, width: 2 });
P.axis(90, 1.0, "$\\beta$", { color: C.axis, size: 30, width: 2 });
const thk = 25, dT = 14;
P.vec(P.pol(1.0, thk), { color: C.blue, width: 6, head: 24 });
P.vec(P.pol(1.0, thk + 1.5 * dT), { color: C.orange, width: 6, head: 24 });
P.vec(P.pol(0.85, thk + dT * 0.6), { color: C.muted, width: 3, dash: "8 7" });
P.arc(0.32, 0, thk, { color: C.blue, width: 3 }); P.label(P.pol(0.42, thk / 2), "$\\theta_k$", { size: 28, color: C.blue });
P.arc(1.06, thk, thk + 1.5 * dT, { color: C.orange, width: 3, arrow: true });
P.label(P.pol(1.2, thk + 0.75 * dT), "$1.5\\,\\omega T_s$", { size: 26, color: C.orange, weight: 700 });
P.label(P.pol(1.02, thk - 4), "측정 변환: $\\theta_k$", { anchor: "l", size: 24, color: C.blue, weight: 700 });
P.label(P.pol(1.0, thk + 1.5 * dT + 6), "출력: $\\theta_k + 1.5\\,\\omega T_s$", { anchor: "r", size: 24, color: C.orange, weight: 700 });
P.label(P.pol(0.5, thk + dT * 0.6 + 14), "연속 $\\theta(t)$ ✗", { anchor: "r", size: 22, color: C.muted });
F.label(670, 545, "각도는 보기 좋게 과장 (실제 $\\omega T_s$ = 2.16°)", { anchor: "br", size: 20, color: C.muted });
F.done();
