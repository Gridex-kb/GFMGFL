// 8강 공통: 블록선도 보조, SCR–감쇠비 근사, PLL 유효 이득
const blkRow = (F, x, y, w, h, t, s = {}) => F.block(x, y, w, h, t, Object.assign({ size: 26 }, s));
const harrow = (F, x1, x2, y, s = {}) => F.arrow(x1, y, x2, y, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
const varrow = (F, x, y1, y2, s = {}) => F.arrow(x, y1, x, y2, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
const WB = 2 * Math.PI * 60, H_VSM = 4, D_VSM = 50;
const zetaOf = (scr, Xv) => { const Ks = 1 / (Xv + 1 / scr), wn = Math.sqrt(WB * Ks / (2 * H_VSM)); return { zeta: D_VSM / (4 * H_VSM * wn), fn: wn / (2 * Math.PI) }; };
/* GFL 정적 운전점: sin δ = X_g·i_d / V_g, PLL 유효 이득 = cos δ */
const pllGain = (scr, id = 0.8) => { const s = Math.min(1, id / scr); return { delta: Math.asin(s) * 180 / Math.PI, cos: Math.sqrt(Math.max(0, 1 - s * s)) }; };
