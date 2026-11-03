// 계통이 약할수록 LCL 공진 주파수가 내려와 전류 제어 대역 800 Hz에 다가간다
const F = Fig(780, 520), C = FC;
const A = F.frame([110, 50, 620, 360], [1, 10], [500, 1150]).axes({
  xticks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], yticks: [600, 800, 1000], xlabel: "SCR", ylabel: "공진 주파수 [Hz]" });
A.hline(fres(PR.Lt), { color: C.muted }); A.label(9.9, fres(PR.Lt) + 12, "강한 계통 1039 Hz", { anchor: "br", size: 22, color: C.muted });
A.hline(800, { color: C.orange, dash: "none", width: 3 }); A.label(9.9, 790, "전류 제어 대역 800 Hz", { anchor: "tr", size: 22, color: C.orange, weight: 700 });
A.fn((s) => fres(PR.Lt + 1 / s), 400, { color: C.blue, width: 5 });
[[2, "693", 0.15, "tl", 650], [3, "725", 0.15, "tl", 707]].forEach(([s, t, dx, an, yy]) => { F.dot(A.x(s), A.y(fres(PR.Lt + 1 / s)), { r: 9, color: C.navy }); A.label(s + dx, yy, `SCR ${s}: ${t} Hz`, { anchor: an, size: 22, color: C.navy, weight: 700 }); });
A.label(5.2, 930, "$L_g = L_t + 1/\\mathrm{SCR}$", { size: 26, color: C.blue });
F.done();
