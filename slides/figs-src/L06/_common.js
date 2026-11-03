// 6강 공통: 블록선도 보조 함수
const blkRow = (F, x, y, w, h, t, s = {}) => F.block(x, y, w, h, t, Object.assign({ size: 26 }, s));
const harrow = (F, x1, x2, y, s = {}) => F.arrow(x1, y, x2, y, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
const varrow = (F, x, y1, y2, s = {}) => F.arrow(x, y1, x, y2, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
