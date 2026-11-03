// 7강 공통: 블록선도 보조 함수와 P–δ 관계
const blkRow = (F, x, y, w, h, t, s = {}) => F.block(x, y, w, h, t, Object.assign({ size: 26 }, s));
const harrow = (F, x1, x2, y, s = {}) => F.arrow(x1, y, x2, y, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
const varrow = (F, x, y1, y2, s = {}) => F.arrow(x, y1, x, y2, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
const PR = { Xv: 0.3, Rv: 0.05, scr: 3, H: 4, D: 50, wb: 2 * Math.PI * 60, P0: 0.5 };
PR.X = PR.Xv + 1 / PR.scr; PR.d0 = Math.asin(PR.P0 * PR.X); PR.Ks = Math.cos(PR.d0) / PR.X;
const Pdelta = (deg) => Math.sin(deg * Math.PI / 180) / PR.X;
