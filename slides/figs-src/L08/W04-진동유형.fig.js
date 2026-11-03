// 진동의 두 유형: ① 동기화 상실형 (GFL 10 Hz, SCR 5 → 1.3, ~10 Hz 대진폭) ② 상호작용형 (GFL 50 Hz, SCR 5 → 1.5, ~90 Hz 소진폭). y축 범위가 크게 다르다
const F = Fig(1500, 630), C = FC, D = DATA;
const A = F.frame([120, 120, 560, 380], [-50, 600], [-0.6, 1.8]).axes({ xticks: [0, 200, 400, 600], yticks: [-0.5, 0, 0.5, 1.0, 1.5], tick: 22, xlabel: "SCR 전환 후 시간 [ms]", ylabel: "$P$ [pu]" });
A.plot(D.loss.t, D.loss.P, { color: C.orange, width: 3.5 });
A.vline(0);
F.label(400, 28, "① 동기화 상실형: PLL 10 Hz, SCR 5 → 1.3", { size: 26, color: C.orange, weight: 800 });
F.label(400, 60, "약 10 Hz, 대진폭 (±1 pu 가까이), PLL이 반복해서 미끄러진다", { size: 21, color: C.slate });
const B = F.frame([860, 120, 560, 380], [400, 460], [0.72, 0.88]).axes({ xticks: [400, 420, 440, 460], yticks: [0.75, 0.8, 0.85], tick: 22, xlabel: "SCR 전환 후 시간 [ms] (확대)", ylabel: "$P$ [pu]" });
B.plot(D.inter.t, D.inter.P, { color: C.teal, width: 3.5 });
F.label(1140, 28, "② 상호작용형: PLL 50 Hz, SCR 5 → 1.5", { size: 26, color: C.teal, weight: 800 });
F.label(1140, 60, `약 ${D.inter.f_osc.toFixed(0)} Hz, 소진폭 지속 진동 — 전류 루프·지연과 결합`, { size: 21, color: C.slate });
F.label(1420, 622, "두 그림의 y축 범위가 크게 다르다", { anchor: "br", size: 20, color: C.muted });
F.done();
