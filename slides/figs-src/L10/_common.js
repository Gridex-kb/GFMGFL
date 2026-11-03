// 10강 공통: 외란 구간 음영, 범례, 로그 시간축 보조
const shade = (F, A, x0, x1) => F.rect(A.x(x0), A.box[1], A.x(x1) - A.x(x0), A.box[3], { fill: "#dfe8f2", opacity: 0.4 });
const legend = (F, x, y, items, size = 22) => items.forEach(([txt, col, dash], k) => {
  const yy = y + k * (size + 14);
  F.line(x, yy, x + 44, yy, { color: col, width: 4, dash: dash || "" });
  F.label(x + 56, yy, txt, { anchor: "l", size, color: col, weight: 700 });
});
