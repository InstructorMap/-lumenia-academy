#!/usr/bin/env bash
# Add YUNA Academy branding to approved, existing videos without changing original masters.
set -euo pipefail
SRC="${1:?Usage: bash brand.sh input.mp4 output.mp4 [full|short]}"
DST="${2:?Output path required}"
KIND="${3:-short}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
test -s "$SRC" || { echo "Input not found: $SRC"; exit 1; }
mkdir -p "$(dirname "$DST")"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DUR="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$SRC")"
if [ "$KIND" = "full" ]; then
  SIZE=34; Y=60; END=12
else
  SIZE=45; Y=110; END=6
fi
# Safe margins, translucent backing and timed call-to-action; no misleading claims.
# Use drawtext for portability; later replace with approved logo PNG and motion graphics.
FILTER="drawbox=x=0:y=0:w=iw:h=150:color=0x101a2a@0.55:t=fill:enable='between(t,0,5)',drawtext=fontfile=$FONT:text='YUNA Sound Holistic':fontsize=$SIZE:fontcolor=white:x=(w-text_w)/2:y=$Y:enable='between(t,0,5)',drawbox=x=0:y=ih-190:w=iw:h=190:color=0x101a2a@0.72:t=fill:enable='gte(t,max(0,$DUR-$END))',drawtext=fontfile=$FONT:text='Descubri YUNA Academy':fontsize=$SIZE:fontcolor=0xf1d59a:x=(w-text_w)/2:y=h-145:enable='gte(t,max(0,$DUR-$END))',drawtext=fontfile=$FONT:text='yuna-academy.vercel.app':fontsize=$((SIZE*3/4)):fontcolor=white:x=(w-text_w)/2:y=h-80:enable='gte(t,max(0,$DUR-$END))'"
ffmpeg -hide_banner -loglevel error -y -i "$SRC" -vf "$FILTER" -c:v libx264 -preset medium -crf 20 -c:a copy -movflags +faststart "$DST"
echo "Branded draft: $DST"
