#!/usr/bin/env python3
"""YUNA IA optimizer: nondestructive crops, alpha inspection, optional background removal."""
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"resources/ia/manifest.json"
OUT=ROOT/"generated/optimized"
SIZES={"reel":(1080,1920),"story":(1080,1920),"square":(1080,1080),"landscape":(1920,1080),"thumbnail":(1280,720)}

def focal_crop(im,size,focus_x=.5,focus_y=.5):
    w,h=im.size; tw,th=size
    scale=max(tw/w,th/h)
    nw,nh=math.ceil(w*scale),math.ceil(h*scale)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    left=max(0,min(nw-tw,round((nw-tw)*focus_x)))
    top=max(0,min(nh-th,round((nh-th)*focus_y)))
    return im.crop((left,top,left+tw,top+th))

def inspect_alpha(im):
    if "A" not in im.getbands():return False
    lo,hi=im.getchannel("A").getextrema()
    return lo<255

def remove_solid_bg(im,tolerance=24,feather=1.0):
    """Conservative removal of connected near-uniform border pixels.
    NOT a checkerboard remover or AI segmentation tool."""
    from collections import deque
    im=im.convert("RGBA"); w,h=im.size
    if w*h>4_000_000: im.thumbnail((1800,1800),Image.Resampling.LANCZOS);w,h=im.size
    px=im.load()
    samples=[px[0,0][:3],px[w-1,0][:3],px[0,h-1][:3],px[w-1,h-1][:3]]
    bg=tuple(sorted(p[c] for p in samples)[len(samples)//2] for c in range(3))
    if max(max(abs(p[c]-bg[c]) for c in range(3)) for p in samples)>tolerance:
        raise ValueError("Border colors are not uniform: refusing destructive background removal")
    seen=bytearray(w*h);q=deque()
    for x in range(w):
        q.append((x,0));q.append((x,h-1))
    for y in range(h):
        q.append((0,y));q.append((w-1,y))
    while q:
        x,y=q.popleft();k=y*w+x
        if seen[k]:continue
        seen[k]=1
        if max(abs(px[x,y][c]-bg[c]) for c in range(3))>tolerance:continue
        px[x,y]=(px[x,y][0],px[x,y][1],px[x,y][2],0)
        if x>0:q.append((x-1,y))
        if x+1<w:q.append((x+1,y))
        if y>0:q.append((x,y-1))
        if y+1<h:q.append((x,y+1))
    if feather:
        a=im.getchannel("A").filter(ImageFilter.GaussianBlur(feather))
        im.putalpha(a)
    return im

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--formats",default="reel,square,landscape")
    p.add_argument("--remove-solid-background",action="store_true",help="Opt-in: only near-uniform backgrounds")
    p.add_argument("--tolerance",type=int,default=24)
    p.add_argument("--focus-x",type=float,default=.5)
    p.add_argument("--focus-y",type=float,default=.5)
    args=p.parse_args()
    formats=[x.strip() for x in args.formats.split(",")]
    if any(x not in SIZES for x in formats):p.error("Unknown format")
    if not (0<=args.focus_x<=1 and 0<=args.focus_y<=1):p.error("Focus must be in [0,1]")
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True,exist_ok=True)
    report=[]
    for asset in data["assets"]:
        path=ROOT.parents[1]/asset["path"]
        if not path.exists():
            report.append({"id":asset["id"],"error":"missing source","path":str(path)});continue
        try:
            with Image.open(path) as source:
                im=ImageOps.exif_transpose(source).convert("RGBA")
            alpha=inspect_alpha(im)
            kind=asset["category"]
            record={"id":asset["id"],"source":asset["path"],"original_size":list(im.size),"real_alpha":alpha,"outputs":[]}
            if kind=="background":
                for fmt in formats:
                    dest=OUT/fmt/(path.stem+".png");dest.parent.mkdir(parents=True,exist_ok=True)
                    focal_crop(im,SIZES[fmt],args.focus_x,args.focus_y).save(dest,optimize=True)
                    record["outputs"].append(str(dest.relative_to(ROOT)))
            else:
                if not alpha and args.remove_solid_background:
                    im=remove_solid_bg(im,args.tolerance)
                    alpha=inspect_alpha(im)
                if not alpha:
                    record["warning"]="No real alpha: retained as opaque; not suitable for transparent compositing"
                dest=OUT/"layers"/(path.stem+".png");dest.parent.mkdir(parents=True,exist_ok=True)
                im.save(dest,optimize=True)
                record["real_alpha_after"]=alpha
                record["outputs"].append(str(dest.relative_to(ROOT)))
            report.append(record)
        except Exception as e:report.append({"id":asset["id"],"error":str(e)})
    (OUT/"report.json").write_text(json.dumps({"formats":formats,"assets":report},ensure_ascii=False,indent=2),encoding="utf-8")
    errors=[x for x in report if "error" in x]
    print(f"Processed {len(report)} assets, errors={len(errors)}, output={OUT}")
    if errors:raise SystemExit(1)

if __name__=="__main__":main()
