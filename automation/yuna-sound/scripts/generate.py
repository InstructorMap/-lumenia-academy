#!/usr/bin/env python3
"""Deterministic original ambient sketch, no external music service or samples."""
import math, wave, random, datetime, struct, os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
root=Path(__file__).resolve().parents[1]
out=root/'input';out.mkdir(parents=True,exist_ok=True)
seed=int(os.environ.get('YUNA_SEED',datetime.date.today().strftime('%G%V')))
rng=random.Random(seed)
sr=22050
duration=150
n=sr*duration
audio=np.zeros(n,dtype=np.float32)
scale=[0,2,4,7,9]
root_note=rng.choice([48,50,53,55,57])
progressions=[[0,3,4,1],[0,4,1,3],[0,1,3,4]]
prog=rng.choice(progressions)
def note(hz,start,length,amp,kind='soft'):
    a=int(start*sr);b=min(n,a+int(length*sr))
    if b<=a:return
    t=np.arange(b-a,dtype=np.float32)/sr
    attack=np.minimum(1,t/0.16)
    release=np.minimum(1,(length-t)/1.6)
    env=np.maximum(0,attack*release)*np.exp(-t/(length*1.8))
    if kind=='bell':
        signal=np.sin(2*np.pi*hz*t)+.28*np.sin(2*np.pi*2.01*hz*t)+.12*np.sin(2*np.pi*3.97*hz*t)
        env*=np.exp(-t/2.8)
    else:
        signal=np.sin(2*np.pi*hz*t)+.25*np.sin(2*np.pi*2*hz*t)+.1*np.sin(2*np.pi*3*hz*t)
    audio[a:b]+=amp*env*signal
def freq(m):return 440*2**((m-69)/12)
for bar in range(25):
    start=bar*6
    degree=prog[(bar//2)%4]
    chord=[root_note+scale[degree],root_note+scale[(degree+2)%5]+(12 if degree+2>=5 else 0),root_note+scale[(degree+4)%5]+(12 if degree+4>=5 else 0)]
    for pitch in chord:note(freq(pitch),start,6,.075)
    note(freq(chord[0]-12),start,5.8,.07)
    for step in range(3):
        pitch=chord[rng.randrange(3)]+12
        note(freq(pitch),start+step*2,2.8,.065,'bell')
# gentle stereo echo and fade
delay=int(.34*sr)
echo=np.zeros_like(audio);echo[delay:]=audio[:-delay]*.22
audio+=echo
fade=np.minimum(1,np.arange(n)/float(sr*3))*np.minimum(1,(n-np.arange(n))/float(sr*5))
audio*=fade
peak=max(float(np.max(np.abs(audio))),1e-6)
pcm=(audio/peak*.78*32767).astype('<i2')
with wave.open(str(out/'track.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
W,H=1600,900
im=Image.new('RGB',(W,H))
px=im.load()
for y in range(H):
    for x in range(W):
        glow=max(0,1-math.hypot(x-W*.68,y-H*.36)/(W*.5))
        px[x,y]=(int(13+34*glow),int(22+23*glow),int(47+36*glow))
d=ImageDraw.Draw(im,'RGBA')
d.ellipse((940,130,1190,380),fill=(245,222,177,240))
for i in range(7):
    yy=590+i*52
    d.polygon([(0,H),(0,yy+35),(300,yy-55),(680,yy+30),(1050,yy-95),(1600,yy+30),(1600,H)],fill=(13+i*2,21+i*2,37+i*2,220))
for i in range(110):
    x=rng.randint(0,W);y=rng.randint(0,600);r=rng.randint(2,8)
    d.ellipse((x-r,y-r,x+r,y+r),fill=(243,168,190,rng.randint(80,210)))
d.line([(0,110),(370,240),(650,210)],fill=(65,45,61,240),width=19)
im=im.filter(ImageFilter.GaussianBlur(1))
im.save(out/'visual.jpg',quality=90)
print('Generated original procedural sketch and artwork; review before publishing. seed=',seed)
