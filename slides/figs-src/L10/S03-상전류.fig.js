// T07 점프 직후 상전류 (스위칭 모델 2 µs 기록): GFL 은 PLL 이 따라갈 때까지 그대로, GFM 은 점프 순간부터 전류가 바뀐다
const F = Fig(1100, 730), C = FC, D = DATA, xl = [-5, 20], yl = [-1.3, 1.3];
const panel = (box, L, title, note, col, last) => {
  const A = F.frame(box, xl, yl).axes({ xticks: [-5, 0, 5, 10, 15, 20], yticks: [-1, 0, 1], tick: 22, xfmt: last ? undefined : () => "", xlabel: last ? "점프 후 시간 [ms]" : undefined, ylabel: `${L} 상전류 [pu]` });
  A.vline(0, { color: C.navy, width: 2.5, dash: "8 6" });
  A.plot(D[L].t_ms, D[L].ia, { color: C.blue, width: 2.5 });
  A.plot(D[L].t_ms, D[L].ib, { color: C.orange, width: 2.5 });
  A.plot(D[L].t_ms, D[L].ic, { color: C.green, width: 2.5 });
  F.label(895, A.y(0.9), title, { anchor: "l", size: 22, color: col, weight: 800 });
  F.label(895, A.y(0.0), note, { anchor: "l", size: 20, color: C.slate });
  return A;
};
const A = panel([120, 50, 760, 280], "GFL", "GFL: 한 주기<br>가까이 그대로", "PLL이 새 위상을<br>잰 뒤에야 전류<br>지령이 바뀐다<br>(10 ms +0.00 pu)", C.orange, false);
A.label(0.5, 1.2, "−20° 점프", { anchor: "l", size: 20, color: C.navy, weight: 700 });
panel([120, 370, 760, 280], "GFM", "GFM: 점프 순간<br>부터 바뀐다", "내부 전압 그대로,<br>계통만 튀니 회로<br>법칙으로 즉시<br>(10 ms +0.68 pu)", C.blue, true);
F.label(880, 20, "5 kHz 스위칭 리플이 보이는 2 µs 기록, 상 a·b·c", { anchor: "r", size: 20, color: C.muted });
F.done();
