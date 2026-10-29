import json,re,sys,os,shutil
W,R=sys.argv[1],sys.argv[2]
txt=open(W+'/key.txt',encoding='utf8').read()
secs=[(m[1].strip(),int(m[2]),int(m[3])) for m in re.finditer(r'^\s*(.+?)\s+p\.(\d+)–(\d+)',txt,re.M)]
key={int(k):v for k,v in json.load(open(W+'/key.json')).items()}
items={(i['page'],i['no']):i for i in json.load(open(W+'/crops2/items.json'))}
sets=[];answers={};flags=[]
for title,p0,p1 in secs:
    short=re.sub(r'^[ⅠⅡⅢⅣ]-\d\s*','',title)
    runs=[];cur=None;last=None
    for pg in range(p0,p1+1):
        for n,a in key.get(pg,[]):
            if cur is None or (last is not None and n<=last) or (n==1 and last!=0):
                cur={'pages':[pg,pg],'items':[]};runs.append(cur)
            cur['items'].append((pg,n,a));cur['pages'][1]=pg;last=n
    for k,r in enumerate(runs):
        sk=f"s{len(sets)+1:02d}"
        sub=''
        if len(runs)>1:
            if title.startswith('실전'): sub=f' {k+1}회'
            else: sub=[' 유형',' LEVEL 2',' LEVEL 3'][k] if not title.startswith(('Ⅲ','Ⅳ')) else [' 유형',' 심화',' LEVEL 1~3'][k] if k<3 else f' ({k+1})'
        its=[]
        for pg,n,a in r['items']:
            it=items[(pg,n)];no=str(n)
            os.makedirs(f'{R}/{sk}',exist_ok=True);shutil.copy(f"{W}/crops2/{it['img']}",f'{R}/{sk}/{no}.jpg')
            its.append([no,pg,it['w'],it['h']])
            if any(c in a for c in '★◆⚠'): flags.append((sk,pg,n,a))
            answers[f'{sk}:{no}']=re.sub(r'[★◆⚠]','',a).strip()
        sets.append({'key':sk,'title':short+sub,'pages':r['pages'],'items':its})
print('sets',len(sets),'items',sum(len(s['items']) for s in sets))
for s in sets: print(s['key'],s['title'],s['pages'],len(s['items']),s['items'][0][0],'~',s['items'][-1][0])
json.dump({'id':'b12','title':'1-2 중간·기말 시험대비집','grade':7,'sets':sets,'answers':answers},open(W+'/b12.json','w'),ensure_ascii=False,separators=(',',':'))
print('flags',flags)
