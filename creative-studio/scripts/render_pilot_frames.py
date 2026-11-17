#!/usr/bin/env python3
"""Render five distinct editorial frames from existing repository images."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math
import io
import cairosvg
R=Path(__file__).resolve().parents[2]
O=R/"creative-studio/output/frames"; O.mkdir(parents=True,exist_ok=True)
W,H=1080,1920
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,bold=False): return ImageFont.truetype(BOLD if bold else FONT,n)
def cover(path,w,h):
    im=Image.open(R/path).convert("RGBA")
    ratio=min(w/im.width,h/im.height)
    im=im.resize((int(im.width*ratio),int(im.height*ratio)),Image.Resampling.LANCZOS)
    return im
def centered(im,asset,box):
    x,y,w,h=box
    item=cover(asset,w,h)
    im.alpha_composite(item,(x+(w-item.width)//2,y+(h-item.height)//2))
def svg_layer(path):
    data=cairosvg.svg2png(url=str(R/path),output_width=W,output_height=H)
    return Image.open(io.BytesIO(data)).convert("RGBA")

def base(i):
    im=Image.new("RGBA",(W,H))
    px=im.load()
    for y in range(H):
        t=y/H
        c=tuple(int(a*(1-t)+b*t) for a,b in zip((248,242,230),(224,209,184)))
        ImageDraw.Draw(im).line((0,y,W,y),fill=c+(255,))
    bg=["sakura-dawn.svg","temple-night.svg","sakura-dawn.svg","temple-night.svg","sakura-dawn.svg"][i]
    backdrop=svg_layer("creative-studio/resources/backgrounds/"+bg)
    backdrop.putalpha(90 if i in (1,2,3) else 140)
    im.alpha_composite(backdrop)
    d=ImageDraw.Draw(im)
    for k in range(5):
        d.ellipse((W//2-(390+k*70),230-k*65,W//2+(390+k*70),950+k*65),outline=(175,146,102,30),width=3)
    d.line((90,1530,990,1530),fill=(158,128,88,110),width=3)
    d.text((90,145),"YUNA  /  ACADEMY",font=font(35,True),fill=(68,66,61))
    overlay=svg_layer("creative-studio/resources/overlays/"+("sakura-petals.svg" if i%2==0 else "gold-sparkles.svg"))
    im.alpha_composite(overlay)
    d.text((90,1620),"DESCUBRI YUNA ACADEMY",font=font(38,True),fill=(45,56,72))
    d.text((90,1688),"yuna-academy.vercel.app",font=font(30),fill=(91,83,69))
    return im
def yuna_emblem(im):
    """Original vector-like YUNA wordmark; never imports legacy LUMENIA assets."""
    d=ImageDraw.Draw(im)
    cx,cy=540,660
    d.ellipse((cx-230,cy-230,cx+230,cy+230),outline=(168,133,73),width=8)
    d.arc((cx-184,cy-190,cx+184,cy+175),200,345,fill=(194,154,83),width=10)
    d.ellipse((cx-12,cy-188,cx+12,cy-164),fill=(194,154,83))
    for dx,dy in [(-70,-40),(0,-90),(70,-40)]:
        d.ellipse((cx+dx-38,cy+dy-65,cx+dx+38,cy+dy+38),outline=(168,133,73),width=7)
    d.text((cx,cy+90),"YUNA",anchor="mm",font=font(115,True),fill=(41,56,73))
    d.text((cx,cy+169),"A C A D E M Y",anchor="mm",font=font(35),fill=(124,98,66))

def headline(im,lines):
    d=ImageDraw.Draw(im)
    y=1130
    for line in lines:
        d.text((90,y),line,font=font(59,True),fill=(42,56,75),stroke_width=0)
        y+=88
frames=[
    (["Hay algo nuevo","por descubrir"],[]),
    (["Explora el universo","del Tarot"],["assets/cursos/tarot.png"]),
    (["Aprende a tu ritmo"],["assets/cursos/reiki.png","assets/cursos/meditacion.png"]),
    (["Cinco caminos","para explorar"],["assets/cursos/aromaterapia.png","assets/cursos/flores_de_bach.png"]),
    (["Tu proximo paso","empieza en YUNA"],["assets/branding/logo_referencia.png"])
]
for i,(lines,assets) in enumerate(frames):
    im=base(i)
    if i in (0,4): centered(im,"assets/branding/file_00000000bc98820e81cf96aab0d1dfa7.png",(110,290,860,760))
    elif len(assets)==1: centered(im,assets[0],(110,290,860,760))
    else:
        centered(im,assets[0],(85,345,440,650))
        centered(im,assets[1],(555,345,440,650))
    headline(im,lines)
    im.convert("RGB").save(O/f"scene-{i+1:02d}.png",optimize=True)
    print("Rendered",i+1)
