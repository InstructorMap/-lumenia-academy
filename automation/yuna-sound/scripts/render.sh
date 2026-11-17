#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IN="$ROOT/input"
OUT="$ROOT/output"
mkdir -p "$OUT"
test -s "$IN/track.wav" || { echo "Falta input/track.wav"; exit 1; }
test -s "$IN/visual.jpg" || { echo "Falta input/visual.jpg"; exit 1; }
ffprobe -v error "$IN/track.wav" >/dev/null
ffprobe -v error "$IN/visual.jpg" >/dev/null
DURATION="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$IN/track.wav")"
ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 24 -i "$IN/visual.jpg" -i "$IN/track.wav" -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p" -c:v libx264 -preset veryfast -crf 23 -r 24 -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT/yuna-full.mp4"
for n in 1 2 3; do
  START="$(awk -v d="$DURATION" -v n="$n" 'BEGIN{v=(d-30)*((n-1)/3); if(v<0)v=0; printf "%.2f",v}')"
  ffmpeg -hide_banner -loglevel error -y -ss "$START" -loop 1 -framerate 24 -i "$IN/visual.jpg" -ss "$START" -i "$IN/track.wav" -t 30 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p" -c:v libx264 -preset veryfast -crf 24 -r 24 -c:a aac -b:a 160k -shortest -movflags +faststart "$OUT/yuna-short-$n.mp4"
done
printf 'YUNA Sound Holistic\nComposición original — confirmar autoría, derechos y nombre de pista antes de publicar.\nCanal: https://www.youtube.com/@YunaSoundHolistic\nAcademia: https://yuna-academy.vercel.app/\n' > "$OUT/metadata.txt"
echo "Render completo: $OUT"
