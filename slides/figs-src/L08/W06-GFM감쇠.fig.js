// GFM 전력 루프 감쇠비 ζ와 고유주파수 vs SCR (선형 근사, H 4 s, D 50): Xv 0.3 / 0.1 / 0.03. 강계통일수록 ζ ↓, Xv가 하한을 만든다
const F = Fig(1100, 620), C = FC;
const A = F.frame([120, 60, 420, 440], [1, 20], [0, 0.6]).axes({ xticks: [1, 5, 10, 15, 20], yticks: [0, 0.2, 0.4, 0.6], tick: 22, xlabel: "SCR", ylabel: "감쇠비 ζ" });
const B = F.frame([640, 60, 420, 440], [1, 20], [0, 4]).axes({ xticks: [1, 5, 10, 15, 20], yticks: [0, 1, 2, 3, 4], tick: 22, xlabel: "SCR", ylabel: "고유주파수 [Hz]" });
[[0.3, C.blue, null, "X<b>v</b> = 0.3 (모델)"], [0.1, C.teal, "12 8", "X<b>v</b> = 0.1"], [0.03, C.orange, "4 6", "X<b>v</b> = 0.03"]].forEach(([xv, col, dash, lab], k) => {
  A.fn((s) => zetaOf(s, xv).zeta, 300, { color: col, width: 4, dash });
  B.fn((s) => zetaOf(s, xv).fn, 300, { color: col, width: 4, dash });
  if (k === 0) A.label(8, 0.36, lab, { anchor: "bl", size: 22, color: col, weight: 700 });
  else A.label(19.5, zetaOf(20, xv).zeta + (k === 2 ? -0.03 : 0.035), lab, { anchor: "r", size: 22, color: col, weight: 700 });
});
[3, 20].forEach((s) => { const z = zetaOf(s, 0.3).zeta; F.dot(A.x(s), A.y(z), { r: 8, color: C.blue }); A.label(s + (s === 3 ? 0.6 : -0.6), z + 0.05, `SCR ${s}: ζ ${z.toFixed(2)}`, { anchor: s === 3 ? "bl" : "br", size: 20, color: C.blue, weight: 700 }); });
F.dot(A.x(20), A.y(zetaOf(20, 0.03).zeta), { r: 8, color: C.orange });
F.label(560, 560, "H = 4 s, D = 50, K<b>s</b> ≈ 1/(X<b>v</b> + 1/SCR) · 전력 필터·전압 제어·내부 루프 무시: 절대값보다 경향", { anchor: "b", size: 21, color: C.muted });
F.done();
