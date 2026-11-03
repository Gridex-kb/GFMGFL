// 교차주파수 800 Hz에서 180° 위상 예산: 플랜트 적분 90° + 지연 43° + PI 영점 ≈10° → 위상여유 ≈35~37°
const F = Fig(1500, 330), C = FC, X0 = 60, W = 1380, s = W / 180;
const parts = [[90, "플랜트 (인덕터) 90°", "#c9d3df", C.navy], [43.2, "지연 43°", "#fbcdb8", C.orange], [10, "PI ≈10°", "#cfe8d2", C.green], [36.8, "위상여유 ≈35~37°", "#cfe0f8", C.blue]];
let x = X0;
parts.forEach(([v, t, fill, col]) => { F.rect(x, 80, v * s, 120, { fill, color: "#ffffff", width: 3 }); F.label(x + (v * s) / 2, 140, t, { size: 26, color: col, weight: 700 }); x += v * s; });
F.line(X0, 230, X0 + W, 230, { color: C.axis, width: 2.5 });
[0, 90, 133.2, 143.2, 180].forEach((v) => { F.line(X0 + v * s, 222, X0 + v * s, 238, { color: C.axis, width: 2.5 }); F.label(X0 + v * s, 246, `${v === 133.2 ? "133" : v === 143.2 ? "143" : v}°`, { anchor: "t", size: 22, color: C.muted }); });
F.label(X0, 40, "−180° 까지 쓸 수 있는 위상 (교차주파수 800 Hz)", { anchor: "l", size: 24, color: C.slate });
F.done();
