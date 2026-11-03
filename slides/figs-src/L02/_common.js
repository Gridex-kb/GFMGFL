// 2강 공통: 2레벨 VSC 회로도와 전압 벡터 육각형
const VDC = 2.256, R6 = (2 / 3) * VDC, RIN = VDC / Math.sqrt(3);
const STATES = [["100", 0], ["110", 60], ["010", 120], ["011", 180], ["001", 240], ["101", 300]];

/* 2레벨 VSC + Y 부하. st = "110" 처럼 주면 스위치 ON/OFF 표시와 극전압 라벨을 붙인다 */
function drawVSC(F, st, o = {}) {
  const C = FC, yP = 90, yN = 510, ym = 300, xdc = 150, legs = [340, 540, 740], ph = ["a", "b", "c"];
  // DC 링크: 커패시터 2개 직렬, 중점 0
  F.wire([[xdc, yP], [xdc, 180]]); F.cap(xdc, 195); F.wire([[xdc, 210], [xdc, 390]]); F.cap(xdc, 405); F.wire([[xdc, 420], [xdc, yN]]);
  F.node(xdc, ym); F.label(xdc - 18, ym, "$0$", { anchor: "r", size: 30, color: C.navy });
  F.label(xdc - 44, 195, "$\\tfrac{V_{dc}}{2}$", { anchor: "r", size: 28, color: C.slate });
  F.label(xdc - 44, 405, "$\\tfrac{V_{dc}}{2}$", { anchor: "r", size: 28, color: C.slate });
  F.wire([[xdc, yP], [legs[2], yP]]); F.wire([[xdc, yN], [legs[2], yN]]);
  F.label(xdc - 16, yP, "$P$", { anchor: "r", size: 30, color: C.navy, weight: 700 });
  F.label(xdc - 16, yN, "$N$", { anchor: "r", size: 30, color: C.navy, weight: 700 });
  legs.forEach((x, k) => {
    F.node(x, yP); F.node(x, yN);
    const s = st ? st[k] === "1" : undefined;
    F.igbt(x, yP, ym, { on: st ? s : undefined, label: `$S_${ph[k]}$`, lsize: 26 });
    F.igbt(x, ym, yN, { on: st ? !s : undefined, label: `$\\bar S_${ph[k]}$`, lsize: 26 });
    F.node(x, ym);
  });
  // 출력: 중점에서 오른쪽으로 나와 아래로 내려가 부하로
  const xl = [o.xload || 950, (o.xload || 950) + 85, (o.xload || 950) + 170], yo = [640, 610, 580];
  const yTop = 200, yInd = [430, 320];
  legs.forEach((x, k) => {
    const xt = x + 78;
    F.wire([[x, ym], [xt, ym], [xt, yo[k]], [xl[2 - k], yo[k]], [xl[2 - k], yInd[0]]]);
    F.label(xt + 10, ym - 16, `$${ph[k]}$`, { anchor: "bl", size: 30, color: C.navy, weight: 700 });
    F.node(xt, ym, { r: 6 });
    // 부하 가지 (인덕터 + 저항 생략: 인덕터만)
    const xb = xl[2 - k];
    F.inductorV(xb, yInd[0], yInd[1]);
    F.wire([[xb, yInd[1]], [xb, yTop]]);
    if (st) {
      const v = st[k] === "1" ? "+" : "−";
      F.label(xt + 10, ym + 18, `${v}1.128`, { anchor: "tl", size: 22, color: st[k] === "1" ? C.blue : C.orange, weight: 700 });
    }
  });
  F.wire([[xl[0], yTop], [xl[2], yTop]]); F.node(xl[1], yTop);
  F.label(xl[1], yTop - 18, "$n$", { anchor: "b", size: 30, color: C.navy, weight: 700 });
  if (o.vn0) {
    F.path(`M${xdc},${ym} C ${xdc + 60},${ym - 260} ${xl[1] - 200},${yTop - 120} ${xl[1]},${yTop - 50}`, { color: C.teal, width: 2.5, dash: "8 7" });
    F.label(470, 92 - 40, "$v_{n0}$ : 부하 중성점 − DC 중점", { anchor: "b", size: 24, color: C.teal });
  }
}

/* 수직 인덕터: (x, y1) 아래 → (x, y2) 위 */
function patchInductorV(F) {
  F.inductorV = (x, y1, y2, s = {}) => {
    const n = 4, L = y2 - y1, r = L / (2 * n);
    let d = `M${x},${y1}`;
    for (let i = 0; i < n; i++) d += ` a${Math.abs(r)},${Math.abs(r)} 0 0 ${r < 0 ? 1 : 0} 0,${2 * r}`;
    F.path(d, { color: s.color || FC.navy, width: 3.5 });
  };
}

/* 전압 벡터 육각형. o.hi = "110" 강조, o.circle 내접원, o.labels 상태 라벨 */
function hexagon(F, P, o = {}) {
  const C = FC;
  P.axis(0, 1.95, "$\\alpha$", { color: C.axis, back: 1.95, size: 30, width: 2 });
  P.axis(90, 1.75, "$\\beta$", { color: C.axis, back: 1.75, size: 30, width: 2 });
  const pts = STATES.map(([, d]) => P.xy(P.pol(R6, d)));
  F.poly(pts.concat([pts[0]]), { color: C.navy, width: 3.5, fill: o.fill || "rgba(36,99,200,0.06)" });
  if (o.circle) {
    P.circle(RIN, { color: C.teal, width: 3, dash: "10 8" });
  }
  STATES.forEach(([s, d], k) => {
    const hi = o.hi === s;
    if (o.arrows !== false) P.vec(P.pol(R6, d), { color: hi ? C.orange : C.navy, width: hi ? 7 : 3.5, head: hi ? 26 : 18, opacity: o.hi && !hi ? 0.45 : 1 });
    if (o.labels !== false) {
      const lp = P.pol(R6 + 0.36, d);
      P.label(lp, `$\\vec V_{${k + 1}}$<br><span style="font-size:0.8em">${s}</span>`, { size: 26, color: hi ? C.orange : C.navy, weight: hi ? 700 : 500 });
    }
  });
  F.dot(P.cx, P.cy, { r: 9, color: C.navy });
  if (o.zero !== false) P.label(P.pol(0.62, 210), "$\\vec V_0, \\vec V_7$", { anchor: "c", size: 24, color: C.navy, bg: "#ffffff" });
}
