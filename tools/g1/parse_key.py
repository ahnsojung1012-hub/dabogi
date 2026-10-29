"""Parse '중1-2 시험대비집 페이지별 빠른답지' text (pdftotext -layout) into {page: [[no, answer], ...]}."""
import re, json, sys

LABELS = ['LEVEL 1~3', 'LEVEL 1~2', 'LEVEL 2', '유형', '심화', '1회', '2회', '3회']

def strip_labels(s):
    for lb in LABELS:
        s = re.sub(r'(^|\s)' + re.escape(lb) + r'(?=\s|$)', ' ', s)
    return re.sub(r'(?<=\d)(?=[①②③④⑤])', ' ', s).strip()

def run_last(tokens):
    """Last problem number reached when reading a consecutive run from the first token."""
    if not tokens or not tokens[0].isdigit(): return None
    k = int(tokens[0])
    for t in tokens[1:]:
        if t == str(k + 1): k += 1
    return k

text = open(sys.argv[1], encoding='utf8').read()
chunks, cur, last = {}, None, 0
for raw in text.split('\n'):
    if '검토 결과' in raw: break
    l = raw.strip()
    if not l or '빠른답지' in l or '대비집 237쪽' in l or '답지 오류' in l: continue
    if re.search(r'p\.\d+–\d+', l): continue
    if (re.fullmatch(r'(\d)\1', l) and len(raw) - len(raw.lstrip()) > 30) or re.fullmatch(r'/\d+', l): continue
    toks = l.split()
    if re.fullmatch(r'\d{1,3}', toks[0]):
        pg = int(toks[0])
        la = strip_labels(' '.join(toks[1:])).split()
        first = la[0] if la else ''
        if (cur is None or cur < pg <= cur + 2) and (not la or (first.isdigit() and (int(first) == last + 1 or int(first) == 1 or int(first) > last + 1))):
            cur = pg; toks = toks[1:]; chunks.setdefault(cur, [])
    rest = strip_labels(' '.join(toks))
    if not rest or cur is None: continue
    chunks[cur].append(rest)
    lk = run_last(' '.join(chunks[cur]).split())
    if lk is not None: last = lk

res = {}
for pg, cs in chunks.items():
    toks = ' '.join(cs).split()
    if not toks: continue
    if not toks[0].isdigit(): print('BAD START', pg, toks[:6]); continue
    items, k, i = [], int(toks[0]), 1
    while True:
        j = i
        while j < len(toks) and toks[j] != str(k + 1): j += 1
        items.append([k, ' '.join(toks[i:j]).strip()])
        if j >= len(toks): break
        k += 1; i = j + 1
    res[pg] = items
json.dump(res, open(sys.argv[2], 'w'), ensure_ascii=False)
print('pages', len(res), 'items', sum(len(v) for v in res.values()))
