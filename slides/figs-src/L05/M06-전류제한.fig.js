// 원형 전류 제한 1.2 pu, 세 가지 우선순위: GFL 정상(유효 우선), GFL FRT(무효 우선 ir = 0.95·1.2), GFM(방향 유지 축소)
const F = Fig(1500, 560), C = FC, R = 112, Imax = PR.Imax, ir = 0.95 * Imax;
const panel = (cxp, title, col, req, lim, note) => {
  const P = F.plane(cxp, 320, R);
  P.axis(0, 1.62, "$i_d$", { color: C.axis, width: 2.5, size: 26, back: 1.55 });
  P.axis(90, 1.62, "$i_r$", { color: C.axis, width: 2.5, size: 26, back: 1.55 });
  P.circle(Imax, { color: C.muted, width: 3, dash: "10 8" });
  P.label([Imax * 0.72, -Imax * 0.8], "1.2 pu", { size: 22, color: C.muted });
  P.vec(req, { color: col, width: 3, dash: "8 7", head: 14 });
  F.circle(...P.xy(req), 11, { color: col, width: 4, fill: "#ffffff" });
  P.vec(lim, { color: col, width: 5, head: 20 });
  F.dot(...P.xy(lim), { r: 11, color: col });
  F.arrow(...P.xy(req), ...P.xy(lim), { color: col, width: 3, head: 14, dash: "4 6" });
  F.label(cxp, 46, title, { size: 30, color: col, weight: 800 });
  F.label(cxp, 86, note, { size: 22, color: C.slate });
};
panel(260, "GFL 정상 운전: 유효 우선", C.blue, [1.1, 0.8], [1.1, Math.sqrt(Imax ** 2 - 1.1 ** 2)], "$i_d$를 지키고 남는 만큼 $i_r$");
panel(750, "GFL 저전압(FRT): 무효 우선", C.orange, [0.7, ir], [Math.sqrt(Imax ** 2 - ir ** 2), ir], "$i_r$ = 0.95 × 1.2 고정, 남는 만큼 $i_d$");
panel(1240, "GFM: 방향 유지", C.teal, [1.3, -0.6], [1.3 * Imax / Math.hypot(1.3, 0.6), -0.6 * Imax / Math.hypot(1.3, 0.6)], "가상 어드미턴스 전류의 크기만 축소");
F.label(1490, 548, "빈 원: 외부 루프 지령 · 찬 원: 제한 후 지령 · $i_r = -i_q$ (+Q)", { anchor: "br", size: 22, color: C.muted });
F.done();
