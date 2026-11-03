/* figlib.js — 강의 슬라이드용 그림 라이브러리 (SVG 도형 + KaTeX 라벨).
 * 그림 페이지(.html)는 이 파일과 figlib.css를 불러와서 F = Fig(w, h)로 시작하고, 끝에 F.done()을 부른다.
 * render.mjs가 페이지를 열어 2배 해상도 PNG로 찍는다. 라벨 문자열 안의 $...$는 KaTeX로 조판된다.
 */
(function () {
  const C = {
    navy: "#013364", blue: "#2463c8", orange: "#eb6834", green: "#3aa150", slate: "#45546b",
    muted: "#7d8ca2", grid: "#e3e9f0", axis: "#9aa8b8", light: "#e9f0f6", lime: "#8bc22c",
    teal: "#037673", red: "#c8323c", purple: "#7b4fc0", bg: "#ffffff",
  };
  C.a = C.blue; C.b = C.orange; C.c = C.green;
  const NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function Fig(w, h, opts = {}) {
    document.body.dataset.w = w;
    document.body.dataset.h = h;
    const root = document.createElement("div");
    root.id = "fig";
    root.style.width = w + "px";
    root.style.height = h + "px";
    root.style.background = opts.bg === undefined ? C.bg : opts.bg;
    document.body.appendChild(root);
    const svg = el("svg", { width: w, height: h, viewBox: `0 0 ${w} ${h}` });
    root.appendChild(svg);
    const labels = document.createElement("div");
    labels.className = "labels";
    root.appendChild(labels);

    const F = { svg, root, w, h, C };

    /* ---------- 기본 도형 (픽셀 좌표) ---------- */
    F.line = (x1, y1, x2, y2, s = {}) =>
      el("line", { x1, y1, x2, y2, stroke: s.color || C.slate, "stroke-width": s.width || 3,
        "stroke-dasharray": s.dash, "stroke-linecap": s.cap || "round", opacity: s.opacity }, s.g || svg);
    F.poly = (pts, s = {}) =>
      el(s.closed ? "polygon" : "polyline", { points: pts.map((p) => p.join(",")).join(" "),
        fill: s.fill || "none", stroke: s.color || (s.fill ? "none" : C.slate), "stroke-width": s.width || 3,
        "stroke-dasharray": s.dash, "stroke-linejoin": "round", "stroke-linecap": "round", opacity: s.opacity }, s.g || svg);
    F.path = (d, s = {}) =>
      el("path", { d, fill: s.fill || "none", stroke: s.color || (s.fill ? "none" : C.slate),
        "stroke-width": s.width || 3, "stroke-dasharray": s.dash, "stroke-linejoin": "round",
        "stroke-linecap": "round", opacity: s.opacity }, s.g || svg);
    F.rect = (x, y, w2, h2, s = {}) =>
      el("rect", { x, y, width: w2, height: h2, rx: s.r || 0, fill: s.fill || "none",
        stroke: s.color || (s.fill ? "none" : C.slate), "stroke-width": s.width || 3, "stroke-dasharray": s.dash,
        opacity: s.opacity }, s.g || svg);
    F.circle = (cx, cy, r, s = {}) =>
      el("circle", { cx, cy, r, fill: s.fill || "none", stroke: s.color || (s.fill ? "none" : C.slate),
        "stroke-width": s.width || 3, "stroke-dasharray": s.dash, opacity: s.opacity }, s.g || svg);
    F.dot = (x, y, s = {}) => F.circle(x, y, s.r || 7, { fill: s.color || C.slate });

    /* 화살표: 머리를 다각형으로 그려 색이 정확히 맞는다 */
    F.arrow = (x1, y1, x2, y2, s = {}) => {
      const wdt = s.width || 4, hl = s.head || Math.max(16, wdt * 4.2), hw = s.headw || hl * 0.62;
      const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy);
      if (L < 1e-6) return;
      const ux = dx / L, uy = dy / L;
      const g = el("g", { opacity: s.opacity }, s.g || svg);
      const bx = x2 - ux * hl * 0.9, by = y2 - uy * hl * 0.9;
      el("line", { x1, y1, x2: bx, y2: by, stroke: s.color || C.slate, "stroke-width": wdt,
        "stroke-linecap": "round", "stroke-dasharray": s.dash }, g);
      const px = -uy, py = ux;
      el("polygon", { points: [[x2, y2], [x2 - ux * hl + px * hw / 2, y2 - uy * hl + py * hw / 2],
        [x2 - ux * hl * 0.78, y2 - uy * hl * 0.78], [x2 - ux * hl - px * hw / 2, y2 - uy * hl - py * hw / 2]]
        .map((p) => p.join(",")).join(" "), fill: s.color || C.slate }, g);
      if (s.both) F.arrow(x2, y2, x1, y1, Object.assign({}, s, { both: false, g }));
      return g;
    };

    /* 원호 (도 단위, 수학 방향: 반시계 +). 화면 y는 아래로 증가하므로 내부에서 뒤집는다 */
    F.arc = (cx, cy, r, a0, a1, s = {}) => {
      const p = (a) => [cx + r * Math.cos((a * Math.PI) / 180), cy - r * Math.sin((a * Math.PI) / 180)];
      const [x0, y0] = p(a0), [x1, y1] = p(a1);
      const large = Math.abs(a1 - a0) > 180 ? 1 : 0, sweep = a1 > a0 ? 0 : 1;
      F.path(`M${x0},${y0} A${r},${r} 0 ${large} ${sweep} ${x1},${y1}`, s);
      if (s.arrow) {
        const da = a1 > a0 ? -6 : 6, [xb, yb] = p(a1 + da);
        F.arrow(xb, yb, x1, y1, { color: s.color, width: s.width || 3, head: s.head || 16 });
      }
    };

    /* ---------- 라벨 ($...$는 KaTeX) ---------- */
    const ANCH = { c: [-50, -50], l: [0, -50], r: [-100, -50], t: [-50, 0], b: [-50, -100],
      tl: [0, 0], tr: [-100, 0], bl: [0, -100], br: [-100, -100] };
    F.label = (x, y, text, s = {}) => {
      const d = document.createElement("div");
      d.className = "lbl" + (s.box ? " box" : "");
      d.style.left = x + "px";
      d.style.top = y + "px";
      d.style.color = s.color || C.slate;
      d.style.fontSize = (s.size || 30) + "px";
      d.style.fontWeight = s.weight || 500;
      if (s.bg) { d.style.background = s.bg; d.style.padding = "2px 8px"; d.style.borderRadius = "6px"; }
      if (s.width) { d.style.width = s.width + "px"; d.style.whiteSpace = "normal"; d.style.textAlign = s.align || "center"; }
      const [ax, ay] = ANCH[s.anchor || "c"];
      d.style.transform = `translate(${ax}%, ${ay}%)` + (s.rotate ? ` rotate(${s.rotate}deg)` : "");
      d.innerHTML = text;
      labels.appendChild(d);
      return d;
    };

    /* ---------- 데이터 좌표 영역 ---------- */
    F.frame = (box, xlim, ylim, s = {}) => {
      const [X, Y, W, H] = box;
      const fx = (x) => X + ((x - xlim[0]) / (xlim[1] - xlim[0])) * W;
      const fy = (y) => Y + H - ((y - ylim[0]) / (ylim[1] - ylim[0])) * H;
      const A = { box, xlim, ylim, x: fx, y: fy, F };
      const clipId = "c" + Math.random().toString(36).slice(2, 8);
      const cp = el("clipPath", { id: clipId }, el("defs", {}, svg));
      el("rect", { x: X, y: Y - 2, width: W, height: H + 4 }, cp);
      A.g = el("g", { "clip-path": `url(#${clipId})` }, svg);
      A.axes = (o = {}) => {
        const xt = o.xticks || [], yt = o.yticks || [];
        xt.forEach((t) => F.line(fx(t), Y, fx(t), Y + H, { color: C.grid, width: 2 }));
        yt.forEach((t) => F.line(X, fy(t), X + W, fy(t), { color: C.grid, width: 2 }));
        if (o.zero !== false && ylim[0] < 0 && ylim[1] > 0) F.line(X, fy(0), X + W, fy(0), { color: C.axis, width: 2.5 });
        F.line(X, Y + H, X + W, Y + H, { color: C.axis, width: 2.5 });
        F.line(X, Y, X, Y + H, { color: C.axis, width: 2.5 });
        const fs = o.tick || 24;
        const fmt = o.fmt || ((v) => (Math.abs(v) < 1e-9 ? "0" : String(+v.toFixed(3)).replace("-", "−")));
        const xf = o.xfmt || fmt, yf = o.yfmt || fmt;
        xt.forEach((t) => { const s2 = xf(t); if (s2 !== "") F.label(fx(t), Y + H + 12, s2, { anchor: "t", size: fs, color: C.muted }); });
        yt.forEach((t) => { const s2 = yf(t); if (s2 !== "") F.label(X - 14, fy(t), s2, { anchor: "r", size: fs, color: C.muted }); });
        if (o.xlabel) F.label(X + W, Y + H + 52, o.xlabel, { anchor: "tr", size: o.lsize || 26, color: C.slate });
        if (o.ylabel) F.label(X, Y - 18, o.ylabel, { anchor: "bl", size: o.lsize || 26, color: C.slate });
        return A;
      };
      A.plot = (xs, ys, st = {}) =>
        F.poly(xs.map((x, i) => [fx(x), fy(ys[i])]), Object.assign({ width: 4 }, st, { g: A.g }));
      A.fn = (f, n, st) => {
        const xs = [], ys = [];
        for (let i = 0; i <= (n || 600); i++) {
          const x = xlim[0] + ((xlim[1] - xlim[0]) * i) / (n || 600);
          xs.push(x); ys.push(f(x));
        }
        return A.plot(xs, ys, st);
      };
      A.vline = (x, st = {}) => F.line(fx(x), Y, fx(x), Y + H, Object.assign({ color: C.muted, width: 2.5, dash: "10 8" }, st));
      A.hline = (y, st = {}) => F.line(X, fy(y), X + W, fy(y), Object.assign({ color: C.muted, width: 2.5, dash: "10 8" }, st));
      A.label = (x, y, t, st) => F.label(fx(x), fy(y), t, st);
      A.arrow = (x1, y1, x2, y2, st) => F.arrow(fx(x1), fy(y1), fx(x2), fy(y2), st);
      return A;
    };

    /* ---------- 벡터 평면 (중심 cx,cy, 1 pu = R 픽셀) ---------- */
    F.plane = (cx, cy, R) => {
      const P = { cx, cy, R };
      P.xy = (z) => [cx + z[0] * R, cy - z[1] * R];
      P.pol = (m, deg) => [m * Math.cos((deg * Math.PI) / 180), m * Math.sin((deg * Math.PI) / 180)];
      P.vec = (z, st = {}, z0 = [0, 0]) => {
        const [x0, y0] = P.xy(z0), [x1, y1] = P.xy([z0[0] + z[0], z0[1] + z[1]]);
        return F.arrow(x0, y0, x1, y1, st);
      };
      P.axis = (deg, len, text, st = {}) => {
        const [x0, y0] = P.xy(P.pol(-(st.back || 0), deg)), [x1, y1] = P.xy(P.pol(len, deg));
        F.arrow(x0, y0, x1, y1, { color: st.color || C.axis, width: st.width || 2.5, head: 14, dash: st.dash });
        if (text) {
          const [lx, ly] = P.xy(P.pol(len + (st.loff || 0.12), deg));
          F.label(lx, ly, text, { size: st.size || 30, color: st.lcolor || st.color || C.muted });
        }
      };
      P.label = (z, t, st) => { const [x, y] = P.xy(z); return F.label(x, y, t, st); };
      P.arc = (r, a0, a1, st) => F.arc(cx, cy, r * R, a0, a1, st);
      P.circle = (r, st) => F.circle(cx, cy, r * R, st);
      return P;
    };

    /* ---------- 회로 기호 (수평/수직 배선 위에 놓는다) ---------- */
    const W2 = 3.5;
    F.wire = (pts, s = {}) => F.poly(pts, { color: s.color || C.navy, width: s.width || W2 });
    F.node = (x, y, s = {}) => F.circle(x, y, s.r || 6.5, { fill: s.color || C.navy });
    /* 커패시터: 중심 (x,y), 수직 배선 기준 */
    F.cap = (x, y, s = {}) => {
      const pw = s.w || 48, gap = s.gap || 14, col = s.color || C.navy;
      F.line(x - pw / 2, y - gap / 2, x + pw / 2, y - gap / 2, { color: col, width: 5, cap: "butt" });
      F.line(x - pw / 2, y + gap / 2, x + pw / 2, y + gap / 2, { color: col, width: 5, cap: "butt" });
    };
    /* 인덕터: (x1,y) → (x2,y) 수평 */
    F.inductor = (x1, y, x2, s = {}) => {
      const n = s.n || 4, L = x2 - x1, r = L / (2 * n);
      let d = `M${x1},${y}`;
      for (let i = 0; i < n; i++) d += ` a${r},${r} 0 0 1 ${2 * r},0`;
      F.path(d, { color: s.color || C.navy, width: s.width || W2 });
    };
    F.resistor = (x1, y, x2, s = {}) => {
      const n = 6, L = x2 - x1, st = L / n, a = s.amp || 12;
      const pts = [[x1, y]];
      for (let i = 0; i < n; i++) pts.push([x1 + st * (i + 0.5), y + (i % 2 ? a : -a)]);
      pts.push([x2, y]);
      F.poly(pts, { color: s.color || C.navy, width: s.width || W2 });
    };
    /* 스위치(IGBT 단순화) + 역병렬 다이오드: 위 단자 (x,y1), 아래 단자 (x,y2) */
    F.igbt = (x, y1, y2, s = {}) => {
      const col = s.color || C.navy, m = (y1 + y2) / 2, hh = s.h || 34;
      F.line(x, y1, x, m - hh, { color: col, width: W2 });
      F.line(x, m + hh, x, y2, { color: col, width: W2 });
      // 스위치 몸체: 게이트 바 + 비스듬한 콜렉터/에미터
      F.line(x - 22, m - hh * 0.8, x - 22, m + hh * 0.8, { color: col, width: 5, cap: "butt" });
      F.line(x - 22, m - hh * 0.4, x, m - hh, { color: col, width: W2 });
      F.arrow(x - 22, m + hh * 0.4, x, m + hh, { color: col, width: W2, head: 13 });
      F.line(x - 36, m, x - 22, m, { color: col, width: W2 });
      // 다이오드 (오른쪽, 캐소드 위)
      const dx = x + 40, dh = 16;
      F.line(x, m - hh - 6, dx, m - hh - 6, { color: col, width: 2.8 });
      F.line(x, m + hh + 6, dx, m + hh + 6, { color: col, width: 2.8 });
      F.line(dx, m - hh - 6, dx, m - dh, { color: col, width: 2.8 });
      F.line(dx, m + hh + 6, dx, m + dh, { color: col, width: 2.8 });
      F.poly([[dx - 14, m + dh], [dx + 14, m + dh], [dx, m - dh + 4]], { closed: true, fill: col });
      F.line(dx - 14, m - dh + 2, dx + 14, m - dh + 2, { color: col, width: 3.5, cap: "butt" });
      if (s.on !== undefined) F.rect(x - 52, m - hh - 16, 112, 2 * hh + 32,
        { r: 12, color: s.on ? C.lime : C.axis, width: 3, dash: s.on ? null : "8 6" });
      if (s.label) F.label(x - 62, m, s.label, { anchor: "r", size: s.lsize || 26, color: col });
    };
    /* 이상적 스위치(단극 쌍투) 기호: 극 (x,y)에서 위(y1) 또는 아래(y2)에 연결 */
    F.toggle = (x, yTop, yBot, up, s = {}) => {
      const col = s.color || C.navy, m = (yTop + yBot) / 2;
      F.node(x + 34, yTop + 30, { r: 6, color: col });
      F.node(x + 34, yBot - 30, { r: 6, color: col });
      F.line(x + 34, yTop, x + 34, yTop + 30, { color: col, width: W2 });
      F.line(x + 34, yBot - 30, x + 34, yBot, { color: col, width: W2 });
      F.node(x, m, { r: 6, color: col });
      F.line(x, m, x + 34, up ? yTop + 30 : yBot - 30, { color: s.blade || C.orange, width: 5 });
    };
    /* 교류 전원 원 */
    F.source = (x, y, r = 30, s = {}) => {
      F.circle(x, y, r, { color: s.color || C.navy, width: W2, fill: C.bg });
      F.path(`M${x - r * 0.55},${y} q${r * 0.275},${-r * 0.6} ${r * 0.55},0 t${r * 0.55},0`, { color: s.color || C.navy, width: 3 });
    };
    F.ground = (x, y, s = {}) => {
      const col = s.color || C.navy;
      [[26, 0], [17, 9], [8, 18]].forEach(([hw, dy]) => F.line(x - hw, y + dy, x + hw, y + dy, { color: col, width: 3.5 }));
    };
    /* 블록 (제어 블록선도) */
    F.block = (x, y, w2, h2, text, s = {}) => {
      F.rect(x - w2 / 2, y - h2 / 2, w2, h2, { r: s.r || 12, fill: s.fill || C.light, color: s.color || C.navy, width: s.width || 3 });
      F.label(x, y, text, { size: s.size || 30, color: s.tcolor || C.navy, weight: s.weight || 600 });
    };
    F.sum = (x, y, s = {}) => {
      F.circle(x, y, s.r || 22, { color: C.navy, width: 3, fill: C.bg });
      F.line(x - 11, y, x + 11, y, { color: C.navy, width: 3 });
      F.line(x, y - 11, x, y + 11, { color: C.navy, width: 3 });
    };

    F.done = () => {
      if (window.renderMathInElement) {
        renderMathInElement(labels, { delimiters: [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false }], throwOnError: true });
      }
      document.fonts.ready.then(() => { window.FIG_READY = true; });
    };
    return F;
  }

  /* 수식 페이지: EQ(list) — 각 항목 {name, tex, size, color} */
  function EQ(items) {
    const wrap = document.createElement("div");
    wrap.id = "eqs";
    document.body.appendChild(wrap);
    items.forEach((it) => {
      const d = document.createElement("div");
      d.className = "eq";
      d.dataset.name = it.name;
      d.style.fontSize = (it.size || 40) + "px";
      d.style.color = it.color || C.navy;
      try {
        katex.render(it.tex, d, { displayMode: true, throwOnError: true, strict: false, trust: false,
          macros: { "\\vv": "\\vec{#1}", "\\pu": "\\,\\mathrm{pu}" } });
      } catch (e) { console.error(`${it.name}: ${e.message}`); d.textContent = "ERROR " + it.name; }
      wrap.appendChild(d);
    });
    document.fonts.ready.then(() => { window.FIG_READY = true; });
  }

  window.Fig = Fig;
  window.EQ = EQ;
  window.FC = C;
})();
