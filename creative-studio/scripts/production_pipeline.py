#!/usr/bin/env python3
"""YUNA Creative Studio: deterministic storyboard, QA and publishing drafts."""
import argparse, hashlib, json, os, random, subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[2]
STUDIO=ROOT/"creative-studio"
MANIFEST=STUDIO/"resources/ia/manifest.json"
OUT=STUDIO/"generated/production"
COURSES=[("Tarot","Descubrí el universo del Tarot"),("Reiki","Explorá el bienestar con Reiki"),("Meditación","Encontrá tu espacio de calma"),("Aromaterapia","Descubrí la aromaterapia"),("Flores de Bach","Conocé las flores de Bach")]
def run(args):
    subprocess.run(args,cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument("--seed",type=int,default=int(datetime.now(timezone.utc).strftime("%G%V")));p.add_argument("--skip-music",action="store_true");a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    data=json.loads(MANIFEST.read_text())
    backgrounds=[x for x in data["assets"] if x["category"]=="background" and (ROOT/x["path"]).exists()]
    if len(backgrounds)<3:raise SystemExit("Need at least three existing backgrounds")
    rng=random.Random(a.seed);rng.shuffle(backgrounds)
    course=COURSES[a.seed%len(COURSES)]
    if not a.skip_music:
        env=os.environ.copy();env["YUNA_SEED"]=str(a.seed)
        subprocess.run(["python","automation/yuna-sound/scripts/generate.py"],cwd=ROOT,env=env,check=True)
    audio=ROOT/"automation/yuna-sound/input/track.wav"
    if not audio.exists():raise SystemExit("Missing generated audio")
    history=STUDIO/"production-history.json"
    previous=json.loads(history.read_text()) if history.exists() else {"productions":[]}
    used={z["asset"] for v in previous["productions"][-4:] for z in v.get("scenes",[])}
    backgrounds.sort(key=lambda x:(x["id"] in used,rng.random()))
    scenes=[]
    crop_audit=[]
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    import statistics
    def source_crop(im):
        # Identify embedded blurred top/bottom padding by low horizontal detail.
        w,h=im.size
        sample=im.resize((128,256))
        scores=[]
        for y in range(256):
            pixels=[sample.getpixel((x,y)) for x in range(0,128,8)]
            scores.append(sum(statistics.pstdev([p[c] for p in pixels]) for c in range(3)))
        mid=statistics.median(scores[88:168])
        active=[i for i,v in enumerate(scores) if v>max(18,mid*.33)]
        if len(active)>65:
            top=max(0,min(active)-2);bottom=min(256,max(active)+3)
            if 65<bottom-top<210:
                return im.crop((0,round(top*h/256),w,round(bottom*h/256)))
        return im
    transparent=[]
    for item in data["assets"]:
        if item["category"]!="overlay_candidate" or not (ROOT/item["path"]).exists():continue
        with Image.open(ROOT/item["path"]) as candidate:
            if "A" in candidate.getbands() and candidate.getchannel("A").getextrema()[0]<245:
                transparent.append(item)
    print("Verified transparent layers:",len(transparent))
    # Three different 8-second shots per Short. Each shot contains a moving
    # background, an independently moving alpha layer and fading typography.
    for n in range(3):
        clips=[]
        for shot in range(3):
            item=backgrounds[(n*3+shot)%len(backgrounds)]
            with Image.open(ROOT/item["path"]) as raw:
                original=ImageOps.exif_transpose(raw).convert("RGB")
                im=source_crop(original)
                crop_audit.append({"asset":item["id"],"original":list(original.size),"cropped":list(im.size),"crop_applied":im.size!=original.size})
            im=ImageOps.fit(im,(1080,1920),method=Image.Resampling.LANCZOS,centering=(.5,.45))
            base=OUT/f"background-{n}-{shot}.png";im.save(base,optimize=True)
            fg=Image.new("RGBA",(1080,1920),(0,0,0,0))
            alpha_id="procedural"
            if transparent:
                layer=transparent[(n+shot)%len(transparent)]
                with Image.open(ROOT/layer["path"]) as raw:
                    decal=raw.convert("RGBA");decal.thumbnail((780,800),Image.Resampling.LANCZOS)
                fg.alpha_composite(decal,(1080-decal.width-35,120))
                alpha_id=layer["id"]
            else:
                draw=ImageDraw.Draw(fg)
                for k in range(35):
                    x=rng.randrange(50,1030);y=rng.randrange(120,1450);r=rng.randrange(2,8)
                    draw.ellipse((x-r,y-r,x+r,y+r),fill=(255,212,161,rng.randrange(75,175)))
            fp=OUT/f"foreground-{n}-{shot}.png";fg.save(fp)
            tp=Image.new("RGBA",(1080,1920),(0,0,0,0))
            td=ImageDraw.Draw(tp)
            # No opaque cards. Typography is a separately animated RGBA plane.
            td.text((80,1400),"YUNA",font=ImageFont.truetype(font,95),fill="#f5e5c5")
            td.line((80,1515,315,1515),fill="#d8b679",width=4)
            msg=[course[1],"Aprendé a tu ritmo","Explorá YUNA Academy"][shot]
            words=msg.split();lines=[];line=""
            face=ImageFont.truetype(font,52)
            for word in words:
                test=(line+" "+word).strip()
                if td.textbbox((0,0),test,font=face)[2]>900 and line:
                    lines.append(line);line=word
                else:line=test
            if line:lines.append(line)
            for j,ln in enumerate(lines):
                td.text((80,1580+j*70),ln,font=face,fill="white",stroke_width=2,stroke_fill="#101020")
            td.text((80,1820),"yuna-academy.vercel.app",font=ImageFont.truetype(regular,35),fill="#f5d7a8")
            txt=OUT/f"text-{n}-{shot}.png";tp.save(txt)
            clip=OUT/f"clip-{n}-{shot}.mp4"
            vf=("[0:v]scale=1140:2027,zoompan=z='min(zoom+0.00020,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=24,format=rgba[bg];"
                "[1:v]format=rgba[decal];[bg][decal]overlay=x='12+18*sin(t*0.7)':y='12+10*cos(t*0.6)':eval=frame:shortest=1[mid];"
                "[2:v]format=rgba,fade=t=in:st=0.6:d=1:alpha=1[words];"
                "[mid][words]overlay=0:0:shortest=1,format=yuv420p[out]")
            run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","24","-i",str(base),
                 "-loop","1","-framerate","24","-i",str(fp),"-loop","1","-framerate","24","-i",str(txt),
                 "-filter_complex",vf,"-map","[out]","-t","8","-r","24","-c:v","libx264","-preset","ultrafast","-crf","26",str(clip)])
            if not clip.exists() or clip.stat().st_size<100_000:raise SystemExit(f"Missing or empty animated scene: {clip}")
            clips.append(clip)
            scenes.append({"asset":item["id"],"message":msg,"overlay":alpha_id})
        playlist=OUT/f"concat-{n}.txt"
        playlist.write_text("".join("file '"+c.name+"'\\n" for c in clips))
        video=OUT/f"yuna-short-{n+1}.mp4"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(playlist),
             "-i",str(audio),"-map","0:v","-map","1:a","-t","24","-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",str(video)])
    # Verify media streams and prohibit accidental publishing.
    qa=[]
    for n in range(3):
        video=OUT/f"yuna-short-{n+1}.mp4"
        streams=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(video)]))["streams"]
        kinds={s["codec_type"] for s in streams}
        ok=video.stat().st_size>100_000 and {"video","audio"}<=kinds and any(z.get("width")==1080 and z.get("height")==1920 for z in streams if z["codec_type"]=="video")
        duration=float(json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-of","json",str(video)]))["format"]["duration"])
        ok=ok and 23.5<=duration<=24.5 and len(clips)==3
        qa.append({"file":video.name,"passed":ok,"streams":sorted(kinds),"bytes":video.stat().st_size,"duration_seconds":round(duration,2),"animated_scenes":3})
    if not all(x["passed"] for x in qa):raise SystemExit("QA failed")
    (OUT/"visual-qa.json").write_text(json.dumps({"transparent_overlays_available":len(transparent),"procedural_fallback_used":len(transparent)==0,"crop_audit":crop_audit,"shots_per_short":3,"requires_human_visual_approval":True},ensure_ascii=False,indent=2))
    record={"seed":a.seed,"created_at":datetime.now(timezone.utc).isoformat(),"course":course[0],"scenes":scenes,"qa":qa,"publication_status":"draft_requires_approval"}
    (OUT/"production.json").write_text(json.dumps(record,ensure_ascii=False,indent=2))
    (OUT/"publishing-draft.txt").write_text("YUNA Academy | "+course[0]+"\n"+course[1]+"\nConocé nuestros cursos: https://yuna-academy.vercel.app/\nCanal: https://www.youtube.com/@YunaSoundHolistic\nESTADO: BORRADOR, NO PUBLICADO\n",encoding="utf-8")
    previous["productions"]=(previous["productions"]+[record])[-52:]
    history.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+"\n")
    print("YUNA production complete: 3 reviewed-by-technical-QA drafts; human visual review required")
if __name__=="__main__":main()
