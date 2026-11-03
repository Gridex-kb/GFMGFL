// 3강 공통: 기준 설비 값과 LCL 전달함수 (pu, h = f/60)
const PR = { Lf: 0.2, Rf: 0.005, Cf: 0.05, Rd: 2.0, Lt: 0.1, Rt: 0.005, fsw: 5000, f0: 60 };
const cx = (re, im = 0) => ({ re, im });
const cadd = (a, b) => cx(a.re + b.re, a.im + b.im);
const cmul = (a, b) => cx(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
const cdiv = (a, b) => { const d = b.re * b.re + b.im * b.im; return cx((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d); };
const cabs = (a) => Math.hypot(a.re, a.im);
function lclGain(f, Rd, Lg = PR.Lt) {
  const h = f / PR.f0, Zf = cx(PR.Rf, h * PR.Lf), Zg = cx(PR.Rt, h * Lg), Zc = cadd(cx(Rd), cdiv(cx(1), cx(0, h * PR.Cf)));
  const par = cdiv(cmul(Zc, Zg), cadd(Zc, Zg)), iF = cdiv(cx(1), cadd(Zf, par));
  return 20 * Math.log10(cabs(cmul(iF, cdiv(Zc, cadd(Zc, Zg)))));
}
function lGain(f) { const h = f / PR.f0; return 20 * Math.log10(1 / cabs(cx(PR.Rf + PR.Rt, h * (PR.Lf + PR.Lt)))); }
const fres = (Lg) => PR.f0 * Math.sqrt((PR.Lf + Lg) / (PR.Lf * Lg * PR.Cf));
/* 수직 저항(지그재그): (x, y1) → (x, y2) */
function resV(F, x, y1, y2, col) {
  const n = 6, st = (y2 - y1) / n, a = 12, pts = [[x, y1]];
  for (let i = 0; i < n; i++) pts.push([x + (i % 2 ? a : -a), y1 + st * (i + 0.5)]);
  pts.push([x, y2]); F.poly(pts, { color: col || FC.navy, width: 3.5 });
}
