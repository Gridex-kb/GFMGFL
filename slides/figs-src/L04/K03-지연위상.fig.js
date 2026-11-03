// 150 µs 순수 지연 vs 1차 지연 근사: 위상(위)과 크기(아래)
const F = Fig(1100, 660), C = FC, Td = 150e-6, lg = Math.log10;
const xt = [1, 2, 3, Math.log10(5000)], xf = (v) => ({ 1: "10", 2: "100", 3: "1k" })[v] || (Math.abs(v - lg(5000)) < 1e-6 ? "5k" : "");
const A = F.frame([120, 70, 860, 300], [1, lg(5000)], [-270, 0]).axes({ xticks: xt, yticks: [-270, -180, -90, 0], tick: 22, xfmt: () => "", ylabel: "위상 [°]" });
A.fn((x) => -360 * 10 ** x * Td, 600, { color: C.orange, width: 5 });
A.fn((x) => -Math.atan(2 * Math.PI * 10 ** x * Td) * 180 / Math.PI, 600, { color: C.blue, width: 5, dash: "14 9" });
A.vline(lg(800));
F.dot(A.x(lg(800)), A.y(-43.2), { r: 9, color: C.orange }); F.dot(A.x(lg(800)), A.y(-37.0), { r: 9, color: C.blue });
A.label(lg(800) - 0.04, -60, "800 Hz: −43°", { anchor: "tr", size: 24, color: C.orange, weight: 700 });
A.label(lg(800) + 0.04, -28, "−37°", { anchor: "bl", size: 24, color: C.blue, weight: 700 });
const B = F.frame([120, 430, 860, 140], [1, lg(5000)], [-8, 1]).axes({ xticks: xt, yticks: [-6, -3, 0], tick: 22, xfmt: xf, xlabel: "주파수 [Hz]", ylabel: "" });
B.fn(() => 0, 4, { color: C.orange, width: 5 });
B.fn((x) => -10 * lg(1 + (2 * Math.PI * 10 ** x * Td) ** 2), 600, { color: C.blue, width: 5, dash: "14 9" });
B.vline(lg(800));
F.label(130, 418, "크기 [dB]", { anchor: "bl", size: 22, color: C.slate });
F.label(1000, 150, "순수 지연<br>$e^{-1.5sT_s}$", { anchor: "l", size: 24, color: C.orange, weight: 700 });
F.label(1000, 270, "1차 근사<br>$\\frac{1}{1+sT_d}$", { anchor: "l", size: 24, color: C.blue, weight: 700 });
F.done();
