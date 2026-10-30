#!/usr/bin/env python3
"""페르마(매쓰플랫형) 시험지 양식으로 PDF 만들기.

사용법:
  python3 make_exam_pdf.py --images <문제이미지폴더> --out 시험지.pdf \
      --title "[중1-2] 기말대비1" --sub "기본 도형 ~ 통계" [--label 내신대비] \
      [--answers 정답.txt] [--tags 태그.txt] [--answers-only 빠른정답.pdf] [--start 1]

  문제이미지폴더: 문제 한 개씩 잘린 이미지(01.png, 02.jpg …) — 파일 이름 순서가 문제 순서
  정답.txt: 한 줄에 하나씩 (①, ②,⑤, 10cm², 1/3 …). 있으면 마지막에 빠른정답 쪽이 붙어요
  태그.txt: 한 줄에 하나씩 문제 위 작은 태그(예: "| 삼각형의 무게중심"). 비워 두면 생략
"""
import argparse, glob, os
from PIL import Image, ImageDraw, ImageFont

BLUE=(0,171,255); INK=(27,27,27); GRAY=(124,124,124); LINE=(227,227,227); SKY=(159,220,251)
PW,PH,M=1240,1754,62; CW=PW-2*M; BOTTOM=PH-112
def font(bold,size):
    for f in (['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'] if bold else ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'])+glob.glob('/usr/share/fonts/**/*CJK*.tt*',recursive=True)+glob.glob('/System/Library/Fonts/AppleSDGothicNeo.ttc')+glob.glob('C:/Windows/Fonts/malgun*.ttf'):
        if os.path.exists(f): return ImageFont.truetype(f,size)
    return ImageFont.load_default()

class Doc:
    def __init__(s,a,n): s.a=a; s.n=n; s.pages=[]; s.im=None
    def page(s,first=False):
        if s.im: s.pages.append(s.im)
        s.im=Image.new('RGB',(PW,PH),'white'); d=s.d=ImageDraw.Draw(s.im); k=len(s.pages)+1
        d.rectangle([0,0,PW,44],fill=BLUE)
        d.text((M,PH-60),f'{k:02d}',font=font(True,26),fill=GRAY); d.rectangle([M+52,PH-53,PW-M,PH-51],fill=SKY)
        if first:
            d.rounded_rectangle([-60,134,310,290],radius=40,fill=BLUE)
            d.text((284,200),s.a.label,font=font(True,36),fill='white',anchor='rs')
            d.text((284,248),f'{s.n}문제 | 페르마 수학학원',font=font(True,23),fill='white',anchor='rs')
            d.text((338,206),s.a.title,font=font(True,48),fill=INK,anchor='ls')
            if s.a.sub: d.text((338,252),s.a.sub,font=font(True,26),fill=GRAY,anchor='ls')
            d.text((338,334),'이름',font=font(True,21),fill=(85,85,85),anchor='ls'); d.rectangle([384,344,564,345],fill=(119,119,119))
            s.top=400
        else:
            f=font(True,28); d.text((M+6,96),s.a.label,font=f,fill=BLUE,anchor='ls'); w=d.textlength(s.a.label+' ',font=f)
            d.text((M+6+w,96),s.a.title,font=f,fill=INK,anchor='ls'); d.rectangle([M,116,PW-M,118],fill=SKY)
            s.top=158
        s.y=s.top
    def done(s,out):
        s.pages.append(s.im); s.pages[0].save(out,save_all=True,append_images=s.pages[1:],resolution=150)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--images',required=True); p.add_argument('--out',required=True)
    p.add_argument('--title',required=True); p.add_argument('--sub',default=''); p.add_argument('--label',default='내신대비')
    p.add_argument('--answers'); p.add_argument('--tags'); p.add_argument('--answers-only'); p.add_argument('--start',type=int,default=1)
    a=p.parse_args()
    fs=sorted(f for f in glob.glob(os.path.join(a.images,'*')) if f.lower().endswith(('.png','.jpg','.jpeg','.webp')))
    tags=open(a.tags,encoding='utf8').read().split('\n') if a.tags else []
    ans=[l.strip() for l in open(a.answers,encoding='utf8').read().strip().split('\n')] if a.answers else []
    n=len(fs); doc=Doc(a,n); doc.page(True)
    GAP=56; COLW=(CW-GAP)//2; NUMW=78; SOLVE=120; col=0
    def divider(): doc.d.rectangle([M+COLW+GAP//2,doc.top-6,M+COLW+GAP//2+1,BOTTOM],fill=LINE)
    for i,f in enumerate(fs):
        im=Image.open(f).convert('RGB'); sc=min((COLW-NUMW)/im.width,0.78); iw,ih=int(im.width*sc),int(im.height*sc)
        tag=tags[i].strip() if i<len(tags) else ''; th=40 if tag else 0
        if doc.y+th+ih+SOLVE>BOTTOM and doc.y>doc.top:
            if col==0: col=1; doc.y=doc.top
            else: divider(); doc.page(); col=0
        cx=M+col*(COLW+GAP); d=doc.d
        if tag: d.text((cx,doc.y+20),tag,font=font(False,18),fill=GRAY,anchor='lm'); doc.y+=th
        d.text((cx,doc.y+44),f'{a.start+i:02d}',font=font(True,46),fill=BLUE,anchor='ls')
        doc.im.paste(im.resize((iw,ih),Image.LANCZOS),(cx+NUMW,doc.y)); doc.y+=ih+SOLVE
    divider()
    def answer_page(d0):
        d0.page(False); d=d0.d; y=d0.y
        d.text((PW//2,y+30),'빠른정답',font=font(True,32),fill=INK,anchor='ms'); d.rectangle([PW//2-110,y-12,PW//2+110,y-11],fill=(207,207,207)); d.rectangle([PW//2-110,y+52,PW//2+110,y+53],fill=(207,207,207))
        y+=92; cw=CW//3; d.rectangle([M,y,PW-M,y+2],fill=(51,51,51))
        for r in range(0,len(ans),3):
            if y+74>BOTTOM: d.rectangle([M,y,PW-M,y+2],fill=(51,51,51)); d0.page(False); d=d0.d; y=d0.y+10; d.rectangle([M,y,PW-M,y+2],fill=(51,51,51))
            for k,t in enumerate(ans[r:r+3]):
                cx=M+k*cw; d.text((cx+14,y+46),f'{a.start+r+k:02d}',font=font(True,25),fill=BLUE,anchor='ls')
                d.text((cx+80,y+46),t,font=font(False,25),fill=INK,anchor='ls')
                if k: d.rectangle([cx,y,cx+1,y+74],fill=(208,208,208))
            y+=74; d.rectangle([M,y,PW-M,y+1],fill=(208,208,208))
        d.rectangle([M,y,PW-M,y+2],fill=(51,51,51))
    if ans and not a.answers_only: answer_page(doc)
    doc.done(a.out)
    if ans and a.answers_only:
        d2=Doc(a,n); d2.im=None; answer_page(d2); d2.done(a.answers_only)
    print('wrote',a.out,len(doc.pages),'pages')
if __name__=='__main__': main()
