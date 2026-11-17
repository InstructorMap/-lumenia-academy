#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/creative-studio/output"
mkdir -p "$OUT"
python "$ROOT/creative-studio/scripts/render_pilot_frames.py"
MUSIC="${1:?Usage: render_pilot.sh approved-music.wav}"
test -s "$MUSIC"
mkdir -p "$OUT/segments"
DURS=(4 6 6 4 4)
for i in 1 2 3 4 5; do
  idx=$((i-1))
  printf -v num '%02d' "$i"
  ffmpeg -hide_banner -loglevel error -y -loop 1 -framerate 30 -i "$OUT/frames/scene-$num.png" -t "${DURS[$idx]}" -vf "scale=1100:1956,zoompan=z='min(zoom+0.00025,1.06)':d=1:x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':s=1080x1920:fps=30,format=yuv420p" -c:v libx264 -preset veryfast -crf 22 -an "$OUT/segments/$num.mp4"
done
printf "file '%s'\n" "$OUT"/segments/*.mp4 > "$OUT/concat.txt"
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$OUT/concat.txt" -ss 20 -i "$MUSIC" -t 24 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "afade=t=in:st=0:d=0.5,afade=t=out:st=22.5:d=1.5" -movflags +faststart "$OUT/yuna-academy-piloto-01.mp4"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "$OUT/yuna-academy-piloto-01.mp4"
