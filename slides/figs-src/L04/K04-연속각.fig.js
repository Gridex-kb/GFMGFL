// 위: 홀드된 전압을 연속 θ로 보면 vq가 톱니(평균 −ωTs/2). 아래: EMT GFL의 PLL 주파수 (5 ms 이동평균)
const F = Fig(1200, 700), C = FC, D = DATA, wTs = 2 * Math.PI * 60 * 100e-6;
const A = F.frame([130, 70, 860, 220], [0, 500], [-0.045, 0.012]).axes({ xticks: [0, 100, 200, 300, 400, 500], yticks: [-0.04, -0.02, 0], tick: 22, xlabel: "시간 [µs]", ylabel: "$v_q$ [pu]" });
A.fn((t) => -Math.sin(wTs * ((t % 100) / 100)), 2000, { color: C.orange, width: 4 });
A.fn(() => 0, 4, { color: C.blue, width: 4 });
A.hline(-wTs / 2, { color: C.orange, width: 2.5 });
F.label(1000, A.y(-0.025), "연속 θ<br>평균 $-\\omega T_s/2$", { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(1000, A.y(0.002), "샘플 시점 θ", { anchor: "l", size: 22, color: C.blue, weight: 700 });
const B = F.frame([130, 400, 860, 200], [0, 95], [59.6, 61.8]).axes({ xticks: [0, 20, 40, 60, 80], yticks: [60, 61], tick: 22, xlabel: "시간 [ms]", ylabel: "PLL 주파수 [Hz]" });
B.plot(D.cont.t, D.cont.f, { color: C.orange, width: 4 }); B.plot(D.hold.t, D.hold.f, { color: C.blue, width: 4 });
F.label(1000, B.y(D.cont.mean), `연속 θ<br>${D.cont.mean.toFixed(2)} Hz`, { anchor: "l", size: 22, color: C.orange, weight: 700 });
F.label(1000, B.y(D.hold.mean) + 10, `샘플 시점 θ<br>+ 지연 보상<br>${D.hold.mean.toFixed(2)} Hz`, { anchor: "l", size: 22, color: C.blue, weight: 700 });
F.done();
