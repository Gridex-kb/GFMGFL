// 컨버터 전압 → 변압기 전류 이득: L 필터, LCL(Rd=0), LCL(Rd=2), 강한 계통
const F = Fig(1080, 600), C = FC, lg = Math.log10;
const A = F.frame([110, 60, 900, 430], [1, 4.3], [-80, 45]).axes({
  xticks: [1, 2, 3, 4], yticks: [-80, -60, -40, -20, 0, 20, 40],
  xfmt: (v) => ({ 1: "10", 2: "100", 3: "1k", 4: "10k" })[v], xlabel: "주파수 [Hz]", ylabel: "|변압기 전류 / 컨버터 전압| [dB]" });
[2, 3, 4].forEach((d) => [2, 3, 4, 5, 6, 7, 8, 9].forEach((m) => { const x = d - 1 + lg(m); if (x < 4.3) F.line(A.x(x), 60, A.x(x), 490, { color: "#f1f4f8", width: 1.5 }); }));
const fr = fres(PR.Lt);
A.vline(lg(fr)); A.vline(lg(PR.fsw));
A.fn((x) => lGain(10 ** x), 800, { color: C.muted, width: 4, dash: "12 8" });
A.fn((x) => lclGain(10 ** x, 0), 1600, { color: C.orange, width: 4 });
A.fn((x) => lclGain(10 ** x, PR.Rd), 1600, { color: C.blue, width: 5 });
A.label(lg(fr) - 0.03, 38, `공진 ${fr.toFixed(0)} Hz`, { anchor: "r", size: 24, color: C.slate, bg: "#ffffff" });
A.label(lg(PR.fsw) - 0.03, -74, "스위칭 5 kHz", { anchor: "r", size: 24, color: C.slate, bg: "#ffffff" });
const at = (g) => g(PR.fsw);
[[lGain, C.muted, "L 필터"], [(f) => lclGain(f, PR.Rd), C.blue, "LCL Rd 2"], [(f) => lclGain(f, 0), C.orange, "LCL Rd 0"]].forEach(([g, col, n]) => {
  const v = at(g); F.dot(A.x(lg(PR.fsw)), A.y(v), { r: 8, color: col });
  A.label(lg(PR.fsw) + 0.04, v, `${v.toFixed(0)} dB`, { anchor: "l", size: 24, color: col, weight: 700 });
});
A.label(3.42, -15, "L 필터 (0.3 pu)", { anchor: "bl", size: 24, color: C.muted, weight: 700 });
A.label(2.7, 22, "LCL, $R_d = 0$", { anchor: "r", size: 24, color: C.orange, weight: 700 });
A.label(2.0, -34, "LCL, $R_d = 2$ (모델)", { anchor: "l", size: 24, color: C.blue, weight: 700 });
F.done();
