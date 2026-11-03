// render.mjs — 강의 그림·수식 렌더러 (Playwright + KaTeX). 2배 해상도 PNG와 크기 목록(manifest.json)을 만든다.
// 사용: node slides/tools/render.mjs <src 폴더> <출력 폴더>
//   <src>/*.fig.js   : 그림 하나 = 파일 하나. Fig(w,h)로 그리고 F.done()을 부른다. 같은 이름의 .json이 있으면 window.DATA로 들어간다.
//   <src>/_common.js : (선택) 모든 그림 앞에 실행되는 강의 공통 함수
//   <src>/eqs.tex    : "%% 이름 [size=40] [color=#013364]" 머리줄 + LaTeX 본문
// manifest.json에는 각 PNG의 CSS 크기(= 슬라이드에 넣을 px 크기, PNG의 절반)가 기록된다.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const TOOLS = path.dirname(fileURLToPath(import.meta.url));
const [srcDir, outDir] = process.argv.slice(2).map((p) => path.resolve(p));
if (!srcDir || !outDir) { console.error("usage: render.mjs <src> <out>"); process.exit(1); }
fs.mkdirSync(outDir, { recursive: true });
const only = process.env.ONLY ? new Set(process.env.ONLY.split(",")) : null;

const head = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="node_modules/katex/dist/katex.min.css">
<link rel="stylesheet" href="figlib.css">
<script src="node_modules/katex/dist/katex.min.js"></script>
<script src="node_modules/katex/dist/contrib/auto-render.min.js"></script>
<script src="figlib.js"></script></head><body>`;

const browser = await chromium.launch();
const ctx = await browser.newContext({ deviceScaleFactor: 2, viewport: { width: 2400, height: 1600 } });
const manifestPath = path.join(outDir, "manifest.json");
const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf8")) : {};

async function page(html, tmpName) {
  const tmp = path.join(TOOLS, `.tmp-${tmpName}.html`);
  fs.writeFileSync(tmp, html);
  const p = await ctx.newPage();
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  p.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(pathToFileURL(tmp).href);
  try { await p.waitForFunction(() => window.FIG_READY === true, null, { timeout: 15000 }); }
  catch (e) { errs.push("FIG_READY timeout"); }
  fs.unlinkSync(tmp);
  if (errs.length) { console.error(`✗ ${tmpName}:\n  ` + errs.join("\n  ")); }
  return p;
}

// 그림
for (const f of fs.readdirSync(srcDir).filter((f) => f.endsWith(".fig.js")).sort()) {
  const name = f.replace(/\.fig\.js$/, "");
  if (only && !only.has(name)) continue;
  const dataFile = path.join(srcDir, name + ".json");
  const data = fs.existsSync(dataFile) ? fs.readFileSync(dataFile, "utf8") : "null";
  const code = fs.readFileSync(path.join(srcDir, f), "utf8");
  const commonFile = path.join(srcDir, "_common.js");
  const common = fs.existsSync(commonFile) ? fs.readFileSync(commonFile, "utf8") : "";
  const p = await page(`${head}<script>window.DATA=${data};</script><script>${common}</script><script>${code}</script></body></html>`, name);
  const box = await p.$("#fig");
  if (box) {
    const out = path.join(outDir, name + ".png");
    await box.screenshot({ path: out, omitBackground: true });
    const bb = await box.boundingBox();
    manifest[name + ".png"] = { w: Math.round(bb.width), h: Math.round(bb.height) };
    console.log(`fig ${name}.png ${Math.round(bb.width)}x${Math.round(bb.height)}`);
  }
  await p.close();
}

// 수식
// eqs.tex 형식: "%% 이름 [size=34] [color=#hex]" 줄 다음에 LaTeX 본문(여러 줄 가능)
function readTex(file) {
  const out = {};
  let cur = null;
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    const m = line.match(/^%%\s*(\S+)(.*)$/);
    if (m) {
      cur = { tex: "" };
      for (const kv of m[2].trim().split(/\s+/).filter(Boolean)) {
        const [k, v] = kv.split("=");
        cur[k] = k === "size" ? Number(v) : v;
      }
      out[m[1]] = cur;
    } else if (cur && !line.startsWith("%")) cur.tex += line + "\n";
  }
  for (const k in out) out[k].tex = out[k].tex.trim();
  return out;
}
const eqFile = path.join(srcDir, "eqs.tex");
if (fs.existsSync(eqFile)) {
  const eqs = readTex(eqFile);
  const items = Object.entries(eqs).filter(([n]) => !only || only.has(n))
    .map(([name, v]) => (typeof v === "string" ? { name, tex: v } : Object.assign({ name }, v)));
  if (items.length) {
    const p = await page(`${head}<script>EQ(${JSON.stringify(items)});</script></body></html>`, "eqs");
    for (const d of await p.$$(".eq")) {
      const name = await d.getAttribute("data-name");
      const out = path.join(outDir, name + ".png");
      await d.screenshot({ path: out, omitBackground: true });
      const bb = await d.boundingBox();
      manifest[name + ".png"] = { w: Math.round(bb.width), h: Math.round(bb.height) };
      console.log(`eq  ${name}.png ${Math.round(bb.width)}x${Math.round(bb.height)}`);
    }
    await p.close();
  }
}
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 1));
await browser.close();
