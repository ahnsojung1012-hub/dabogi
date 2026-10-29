import re,json,sys,html
from collections import Counter
W=sys.argv[1]
key={int(k):v for k,v in json.load(open(W+'/key.json')).items()}
t=open(W+'/bbox.html',encoding='utf8').read()
pages=re.split(r'<page ',t)[1:]
res={};report=[]
for i,pg in enumerate(pages):
    pn=i+1
    m=re.match(r'width="([\d.]+)" height="([\d.]+)"',pg);pw,ph=float(m[1]),float(m[2])
    words=[(float(a),float(b),float(c),float(d),html.unescape(w)) for a,b,c,d,w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',pg)]
    exp=[n for n,_ in key.get(pn,[])]
    cands={}
    for (x0,y0,x1,y1,w) in words:
        s=w.rstrip('.').strip()
        if not re.fullmatch(r'[0-9]+',s): continue
        n=int(s)
        if n not in exp: continue
        if y0<40 or y0>ph-50: continue
        # line start: no word on same line to the left within 120pt
        left=[1 for (a,b,c,d,ww) in words if abs(b-y0)<4 and c<=x0+0.5 and x0-c<120 and ww.strip()]
        cands.setdefault(n,[]).append(dict(x=x0,y=y0,x1=x1,y1=y1,h=y1-y0,start=not left,dot=w.endswith('.'),txt=w))
    chosen={}
    for n in exp:
        cs=[c for c in cands.get(n,[]) if c['start']]
        if not cs: cs=cands.get(n,[])
        if not cs: continue
        cs.sort(key=lambda c:(-c['h'],c['x']))
        chosen[n]=cs
    res[pn]=dict(w=pw,h=ph,exp=exp,cands={n:chosen[n] for n in chosen})
    miss=[n for n in exp if n not in chosen];amb=[n for n in chosen if len(chosen[n])>1]
    if miss or amb: report.append((pn,miss,amb))
json.dump(res,open(W+'/cands.json','w'))
print('pages',len(res),'problem pages with issues',len(report))
for r in report[:60]: print(r)
