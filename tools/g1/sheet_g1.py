import json,sys,os
from PIL import Image,ImageDraw
W=sys.argv[1];D=W+'/crops2';out=W+'/review';os.makedirs(out,exist_ok=True)
items=sorted(json.load(open(D+'/items.json')),key=lambda i:(i['page'],i['no']))
TW,COLS,MAXH=300,6,2400
tiles=[]
for it in items:
    im=Image.open(f"{D}/{it['img']}").convert('RGB');sc=TW/im.width;im=im.resize((TW,max(1,int(im.height*sc))))
    t=Image.new('RGB',(TW+6,im.height+18),(255,228,228));t.paste(im,(3,16))
    ImageDraw.Draw(t).text((4,2),f"p{it['page']} #{it['no']}"+(' +cont' if it.get('cont') else ''),fill=(200,0,0));tiles.append(t)
rows=[tiles[i:i+COLS] for i in range(0,len(tiles),COLS)]
sheets=[];cur=[];h=0
for r in rows:
    rh=max(t.height for t in r)+4
    if h+rh>MAXH and cur: sheets.append(cur);cur=[];h=0
    cur.append(r);h+=rh
if cur: sheets.append(cur)
for k,rs in enumerate(sheets):
    H=sum(max(t.height for t in r)+4 for r in rs);sh=Image.new('RGB',(COLS*(TW+10),H),'white');y=0
    for r in rs:
        for i,t in enumerate(r): sh.paste(t,(i*(TW+10),y))
        y+=max(t.height for t in r)+4
    sh.save(f'{out}/s{k:02d}.jpg',quality=68)
print(len(sheets))
