// 반송파 꼭짓점 샘플링(10 kHz)과 1.5 Ts 지연: 샘플 1에서 계산한 지령은 샘플 2부터 Ts 동안 유지
const F = Fig(1300, 600), C = FC, Ts = 100;
const car = (t) => { const ph = (t / 200) % 1; return ph < 0.5 ? 4 * ph - 1 : 3 - 4 * ph; };
const A = F.frame([120, 50, 1060, 230], [0, 400], [-1.25, 1.25]).axes({ xticks: [0, 100, 200, 300, 400], yticks: [-1, 0, 1], tick: 22, xfmt: () => "" });
A.fn(car, 800, { color: C.navy, width: 4 });
[0, 1, 2, 3, 4].forEach((k) => { A.vline(k * Ts, { color: C.axis, width: 2, dash: "4 6" }); F.dot(A.x(k * Ts), A.y(car(k * Ts)), { r: 10, color: C.orange }); A.label(k * Ts, 1.12, `샘플 ${k}`, { anchor: "b", size: 22, color: C.orange, weight: 700 }); });
F.label(1190, A.y(0), "반송파", { anchor: "l", size: 24, color: C.navy });
// 아래: 타임라인
const B = F.frame([120, 340, 1060, 160], [0, 400], [0, 1]);
F.line(B.x(0), 500, B.x(400), 500, { color: C.axis, width: 2.5 });
[0, 100, 200, 300, 400].forEach((t) => F.label(B.x(t), 512, `${t} µs`, { anchor: "t", size: 22, color: C.muted }));
F.rect(B.x(100), 360, B.x(200) - B.x(100), 56, { r: 8, fill: "#fde3d6" });
F.label(B.x(150), 388, "계산 (샘플 1의 측정)", { size: 22, color: C.orange, weight: 700 });
F.rect(B.x(200), 430, B.x(300) - B.x(200), 56, { r: 8, fill: "#d9e6fa" });
F.label(B.x(250), 458, "PWM 적용 (영차 홀드)", { size: 22, color: C.blue, weight: 700 });
F.dot(B.x(250), 500, { r: 9, color: C.blue });
F.arrow(B.x(100), 548, B.x(250), 548, { color: C.navy, width: 3.5, head: 16, both: true });
F.label(B.x(175), 556, "$T_d = 1.5\\,T_s = 150\\ \\mu s$", { anchor: "t", size: 26, color: C.navy, weight: 700 });
F.label(B.x(250) + 16, 494, "무게중심", { anchor: "l", size: 20, color: C.blue });
F.done();
