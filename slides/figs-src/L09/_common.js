// 9강 공통: 블록선도 보조, 고장 구간 음영
const blkRow = (F, x, y, w, h, t, s = {}) => F.block(x, y, w, h, t, Object.assign({ size: 26 }, s));
const harrow = (F, x1, x2, y, s = {}) => F.arrow(x1, y, x2, y, Object.assign({ color: FC.navy, width: 3.5, head: 16 }, s));
const shade = (F, A, x0, x1) => F.rect(A.x(x0), A.box[1], A.x(x1) - A.x(x0), A.box[3], { fill: "#dfe8f2", opacity: 0.4 });
