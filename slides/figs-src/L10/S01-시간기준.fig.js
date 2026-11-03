// 시험 판정의 시간 기준을 로그 시간축 하나에 모은 개념도 (시뮬레이션 결과 아님)
const F = Fig(1500, 600), C = FC;
const X0 = 130, X1 = 1400, T0 = 1, T1 = 3000, Y = 330;
const px = (ms) => X0 + (X1 - X0) * Math.log10(ms / T0) / Math.log10(T1 / T0);
// 구간 음영: 기본파 한 주기(≤ 16.7 ms), 관성 시간대(≥ 100 ms)
F.rect(px(1), Y - 175, px(16.7) - px(1), 350, { fill: "#d9e6fa", opacity: 0.55 });
F.rect(px(100), Y - 175, px(3000) - px(100), 350, { fill: "#e3f1dc", opacity: 0.6 });
F.label((px(1) + px(16.7)) / 2, Y - 215, "기본파 한 주기 안 (≤ 16.7 ms): 측정·PLL 없이 <b>전압원 거동</b>으로만 응답 가능", { size: 22, color: C.blue, weight: 700 });
F.label((px(100) + px(3000)) / 2, Y - 215, "관성 시간대: 지속·회복", { size: 22, color: C.green, weight: 700 });
F.label((px(16.7) + px(100)) / 2, Y - 215, "제어 응답", { size: 22, color: C.slate, weight: 700 });
// 축
F.arrow(X0 - 20, Y, X1 + 40, Y, { color: C.axis, width: 3, head: 16 });
[[1, "1 ms"], [10, "10"], [100, "100"], [1000, "1 s"]].forEach(([t, s]) => {
  F.line(px(t), Y - 10, px(t), Y + 10, { color: C.axis, width: 2.5 });
  F.label(px(t), Y - 28, s, { size: 20, color: C.muted });
});
F.label(X1 + 40, Y - 28, "외란 후 시간 (로그)", { anchor: "r", size: 20, color: C.muted });
// 기준 표식: [ms, 라벨, 위(−1)/아래(+1), 단, 색]
const marks = [
  [5, "GB GC0137<br>자연 응답 5 ms<br>(초기 피크 50 %)", -1, 1, C.blue],
  [10, "ENTSO-E TG GFC<br>10 ms 유효전류<br>≥ 0.25 pu", 1, 1, C.blue],
  [15, "ERCOT AGS #7<br>90 % 도달 15 ms", -1, 2, C.blue],
  [30, "ENTSO-E<br>무효전류 90 %<br>30 ms", 1, 2, C.teal],
  [140, "한국 연계기준안<br>2.0 pu 지속<br>≥ 140 ms", 1, 1, C.green],
  [300, "동기원 상실<br>주파수 판정 시작<br>0.3 s", -1, 1, C.green],
  [1000, "고장 후 회복·<br>전압 판정 1 s", 1, 2, C.green],
];
marks.forEach(([t, txt, side, row, col]) => {
  const x = px(t), yy = Y + side * (row === 1 ? 58 : 128);
  F.line(x, Y, x, yy + (side < 0 ? 8 : -8), { color: col, width: 3 });
  F.dot(x, Y, { r: 9, color: col });
  F.label(x, yy, txt, { anchor: side < 0 ? "b" : "t", size: 20, color: col, weight: 700 });
});
F.done();
