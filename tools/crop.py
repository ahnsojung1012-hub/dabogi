"""Crop every problem of the 중2-2 시험대비집 into its own image (text + figure + choices)."""
import json, sys, os
import numpy as np
from PIL import Image

W = sys.argv[1]; OUT = sys.argv[2]
S = 3.0  # render scale (216 dpi / 72)
labels = {pn: (pw, ph, labs) for pn, pw, ph, labs in json.load(open(W + '/labels.json'))}
SETS = [
    ('c06', '06 평행선과 선분의 길이의 비', 116, 123, 4),
    ('c07', '07 삼각형의 무게중심', 125, 132, 4),
    ('x141', '잘 틀리는 유형·서술형·최고난도', 133, 139, 3),
    ('x046', '잘 틀리는 유형·서술형·최고난도', 140, 144, 3),
    ('c08', '08 피타고라스 정리', 147, 153, 4),
    ('x091', '잘 틀리는 유형·서술형·최고난도', 154, 158, 3),
    ('c09', '09 경우의 수', 161, 170, 4),
    ('x109', '잘 틀리는 유형·서술형·최고난도', 171, 175, 3),
    ('c10', '10 확률', 178, 186, 4),
    ('x099', '잘 틀리는 유형·서술형·최고난도', 187, 193, 3),
    ('j80', '족집게 마무리 객관식 80선', 194, 207, 2),
    ('j20', '족집게 마무리 서술형 20선', 208, 212, 2),
    ('g24', '고난도 기출문제', 213, 218, 2),
]

def is_label(w, h, digits):
    if digits == 4: return len(w) == 4 and abs(h - 15.8) < 0.6
    if digits == 3: return len(w) == 3 and abs(h - 15.4) < 0.6
    return len(w) == 2 and abs(h - 24.7) < 0.6

from scipy import ndimage

DROPS = []
STARS = False
def clean(img):
    """Whiten decorations that are not part of the problem, then drop trailing non-problem blocks."""
    a = np.asarray(img.convert('RGB')).astype(int).copy()
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    # 1) light-cyan connector icons/arrows between paired problems (thin or small pieces only; figure fills stay)
    cyan = (R > 120) & (R < 205) & (G > 195) & (G < 245) & (B >= 225) & (B - R >= 35)
    lab, n = ndimage.label(cyan)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        area = (lab[sl] == i).sum(); box = (sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start)
        if area < 2500 or area / box < 0.35: a[sl][lab[sl] == i] = 255
    gray = a.mean(axis=2)
    ink = gray < 238
    # 2) anything touching the top edge (badges/headers cut by the crop line), and specks near the top
    lab, n = ndimage.label(ink)
    if n:
        for i in set(np.unique(lab[:3])) - {0}: a[lab == i] = 255
        if not STARS:
            for i, sl in enumerate(ndimage.find_objects(lab), 1):
                if sl[0].stop <= 45 and (lab[sl] == i).sum() < 60: a[sl][lab[sl] == i] = 255
    gray = a.mean(axis=2); ink = gray < 238
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    purple = ((R > 60) & (R < 170) & (G < 100) & (B > 110) & (B - G > 50)) | ((R > 120) & (R < 200) & (G > 90) & (G < 150) & (B > 160) & (B - G > 40) & (R - G > 20))
    H, Wd = ink.shape
    for _ in range(12):
        rows = np.where(ink.any(axis=1))[0]
        if not len(rows): break
        # split into blocks separated by >= 36px of white
        gaps = np.where(np.diff(rows) > 36)[0]
        if not len(gaps): break
        y0 = rows[gaps[-1] + 1]; y1 = rows[-1] + 1
        blk = ink[y0:y1]; cols = np.where(blk.any(axis=0))[0]
        bw = cols[-1] - cols[0] + 1; bh = y1 - y0
        fill = blk.mean(axis=1).mean()
        dens = blk.mean()
        drop = (purple[y0:y1].mean() > 0.002 and bh < 160) or (fill >= 0.45 and bh <= 100) \
            or (bw >= 0.85 * Wd and dens < 0.03) or (bw < 60 and bh < 60)
        if not drop: break
        ink[y0:] = False; a[y0:] = 255
        DROPS.append((bh, bw, round(fill,2), round(float(dens),3)))
    return Image.fromarray(a.clip(0, 255).astype('uint8'))

def trim(img, pad=10):
    img = clean(img)
    a = np.asarray(img.convert('L'))
    dark = a < 235
    ys = np.where(dark.any(axis=1))[0]; xs = np.where(dark.any(axis=0))[0]
    if not len(ys): return img
    y0, y1 = max(0, ys[0] - pad), min(a.shape[0], ys[-1] + pad)
    x0, x1 = max(0, xs[0] - pad), min(a.shape[1], xs[-1] + pad)
    return img.crop((x0, y0, x1, y1))

manifest = []
os.makedirs(OUT, exist_ok=True)
for key, title, p0, p1, digits in SETS:
    items = []
    for pn in range(p0, p1 + 1):
        pw, ph, labs = labels[pn]
        page = Image.open(f'{W}/render/p-{pn}.png').convert('RGB')
        probs = [(y, x, w) for y, x, w, h in labs if w.isdigit() and is_label(w, h, digits)]
        types = [(y, x) for y, x, w, h in labs if digits == 4 and len(w) == 2 and abs(h - 19.8) < 0.6]
        if not probs: continue
        xl = min(x for y, x, w in probs if x < pw / 2) if any(x < pw / 2 for y, x, w in probs) else (82 if pn % 2 else 85) + (9 if digits == 2 else 0)
        xr = min(x for y, x, w in probs if x >= pw / 2) if any(x >= pw / 2 for y, x, w in probs) else xl + (275 if digits == 2 else 265)
        bottom = {4: 815, 3: ph - 45, 2: 826}[digits]
        cols = {'L': (xl - 7, xr - {4: 16, 3: 22, 2: 22}[digits]), 'R': (xr - 7, min(pw - 30, xr + (xr - xl) - 8))}
        for y, x, w in probs:
            c = 'L' if x < pw / 2 else 'R'
            top = y - (16 if digits == 3 else 7)
            nxt = [yy - (18 if digits == 3 else 9) for yy, xx, ww in probs if (xx < pw / 2) == (c == 'L') and yy > y]
            nxt += [yy - 30 for yy, xx in types if (xx < pw / 2) == (c == 'L') and yy > y]
            end = min(nxt) if nxt else bottom
            x0, x1 = cols[c]
            crop = page.crop((int(x0 * S), int(top * S), int(x1 * S), int(end * S)))
            DROPS.clear(); STARS = digits == 3; crop = trim(crop)
            if DROPS: print('DROP', key, w, DROPS)
            fn = f'{key}/{w}.jpg'
            os.makedirs(f'{OUT}/{key}', exist_ok=True)
            crop.save(f'{OUT}/{fn}', quality=78, optimize=True)
            items.append({'no': w, 'page': pn, 'img': fn, 'w': crop.width, 'h': crop.height})
    items.sort(key=lambda i: int(i['no']))
    manifest.append({'key': key, 'title': title, 'pages': [p0, p1], 'items': items})
    print(key, len(items), items[0]['no'], '~', items[-1]['no'])
json.dump(manifest, open(f'{OUT}/manifest.json', 'w'), ensure_ascii=False)
