#!/usr/bin/env python3
"""YUNA Creative Studio: deterministic storyboard, QA and publishing drafts."""
import argparse, hashlib, json, os, random, subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
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
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f=ImageFont.truetype(font,60)
    for i,item in enumerate(backgrounds[:3]):
        src=ROOT/item["path"]
        with Image.open(src) as image:im=ImageOps.fit(ImageOps.exif_transpose(image).convert("RGB"),(1080,1920),method=Image.Resampling.LANCZOS,centering=(.5,.45))
        d=ImageDraw.Draw(im)
        msg=[course[1],"Aprendé a tu ritmo","YUNA ACADEMY"][i]
        d.rounded_rectangle((50,1510,1030,1810),radius=35,fill=(12,23,41),outline=(212,178,123),width=4)
        d.text((540,1600),msg,font=f,anchor="mm",fill="white",stroke_width=0)
        d.text((540,1710),"yuna-academy.vercel.app",font=ImageFont.truetype(font,35),anchor="mm",fill="#f1d8ae")
        dest=OUT/f"scene-{i+1}.png";im.save(dest,optimize=True)
        scenes.append({"asset":item["id"],"path":str(dest.relative_to(ROOT)),"message":msg})
    # Three scene-based Shorts, with slow independent camera movement via zoompan.
    for n in range(3):
        image=OUT/f"scene-{n+1}.png";video=OUT/f"yuna-short-{n+1}.mp4"
        vf="scale=1200:2134,zoompan=z='min(zoom+0.0008,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=24,format=yuv420p"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","24","-i",str(image),"-i",str(audio),"-t","24","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","24","-c:a","aac","-b:a","160k","-shortest",str(video)])
    # Verify media streams and prohibit accidental publishing.
    qa=[]
    for n in range(3):
        video=OUT/f"yuna-short-{n+1}.mp4"
        streams=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(video)]))["streams"]
        kinds={s["codec_type"] for s in streams}
        ok=video.stat().st_size>100_000 and {"video","audio"}<=kinds
        qa.append({"file":video.name,"passed":ok,"streams":sorted(kinds),"bytes":video.stat().st_size})
    if not all(x["passed"] for x in qa):raise SystemExit("QA failed")
    record={"seed":a.seed,"created_at":datetime.now(timezone.utc).isoformat(),"course":course[0],"scenes":scenes,"qa":qa,"publication_status":"draft_requires_approval"}
    (OUT/"production.json").write_text(json.dumps(record,ensure_ascii=False,indent=2))
    (OUT/"publishing-draft.txt").write_text("YUNA Academy | "+course[0]+"\n"+course[1]+"\nConocé nuestros cursos: https://yuna-academy.vercel.app/\nCanal: https://www.youtube.com/@YunaSoundHolistic\nESTADO: BORRADOR, NO PUBLICADO\n",encoding="utf-8")
    previous["productions"]=(previous["productions"]+[record])[-52:]
    history.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+"\n")
    print("YUNA production complete: 3 reviewed-by-technical-QA drafts; human visual review required")
if __name__=="__main__":main()
