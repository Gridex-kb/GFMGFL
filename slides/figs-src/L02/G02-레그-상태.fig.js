// 레그 하나 = 스위칭 함수 하나: S=1이면 출력이 P에, S=0이면 N에 붙는다
const F = Fig(980, 470), C = FC;
function leg(x0, S) {
  const yP = 70, yN = 380, xc = x0 + 70, xs = x0 + 230, ym = (yP + yN) / 2;
  F.wire([[xc, yP], [xc, 150]]); F.cap(xc, 162); F.wire([[xc, 174], [xc, 336]]); F.cap(xc, 348); F.wire([[xc, 360], [xc, yN]]);
  F.node(xc, ym); F.label(xc - 16, ym, "$0$", { anchor: "r", size: 28, color: C.navy });
  F.wire([[xc, yP], [xs + 34, yP]]); F.wire([[xc, yN], [xs + 34, yN]]);
  F.label(xc - 14, yP, "$P$", { anchor: "r", size: 28, color: C.navy, weight: 700 });
  F.label(xc - 14, yN, "$N$", { anchor: "r", size: 28, color: C.navy, weight: 700 });
  F.toggle(xs, yP, yN, S === 1);
  F.wire([[xs, ym], [xs - 0, ym]]);
  F.wire([[xs, ym], [xs + 130, ym]]); F.node(xs + 130, ym);
  F.label(xs + 142, ym, "$x$", { anchor: "l", size: 30, color: C.navy, weight: 700 });
  // 극전압 화살표: 0 → x (점선 기준선)
  F.line(xc, ym, xs - 10, ym, { color: C.grid, width: 2, dash: "6 6" });
  F.label(x0 + 240, 440, S === 1 ? "$S_x = 1$ : $v_{x0} = +\\tfrac{V_{dc}}{2} = +1.128$" : "$S_x = 0$ : $v_{x0} = -\\tfrac{V_{dc}}{2} = -1.128$",
    { anchor: "b", size: 26, color: S === 1 ? C.blue : C.orange, weight: 700 });
}
leg(0, 1); leg(500, 0);
F.line(490, 40, 490, 400, { color: C.grid, width: 2 });
F.done();
