"""Crop each problem of the 중1-2 시험대비집 (page-indexed answer key) into its own image."""
import json, sys, os, re
import numpy as np
from PIL import Image
from scipy import ndimage

W, OUT = sys.argv[1], sys.argv[2]
ONLY = set(int(x) for x in sys.argv[3:]) if len(sys.argv) > 3 else None
S = 3.0
cands = json.load(open(W + '/cands.json'))
key = {int(k): v for k, v in json.load(open(W + '/key.json')).items()}
DROPS = []

def sat_mask(a):
    mx, mn = a.max(axis=2), a.min(axis=2)
    return (mx - mn) > 45

def clean(img):
    a = np.asarray(img.convert('RGB')).astype(int).copy()
    g0 = a.mean(axis=2); sat0 = a.max(axis=2) - a.min(axis=2)
    pill = (g0 > 190) & (g0 < 232) & (sat0 < 14)
    pl, pn_ = ndimage.label(pill)
    for i, sl in enumerate(ndimage.find_objects(pl), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 25 < hh < 80 and ww > 180 and ww > 3 * hh and (pl[sl] == i).mean() > 0.6:
            a[sl[0].start - 4:sl[0].stop + 4, sl[1].start - 4:sl[1].stop + 4] = 255
    ink = a.mean(axis=2) < 232
    lab, n = ndimage.label(ink)
    if n:
        for i in set(np.unique(lab[:3])) - {0}: a[lab == i] = 255     # cut-off stuff at the top edge
        for edge in (lab[:, :3], lab[:, -3:]):
            for i in set(np.unique(edge)) - {0}:
                if (lab == i).sum() < 1500: a[lab == i] = 255
    ink = a.mean(axis=2) < 232
    sat = sat_mask(a) & ink
    H, Wd = ink.shape
    for _ in range(12):
        rows = np.where(ink.any(axis=1))[0]
        if not len(rows): break
        gaps = np.where(np.diff(rows) > 30)[0]
        if not len(gaps): break
        y0 = rows[gaps[-1] + 1]; y1 = rows[-1] + 1
        blk = ink[y0:y1]; cols = np.where(blk.any(axis=0))[0]
        bw = cols[-1] - cols[0] + 1; bh = y1 - y0
        sfrac = sat[y0:y1].sum() / max(1, blk.sum())
        dens = blk.mean()
        drop = (bh < 190 and sfrac > 0.22) or (bh < 120 and bw > 0.7 * Wd and dens > 0.25) \
            or (bw < 50 and bh < 50) or (bw > 0.8 * Wd and bh < 14) \
            or (bh < 80 and bw < 0.5 * Wd and (a[y0:y1, max(0, cols[0] - 40):cols[-1] + 40].mean(axis=2) < 245).mean() > 0.5)
        if not drop: break
        DROPS.append((int(bh), int(bw), round(float(sfrac), 2)))
        ink[y0:] = False; a[y0:] = 255
    return Image.fromarray(a.clip(0, 255).astype('uint8'))

def trim(img, pad=12):
    img = clean(img)
    g = np.asarray(img.convert('L')); dark = g < 235
    ys = np.where(dark.any(axis=1))[0]; xs = np.where(dark.any(axis=0))[0]
    if not len(ys): return img
    return img.crop((max(0, xs[0] - pad), max(0, ys[0] - pad), min(g.shape[1], xs[-1] + pad), min(g.shape[0], ys[-1] + pad)))

def page_bottom(arr, ph_px):
    g = arr.mean(axis=2); ink = g < 215
    H, Wd = ink.shape
    for y in range(int(H * 0.72), H):
        if ink[y].sum() > 0.42 * Wd: return y - 6
    return int(H - 0.07 * H)

def pick_labels(info, pw):
    exp = info['exp']; C = {n: info['cands'].get(str(n), []) for n in exp}
    first = {n: sorted(cs, key=lambda c: (-round(c['h'], 0), not c['start'], c['x']))[0] for n, cs in C.items() if cs}
    # column-edge clusters from first picks
    xs = [c['x'] for c in first.values()]
    cl = []
    for x in sorted(xs):
        if not cl or abs(x - cl[-1][-1]) > 10: cl.append([x])
        else: cl[-1].append(x)
    centers = [sum(g) / len(g) for g in cl if len(g) >= max(2, len(xs) // 4)] or [sum(g) / len(g) for g in cl]
    out = {}
    for n, cs in C.items():
        if not cs: continue
        near = [c for c in cs if min(abs(c['x'] - m) for m in centers) <= 8]
        pool = near or cs
        c = dict(sorted(pool, key=lambda c: (-round(c['h'], 0), not c['start'], c['x']))[0])
        if c['h'] < 5:   # only the tiny hidden 'n.' marker was found; the big label sits ~10pt above it
            c['y'] -= 10; c['x'] = min(centers, key=lambda m: abs(m - c['x']))
        out[n] = c
    return out

def h_lines(arr, y0f, y1f, frac=0.42):
    g = arr.mean(axis=2); ink = g < 215; H, Wd = ink.shape
    return [y for y in range(int(H * y0f), int(H * y1f)) if ink[y].sum() > frac * Wd]

def divider(arr):
    g = arr.mean(axis=2); H, Wd = g.shape
    band = g[int(H * .15):int(H * .85), int(Wd * .35):int(Wd * .65)] < 200
    cnt = band.sum(axis=0); x = int(cnt.argmax())
    return (x + int(Wd * .35)) if cnt[x] > 0.25 * band.shape[0] else None

import html as _h
_bb = open(W + '/bbox.html', encoding='utf8').read().split('<page ')[1:]
def page_words(pn):
    return [(float(a), float(b), float(c), float(d), _h.unescape(w)) for a, b, c, d, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', _bb[pn - 1])]
HEAD = re.compile(r'(LEVEL|대표|선택형|서술형|유형|핵심|마무리|확인하기|객관식|문항|단원|Step|기본문제|개념)')
OVR = {(112, 5): (312.06, 390.07)}
SHARED = {193: [(94, 4, 5), (503, 6, 7)]}   # (marker y, first no, last no)
items_all, issues = [], []
prev_last = None   # (page, no) of the last problem seen, for page-crossing continuations
os.makedirs(OUT, exist_ok=True)
def save(img, pn, n, extra=None):
    fn = f'p{pn:03d}/{n}.jpg'; os.makedirs(f'{OUT}/p{pn:03d}', exist_ok=True)
    img.save(f'{OUT}/{fn}', quality=80, optimize=True)
    return fn
def stack(a, b, gap=16):
    o = Image.new('RGB', (max(a.width, b.width), a.height + gap + b.height), 'white'); o.paste(a, (0, 0)); o.paste(b, (0, a.height + gap)); return o
store = {}
for pn in range(1, 238):
    info = cands[str(pn)]; pw, ph = info['w'], info['h']
    picks = pick_labels(info, pw)
    for (opn, on), (ox, oy) in OVR.items():
        if opn == pn: picks[on] = {'x': ox, 'y': oy, 'h': 17}
    for n in info['exp']:
        if n not in picks: issues.append((pn, n, 'no label'))
    labs = [(n, picks[n]['x'], picks[n]['y']) for n in info['exp'] if n in picks]
    if not labs: continue
    page = Image.open(f'{W}/render/p-{pn:03d}.jpg').convert('RGB'); arr = np.asarray(page).astype(int)
    bl = h_lines(arr, 0.86, 1.0); bottom = (bl[0] - 6) / S if bl else ph * 0.93
    tl = h_lines(arr, 0.0, 0.12); top = (tl[-1] + 8) / S if tl else ph * 0.05
    dv = divider(arr); dvx = dv / S if dv else None
    xs = sorted(x for _, x, _ in labs)
    xl = xs[0]; right = [x for x in xs if x > pw * 0.4]
    xr = right[0] if right else (dvx + 8 if dvx else None)
    if xl > pw * 0.4: xl = 42.0 if pw > 700 else 40.0
    l1 = (xr - 8) if xr else pw / 2 - 4
    if dvx and dvx < l1 + 6: l1 = min(l1, dvx - 4)
    r0 = (xr - 6) if xr else pw / 2 + 4
    if dvx and r0 < dvx + 3: r0 = dvx + 3
    colL = (xl - 6, l1); colR = (r0, min(pw - 10, pw - xl + 6))
    isRf = lambda x: xr is not None and x >= xr - 20
    marks = SHARED.get(pn, [])
    def crop_box(isR, y0, y1):
        x0, x1 = colR if isR else colL
        if y1 - y0 < 4: return None
        return trim(page.crop((int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S))))
    # continuation: content above the first label of each column belongs to the previous problem
    for isR in (False, True):
        colLabs = sorted(y for n, x, y in labs if isRf(x) == isR)
        if not colLabs: continue
        firstY = colLabs[0]
        if any(abs(my - firstY) < 1 or (my < firstY) for my, a_, b_ in marks if isRf(xr or 0) == isR and isR): continue
        im = crop_box(isR, top, firstY - 6)
        if im is None: continue
        g = np.asarray(im.convert('L')) < 200
        if g.sum() < 400 or im.height < 40: continue
        x0c, x1c = colR if isR else colL
        ws = [w for (a, b, c, d, w) in page_words(pn) if a >= x0c - 2 and c <= x1c + 2 and b >= top - 2 and d <= firstY - 4]
        if len(ws) < 5 or any(HEAD.search(w) for w in ws) or not ws[0][:1] in '①②③④⑤ㄱ(': continue
        tgt = None
        if isR:
            leftLabs = [(y, n) for n, x, y in labs if not isRf(x)]
            if leftLabs: tgt = (pn, max(leftLabs)[1])
        if tgt is None: tgt = prev_last
        os.makedirs(OUT+'/cont',exist_ok=True); im.save(f"{OUT}/cont/p{pn:03d}{'R' if isR else 'L'}.jpg",quality=60)
        if tgt and tgt in store:
            store[tgt]['img'] = stack(store[tgt]['img'], im); store[tgt]['cont'] = True
            issues.append((pn, 'cont->', tgt))
    for n, x, y in labs:
        isR = isRf(x)
        same = [yy for nn, xx, yy in labs if isRf(xx) == isR and yy > y + 2]
        same += [my for my, a_, b_ in marks if my > y + 2 and isR]
        end = (min(same) - 6) if same else bottom
        im = crop_box(isR, y - 6, end)
        for my, a_, b_ in marks:
            if a_ <= n <= b_:
                labA = [yy for nn, xx, yy in labs if nn == a_][0]
                sh = crop_box(True, my - 6, labA - 6)
                if sh is not None: im = stack(sh, im)
        store[(pn, n)] = {'img': im, 'page': pn, 'no': n}
    prev_last = (pn, max(labs, key=lambda t: (isRf(t[1]), t[2]))[0])
for (pn, n), v in store.items():
    if ONLY and pn not in ONLY: continue
    fn = save(v['img'], pn, n)
    items_all.append({'page': pn, 'no': n, 'img': fn, 'w': v['img'].width, 'h': v['img'].height, 'cont': v.get('cont', False)})
json.dump(items_all, open(OUT + '/items.json', 'w'), ensure_ascii=False)
print('items', len(items_all)); print('issues', [i for i in issues if i[1]!='cont->'][:20]); print('continuations', [i for i in issues if i[1]=='cont->'])
