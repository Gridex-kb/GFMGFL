// 전류원 등가: PLL이 d축을 전압 벡터에 맞추면 i_d* = P*/v_d, i_q* = −Q*/v_d. Q > 0 이면 전류가 전압보다 뒤진다
const F = Fig(680, 560), C = FC, P = F.plane(150, 300, 300);
P.axis(0, 1.5, "$d$", { color: C.axis, width: 2.5, size: 28, back: 0.3 });
P.axis(90, 0.75, "$q$", { color: C.axis, width: 2.5, size: 28, back: 0.7 });
P.vec([1.0, 0], { color: C.orange, width: 6, head: 24 });
P.label([0.55, 0.09], "$v = v_d$ (PLL 정렬, $v_q = 0$)", { size: 22, color: C.orange, weight: 700 });
const id = 0.84, iq = -0.32;
P.vec([id, iq], { color: C.blue, width: 6, head: 24 });
P.vec([id, 0], { color: C.blue, width: 2.5, dash: "8 7", head: 10 });
P.vec([0, iq], { color: C.blue, width: 2.5, dash: "8 7", head: 10 }, [id, 0]);
P.label([0.56, -0.27], "$i_d^* = P^*/v_d$", { anchor: "t", size: 22, color: C.blue });
P.label([id + 0.05, iq / 2], "$i_q^* = -Q^*/v_d$", { anchor: "l", size: 22, color: C.blue });
P.label([0.6, iq - 0.1], "$i = i_d^* + j\\,i_q^*$", { anchor: "t", size: 26, color: C.blue, weight: 700 });
P.arc(0.3, -21, 0, { color: C.teal, width: 3, arrow: true });
P.label([0.25, -0.14], "뒤짐 → $Q > 0$", { anchor: "tr", size: 20, color: C.teal, weight: 700 });
F.label(340, 548, "느린 시간대: $i \\approx (i_d^* + j i_q^*)\\,e^{j\\theta_c}$, PLL 각에 붙은 전류원", { anchor: "b", size: 21, color: C.navy, weight: 700 });
F.done();
