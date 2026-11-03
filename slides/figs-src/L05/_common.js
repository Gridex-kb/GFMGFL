// 5강 공통: 기준 설비 값과 전류루프 전달함수 (pu). Kp = ωcc·Lf/ωb, Ki = Kp·ωcc/5, 지연 Td = 1.5 Ts
const PR = { Lf: 0.2, Rf: 0.005, fcc: 800, fsw: 5000, wb: 2 * Math.PI * 60, Vmax: 1.303, Imax: 1.2 };
PR.Ts = 1 / (2 * PR.fsw); PR.Td = 1.5 * PR.Ts; PR.wcc = 2 * Math.PI * PR.fcc;
PR.Kp = PR.wcc * PR.Lf / PR.wb; PR.Ki = PR.Kp * PR.wcc / 5;
const cx = (re, im = 0) => ({ re, im });
const cmul = (a, b) => cx(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
const cdiv = (a, b) => { const d = b.re * b.re + b.im * b.im; return cx((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d); };
const cabs = (a) => Math.hypot(a.re, a.im), carg = (a) => Math.atan2(a.im, a.re);
/* 개루프 L(jω) = (Kp + Ki/jω)·e^{-jωTd}·ωb/(jωLf + Rf·ωb) — 위상은 연속(언래핑) 도 단위 */
function openLoop(f, withDelay = true) {
  const w = 2 * Math.PI * f;
  const pi = cx(PR.Kp, -PR.Ki / w), plant = cdiv(cx(PR.wb / PR.Lf), cx(PR.Rf * PR.wb / PR.Lf, w));
  const L = cmul(pi, plant);
  const mag = 20 * Math.log10(cabs(L));
  let ph = carg(L) * 180 / Math.PI; if (ph > 0) ph -= 360;
  if (withDelay) ph -= w * PR.Td * 180 / Math.PI;
  return { mag, ph };
}
function crossover(withDelay = true) {
  let lo = 100, hi = 3000;
  for (let k = 0; k < 60; k++) { const m = Math.sqrt(lo * hi); if (openLoop(m, withDelay).mag > 0) lo = m; else hi = m; }
  const f = Math.sqrt(lo * hi); return { f, pm: 180 + openLoop(f, withDelay).ph };
}
