"""렌더 결과 확인용 밀착 인화: python sheet.py <폴더> <출력.png> [패턴]  (PNG를 2열로 배치)"""
import sys, glob, os
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
pat = sys.argv[3] if len(sys.argv) > 3 else "F*.png"
ims = [(os.path.basename(f), Image.open(f).convert("RGBA")) for f in sorted(glob.glob(os.path.join(d, pat)))]
col_w = 1400
rows, cur, h = [], [], 0
for n, im in ims:
    im.thumbnail((col_w // 2 - 20, 1200))
    cur.append(im)
    if len(cur) == 2: rows.append(cur); cur = []
if cur: rows.append(cur)
H = sum(max(i.height for i in r) + 24 for r in rows)
sheet = Image.new("RGB", (col_w, H), "#d0d6dd")
y = 0
for r in rows:
    x = 10
    for im in r:
        bg = Image.new("RGB", im.size, "white"); bg.paste(im, (0, 0), im); sheet.paste(bg, (x, y + 12)); x += col_w // 2
    y += max(i.height for i in r) + 24
sheet.save(out)
