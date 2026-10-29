import json, sys, os
from PIL import Image, ImageDraw
W = sys.argv[1]; D = W + '/crops'; out = W + '/review'; os.makedirs(out, exist_ok=True)
m = json.load(open(D + '/manifest.json'))
only = sys.argv[2:] if len(sys.argv) > 2 else None
TW, COLS, MAXH = 330, 4, 2000
for s in m:
    if only and s['key'] not in only: continue
    tiles = []
    for it in s['items']:
        im = Image.open(f"{D}/{it['img']}").convert('RGB')
        sc = TW / im.width; im = im.resize((TW, max(1, int(im.height * sc))))
        t = Image.new('RGB', (TW + 8, im.height + 26), (255, 235, 235)); t.paste(im, (4, 22))
        ImageDraw.Draw(t).text((6, 4), f"{s['key']} {it['no']} p{it['page']}", fill=(200, 0, 0))
        tiles.append(t)
    sheets, row, rows, h = [], [], [], 0
    for t in tiles:
        row.append(t)
        if len(row) == COLS: rows.append(row); row = []
    if row: rows.append(row)
    cur, curh = [], 0
    for r in rows:
        rh = max(t.height for t in r) + 6
        if curh + rh > MAXH and cur: sheets.append(cur); cur, curh = [], 0
        cur.append(r); curh += rh
    if cur: sheets.append(cur)
    for k, rs in enumerate(sheets):
        H = sum(max(t.height for t in r) + 6 for r in rs)
        sh = Image.new('RGB', (COLS * (TW + 14), H), 'white'); y = 0
        for r in rs:
            for i, t in enumerate(r): sh.paste(t, (i * (TW + 14), y))
            y += max(t.height for t in r) + 6
        sh.save(f"{out}/{s['key']}_{k}.jpg", quality=70)
print(sorted(os.listdir(out)))
