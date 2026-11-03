// anti-windup: 포화 중 가상 전류 i_v 의 미분에서 바깥 방향(반지름) 성분만 지운다. 접선 성분은 남아 원 위에서 움직인다
const F = Fig(680, 560), C = FC, P = F.plane(300, 300, 150), Imax = 1.2;
P.axis(0, 1.7, "$i_d$", { color: C.axis, width: 2.5, size: 26, back: 1.7 });
P.axis(90, 1.6, "$i_q$", { color: C.axis, width: 2.5, size: 26, back: 1.6 });
P.circle(Imax, { color: C.muted, width: 3, dash: "10 8" });
P.label([-0.3, 1.38], "|i| = 1.2", { size: 22, color: C.muted });
const ang = 35 * Math.PI / 180, iv = [Imax * Math.cos(ang), Imax * Math.sin(ang)];
P.vec(iv, { color: C.blue, width: 6, head: 24 });
P.label([iv[0] * 0.45, iv[1] * 0.45 - 0.22], "$i_v$ (포화)", { size: 24, color: C.blue, weight: 700 });
// 미분 벡터: 반지름 성분(주황, 지움) + 접선 성분(초록, 남김)
const rhat = [Math.cos(ang), Math.sin(ang)], that = [-Math.sin(ang), Math.cos(ang)];
const dr = 0.55, dt = 0.45;
const di = [dr * rhat[0] + dt * that[0], dr * rhat[1] + dt * that[1]];
P.vec(di, { color: C.muted, width: 3, dash: "8 7", head: 14 }, iv);
P.vec([dr * rhat[0], dr * rhat[1]], { color: C.orange, width: 4, head: 16 }, iv);
P.vec([dt * that[0], dt * that[1]], { color: C.green, width: 5, head: 18 }, iv);
P.label([iv[0] + di[0] + 0.08, iv[1] + di[1] + 0.1], "$\\dot i_v$ (원래)", { anchor: "l", size: 22, color: C.muted });
P.label([iv[0] + dr * rhat[0] + 0.1, iv[1] + dr * rhat[1] - 0.12], "반지름 성분<br>→ 지운다", { anchor: "l", size: 22, color: C.orange, weight: 700 });
P.label([iv[0] + dt * that[0] - 0.1, iv[1] + dt * that[1] + 0.12], "접선 성분<br>→ 남긴다", { anchor: "r", size: 22, color: C.green, weight: 700 });
F.label(340, 548, "안쪽으로 줄어드는 변화는 그대로 → 고장이 끝나면 곧바로 원 안으로", { anchor: "b", size: 21, color: C.navy, weight: 700 });
F.done();
