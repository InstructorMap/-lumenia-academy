#!/usr/bin/env bash
set -euo pipefail
MUSIC="${1:?Music WAV required}"
CLIP="${2:?Video MP4 required}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/output"
mkdir -p "$OUT"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
# Full horizontal master: use previously approved cinematic motion, not procedural art.
ffmpeg -hide_banner -loglevel error -y -stream_loop -1 -i "$CLIP" -i "$MUSIC" -map 0:v:0 -map 1:a:0 -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p,drawbox=x=0:y=610:w=iw:h=110:color=0x101a2a@0.65:t=fill:enable='gte(t,138)',drawtext=fontfile=$FONT:text='YUNA Academy':fontcolor=0xf0d6a3:fontsize=34:x=(w-text_w)/2:y=624:enable='gte(t,138)',drawtext=fontfile=$FONT:text='yuna-academy.vercel.app':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=675:enable='gte(t,138)'" -c:v libx264 -preset veryfast -crf 22 -r 24 -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT/sakura-full.mp4"
# Three distinct editorial messages and excerpts; source music remains untouched.
TITLES=("Un momento para volver a vos" "Tu curiosidad puede transformarse" "Explora tu proximo aprendizaje")
SUBS=("YUNA Sound Holistic" "Cursos online en YUNA Academy" "yuna-academy.vercel.app")
STARTS=(10 55 110)
for i in 0 1 2; do
  j=$((i+1))
  title="${TITLES[$i]}"
  sub="${SUBS[$i]}"
  ffmpeg -hide_banner -loglevel error -y -stream_loop -1 -i "$CLIP" -ss "${STARTS[$i]}" -i "$MUSIC" -t 25 -map 0:v:0 -map 1:a:0 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,drawbox=x=50:y=1340:w=980:h=320:color=0x101a2a@0.72:t=fill,drawtext=fontfile=$FONT:text='$title':fontcolor=0xf4dfba:fontsize=42:x=(w-text_w)/2:y=1400,drawtext=fontfile=$FONT:text='$sub':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=1505" -c:v libx264 -preset veryfast -crf 23 -r 24 -c:a aac -b:a 160k -movflags +faststart "$OUT/sakura-short-$j.mp4"
done
cat > "$OUT/sakura-publication-draft.txt" <<'EOF'
BORRADORES PARA REVISAR, NO PUBLICADOS
Video: Sakura Dreams | YUNA Sound Holistic
Descripción sugerida:
Una experiencia instrumental original de YUNA Sound Holistic.
Explorá los cursos y programas de YUNA Academy:
https://yuna-academy.vercel.app/
#YunaSoundHolistic #SakuraDreams #MusicaRelajante
Short 1: Un momento para volver a vos
Short 2: Tu curiosidad puede transformarse | Conocé YUNA Academy
Short 3: Explorá tu próximo aprendizaje | YUNA Academy
Revisar calidad, encuadre, licencia y textos antes de publicar.
EOF
