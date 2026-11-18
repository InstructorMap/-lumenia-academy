#!/usr/bin/env python3
"""
YUNA Creative Studio V4 — Production Pipeline
Cinematic SVG layers, deterministic motion, brand identity, zero-cost.
Does NOT touch campus, auth, database or the main website.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

# Local engine
sys.path.insert(0, str(Path(__file__).resolve().parent))
from svg_engine import SVGEngine, SVGLayer, CompositionReport, assert_no_png_overlays

ROOT = Path(__file__).resolve().parents[2]
STUDIO = ROOT / "creative-studio"
MANIFEST = STUDIO / "resources" / "ia" / "manifest.json"
OUT = STUDIO / "generated" / "production"
PRESETS_PATH = STUDIO / "config" / "svg_presets.json"
HISTORY = STUDIO / "production-history.json"

# Official courses — only verified information, no invented claims
COURSES = [
    ("Tarot", "Descubrí el universo del Tarot"),
    ("Reiki", "Explorá el bienestar con Reiki"),
    ("Meditación", "Encontrá tu espacio de calma"),
    ("Aromaterapia", "Descubrí la aromaterapia"),
    ("Flores de Bach", "Conocé las flores de Bach"),
]

OFFICIAL_URL = "https://yuna-academy.vercel.app/"
BRAND = "YUNA Academy"
MUSIC_BRAND = "Yuna Sound Holistic"

# Visual identity palette (sRGB)
PALETTE = {
    "night_blue": (15, 22, 40),
    "soft_gold": (216, 182, 121),
    "sakura_pink": (245, 210, 220),
    "warm_white": (245, 239, 230),
    "deep_ink": (9, 13, 26),
}


def run(cmd: List[str], cwd: Optional[Path] = None) -> None:
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def load_presets() -> Dict:
    if PRESETS_PATH.exists():
        return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    return {}


def source_crop(im: Image.Image) -> Image.Image:
    """Remove low-detail letterbox bars when present (inherited from V3)."""
    w, h = im.size
    sample = im.resize((128, 256))
    scores = []
    for y in range(256):
        pixels = [sample.getpixel((x, y)) for x in range(0, 128, 8)]
        scores.append(sum(statistics.pstdev([p[c] for p in pixels]) for c in range(3)))
    mid = statistics.median(scores[88:168])
    active = [i for i, v in enumerate(scores) if v > max(18, mid * 0.33)]
    if len(active) > 65:
        top = max(0, min(active) - 2)
        bottom = min(256, max(active) + 3)
        if 65 < bottom - top < 210:
            return im.crop((0, round(top * h / 256), w, round(bottom * h / 256)))
    return im


def prepare_background(path: Path, out_path: Path) -> Tuple[Image.Image, Dict]:
    """Load, crop intelligently and fit to 1080×1920 without stretching."""
    with Image.open(path) as raw:
        original = ImageOps.exif_transpose(raw).convert("RGB")
        cropped = source_crop(original)
        audit = {
            "original": list(original.size),
            "cropped": list(cropped.size),
            "crop_applied": cropped.size != original.size,
        }
    fitted = ImageOps.fit(
        cropped, (1080, 1920), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45)
    )
    fitted.save(out_path, optimize=True)
    return fitted, audit


def build_text_plane(
    course_name: str,
    message: str,
    style: str,
    shot_index: int,
    font_bold: str,
    font_regular: str,
) -> Image.Image:
    """
    Cinematic typography plane.
    No rigid cards, no hard horizontal bands.
    Soft gradient for legibility only.
    """
    tp = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    shade = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)

    # Soft bottom gradient (never a solid card)
    for yy in range(1180, 1920):
        t = (yy - 1180) / 740
        opacity = int(165 * (t ** 1.35))
        sd.line((0, yy, 1079, yy), fill=(*PALETTE["deep_ink"], opacity))

    tp.alpha_composite(shade)
    td = ImageDraw.Draw(tp)

    # SVG brand lockup. This is a provisional typographic brand asset, not a
    # claim that an official YUNA logo SVG has been located in the repository.
    import cairosvg
    brand_svg = STUDIO / "resources" / "branding" / "yuna-academy-lockup.svg"
    if not brand_svg.is_file():
        raise FileNotFoundError(f"Missing SVG brand lockup: {brand_svg}")
    logo = Image.open(BytesIO(cairosvg.svg2png(url=str(brand_svg), output_width=470))).convert("RGBA")
    tp.alpha_composite(logo, (72, 1310))
    td = ImageDraw.Draw(tp)

    # Message (varies by style and shot)
    if style == "A":
        # Emotional / atmospheric
        lines_src = [message, "Un espacio para vos"]
    elif style == "B":
        # Educational
        lines_src = [f"Curso de {course_name}", message]
    else:
        # Conversion
        lines_src = [message, "Empezá cuando quieras"]

    # Word-wrap
    face = ImageFont.truetype(font_bold, 48)
    words = " ".join(lines_src).split()
    lines: List[str] = []
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if td.textbbox((0, 0), test, font=face)[2] > 920 and line:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)

    for j, ln in enumerate(lines[:3]):
        td.text(
            (72, 1510 + j * 62),
            ln,
            font=face,
            fill="white",
            stroke_width=2,
            stroke_fill="#101020",
        )

    # Official CTA
    td.text(
        (72, 1825),
        OFFICIAL_URL.replace("https://", ""),
        font=ImageFont.truetype(font_regular, 32),
        fill="#f5d7a8",
    )

    return tp


def build_ffmpeg_filter(
    duration: float,
    camera: Dict,
    layer_count: int,
    motion_profile: str,
) -> str:
    """
    Construct a professional multi-layer filter graph.
    - Parallax / independent motion per SVG depth
    - Cinematic zoom + gentle pan
    - Fade in/out for text
    - No hard edges, no banding
    """
    z0 = camera.get("zoom_start", 1.0)
    z1 = camera.get("zoom_end", 1.05)
    px = camera.get("pan_x", 0.0)
    py = camera.get("pan_y", 0.0)

    # Background: slow cinematic zoom + pan
    # We pre-scale a bit so zoompan has headroom
    bg = (
        f"[0:v]scale=1188:2112,zoompan="
        f"z='{z0}+({z1}-{z0})*on/{int(duration*24)}':"
        f"x='iw/2-(iw/zoom/2)+{px*80}*sin(on/40)':"
        f"y='ih/2-(ih/zoom/2)+{py*60}*cos(on/35)':"
        f"d=1:s=1080x1920:fps=24,format=rgba[bg]"
    )

    # SVG layers (inputs 1..N) with depth-dependent motion
    parts = [bg]
    last = "bg"
    for i in range(layer_count):
        inp = i + 1
        # Different motion amplitudes by depth / profile
        if motion_profile in ("fall", "fall_slow"):
            ox = f"8+22*sin(t*0.55+{i})"
            oy = f"6+18*cos(t*0.48+{i*0.7})+t*4"
        elif motion_profile in ("float", "sparkle"):
            ox = f"10+16*sin(t*0.9+{i*1.3})"
            oy = f"8+12*cos(t*0.7+{i})"
        elif motion_profile in ("breathe", "pulse_slow"):
            ox = f"4+6*sin(t*0.35)"
            oy = f"3+5*cos(t*0.28)"
        elif motion_profile == "drift":
            ox = f"6+10*sin(t*0.4+{i})"
            oy = f"4+8*cos(t*0.35)"
        else:
            ox = "4"
            oy = "3"

        parts.append(
            f"[{inp}:v]format=rgba,"
            f"fade=t=in:st=0:d=0.8:alpha=1,"
            f"fade=t=out:st={duration-1.0}:d=0.9:alpha=1[l{i}]"
        )
        parts.append(
            f"[{last}][l{i}]overlay=x='{ox}':y='{oy}':eval=frame:shortest=1[m{i}]"
        )
        last = f"m{i}"

    # Text plane (last input)
    text_idx = layer_count + 1
    parts.append(
        f"[{text_idx}:v]format=rgba,"
        f"fade=t=in:st=0.9:d=1.1:alpha=1,"
        f"fade=t=out:st={duration-1.4}:d=1.1:alpha=1[txt]"
    )
    parts.append(f"[{last}][txt]overlay=0:0:shortest=1,format=yuv420p[out]")

    return ";".join(parts)


def render_shot(
    bg_path: Path,
    svg_layers: List[SVGLayer],
    text_img: Image.Image,
    out_clip: Path,
    duration: float,
    camera: Dict,
    motion_profile: str,
    seed: int,
) -> None:
    """Render one 8-second cinematic shot with multi-layer SVG motion."""
    eng = SVGEngine(seed=seed)
    # Rasterize all layers once
    layer_pngs: List[Path] = []
    for i, layer in enumerate(svg_layers):
        raster = eng.rasterize(layer)
        p = OUT / f"_tmp_layer_{seed}_{i}.png"
        raster.save(p)
        layer_pngs.append(p)

    text_path = OUT / f"_tmp_text_{seed}.png"
    text_img.save(text_path)

    filter_complex = build_ffmpeg_filter(
        duration=duration,
        camera=camera,
        layer_count=len(layer_pngs),
        motion_profile=motion_profile,
    )

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(bg_path),
    ]
    for p in layer_pngs:
        cmd += ["-loop", "1", "-framerate", "24", "-i", str(p)]
    cmd += [
        "-loop", "1", "-framerate", "24", "-i", str(text_path),
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", str(duration),
        "-r", "24",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(out_clip),
    ]
    run(cmd)

    # Cleanup temps
    for p in layer_pngs:
        p.unlink(missing_ok=True)
    text_path.unlink(missing_ok=True)

    if not out_clip.exists() or out_clip.stat().st_size < 80_000:
        raise SystemExit(f"Shot render failed or too small: {out_clip}")


def qa_video(path: Path, expected_duration: float = 24.0) -> Dict:
    """Technical QA — necessary but not sufficient for visual approval."""
    streams = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)]
        )
    )["streams"]
    kinds = {s["codec_type"] for s in streams}
    video_ok = any(
        s.get("width") == 1080 and s.get("height") == 1920
        for s in streams if s["codec_type"] == "video"
    )
    duration = float(
        json.loads(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_format", "-of", "json", str(path)]
            )
        )["format"]["duration"]
    )
    size_ok = path.stat().st_size > 150_000
    dur_ok = abs(duration - expected_duration) < 1.2
    passed = size_ok and {"video", "audio"} <= kinds and video_ok and dur_ok
    return {
        "file": path.name,
        "passed": passed,
        "streams": sorted(kinds),
        "bytes": path.stat().st_size,
        "duration_seconds": round(duration, 2),
        "resolution_ok": video_ok,
        "requires_human_visual_approval": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="YUNA Creative Studio V4 Pipeline")
    parser.add_argument(
        "--seed",
        type=int,
        default=int(datetime.now(timezone.utc).strftime("%G%V")),
        help="Deterministic seed",
    )
    parser.add_argument("--skip-music", action="store_true")
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Generate a single 8-second test clip instead of 3 full Shorts",
    )
    parser.add_argument(
        "--style",
        choices=["A", "B", "C"],
        default=None,
        help="Commercial style: A=emotional, B=educational, C=conversion",
    )
    parser.add_argument(
        "--course",
        choices=[c[0] for c in COURSES],
        default=None,
        help="Force a specific course",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    assert_no_png_overlays()

    # Load assets
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    backgrounds = [
        x for x in data["assets"]
        if x["category"] == "background" and (ROOT / x["path"]).exists()
    ]
    if len(backgrounds) < 3:
        raise SystemExit("Need at least three existing photographic backgrounds")

    rng = random.Random(args.seed)
    rng.shuffle(backgrounds)

    # Avoid recent backgrounds
    previous = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {"productions": []}
    used = {
        z["asset"]
        for v in previous.get("productions", [])[-6:]
        for z in v.get("scenes", [])
    }
    backgrounds.sort(key=lambda x: (x["id"] in used, rng.random()))

    # Course selection
    if args.course:
        course = next(c for c in COURSES if c[0] == args.course)
    else:
        course = COURSES[args.seed % len(COURSES)]

    style = args.style or ["A", "B", "C"][args.seed % 3]

    presets_data = load_presets()
    course_map = presets_data.get("course_mapping", {})
    preset_name = course_map.get(course[0], "sakura_fall")

    # Music
    if not args.skip_music:
        env = os.environ.copy()
        env["YUNA_SEED"] = str(args.seed)
        subprocess.run(
            [sys.executable, "automation/yuna-sound/scripts/generate.py"],
            cwd=ROOT, env=env, check=True,
        )
    audio = ROOT / "automation/yuna-sound/input/track.wav"
    if not audio.exists() or audio.stat().st_size < 1000:
        raise SystemExit("No usable audio track found. Refusing to deliver a silent Short. Use music generation or provide track.wav.")

    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not Path(font_bold).exists():
        # Fallback common on some runners
        font_bold = font_regular = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

    eng = SVGEngine(seed=args.seed)
    available_svgs = eng.list_available()
    print(f"SVG engine ready — {len(available_svgs)} overlays available")

    scenes_meta: List[Dict] = []
    crop_audit: List[Dict] = []
    composition_reports: List[Dict] = []

    n_shorts = 1 if args.quick_test else 3
    shots_per_short = 1 if args.quick_test else 3

    for n in range(n_shorts):
        clips: List[Path] = []
        for shot in range(shots_per_short):
            item = backgrounds[(n * 3 + shot) % len(backgrounds)]
            bg_path = OUT / f"background-{n}-{shot}.png"
            _, audit = prepare_background(ROOT / item["path"], bg_path)
            audit["asset"] = item["id"]
            crop_audit.append(audit)

            # Build SVG layers for this shot
            layers = eng.build_layers_from_preset(preset_name)
            # Slight per-shot variation for organic feel
            for i, layer in enumerate(layers):
                layer.seed = args.seed + n * 100 + shot * 10 + i
                layer.offset_x += rng.uniform(-25, 25)
                layer.offset_y += rng.uniform(-20, 20)

            # Text
            msg_variants = [
                course[1],
                "Aprendé a tu ritmo",
                "Explorá YUNA Academy",
            ]
            message = msg_variants[shot % len(msg_variants)]
            text_img = build_text_plane(
                course[0], message, style, shot, font_bold, font_regular
            )

            # Camera from preset
            preset = presets_data.get("presets", {}).get(preset_name, {})
            camera = preset.get("camera", {"zoom_start": 1.0, "zoom_end": 1.05})
            motion_profile = preset.get("motion_profile", "fall")

            clip = OUT / f"clip-{n}-{shot}.mp4"
            render_shot(
                bg_path=bg_path,
                svg_layers=layers,
                text_img=text_img,
                out_clip=clip,
                duration=8.0,
                camera=camera,
                motion_profile=motion_profile,
                seed=args.seed + n * 50 + shot,
            )
            clips.append(clip)

            # Report
            _, report = eng.compose(layers)
            report.scene_id = f"short{n+1}_shot{shot+1}"
            report.backgrounds = [item["id"]]
            composition_reports.append(report.to_dict())

            scenes_meta.append({
                "asset": item["id"],
                "message": message,
                "svg_preset": preset_name,
                "style": style,
                "layers": [l.name for l in layers],
            })

        if args.quick_test:
            # Single 8 s clip is the deliverable
            final = OUT / "yuna-quick-test.mp4"
            run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(clips[0]), "-i", str(audio),
                "-map", "0:v", "-map", "1:a", "-t", "8",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                "-movflags", "+faststart", str(final),
            ])
            print(f"Quick test written: {final}")
        else:
            # Concatenate 3 × 8 s → 24 s Short
            playlist = OUT / f"concat-{n}.txt"
            playlist.write_text("".join(f"file '{c.name}'\n" for c in clips))
            video = OUT / f"yuna-short-{n+1}.mp4"
            run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(playlist),
                "-i", str(audio), "-map", "0:v", "-map", "1:a",
                "-t", "24", "-c:v", "copy", "-c:a", "aac",
                "-b:a", "160k", "-movflags", "+faststart", str(video),
            ])

    # QA
    qa_results = []
    if args.quick_test:
        qa_results.append(qa_video(OUT / "yuna-quick-test.mp4", expected_duration=8.0))
    else:
        for n in range(3):
            qa_results.append(qa_video(OUT / f"yuna-short-{n+1}.mp4", 24.0))

    # Visual QA report (technical + resource audit)
    visual_qa = {
        "version": "4.0",
        "svg_overlays_available": len(available_svgs),
        "svg_renderer": "cairosvg",
        "png_decorative_layers_disabled": True,
        "forbidden_png_path_referenced": False,
        "crop_audit": crop_audit,
        "composition_reports": composition_reports,
        "shots_per_short": shots_per_short,
        "requires_human_visual_approval": True,
        "qa": qa_results,
        "style": style,
        "preset": preset_name,
        "course": course[0],
    }
    (OUT / "visual-qa.json").write_text(
        json.dumps(visual_qa, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Production record
    record = {
        "seed": args.seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": "4.0",
        "course": course[0],
        "style": style,
        "preset": preset_name,
        "scenes": scenes_meta,
        "qa": qa_results,
        "publication_status": "draft_requires_approval",
        "official_url": OFFICIAL_URL,
        "brand": BRAND,
        "music_brand": MUSIC_BRAND,
    }
    (OUT / "production.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Publishing draft (never auto-publish)
    draft = (
        f"{BRAND} | {course[0]}\n"
        f"{course[1]}\n"
        f"Conocé nuestros cursos: {OFFICIAL_URL}\n"
        f"Canal: https://www.youtube.com/@YunaSoundHolistic\n"
        f"ESTADO: BORRADOR — REQUIERE REVISIÓN HUMANA — NO PUBLICADO\n"
        f"Estilo: {style} | Preset: {preset_name} | Seed: {args.seed}\n"
    )
    (OUT / "publishing-draft.txt").write_text(draft, encoding="utf-8")

    # History
    previous.setdefault("productions", [])
    previous["productions"] = (previous["productions"] + [record])[-52:]
    HISTORY.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not all(x["passed"] for x in qa_results):
        print("WARNING: Technical QA did not fully pass. Human review mandatory.")
    else:
        print("Technical QA passed. Human visual approval still required.")

    print(
        f"YUNA Creative Studio V4 complete — "
        f"{'quick-test' if args.quick_test else '3 Shorts'} | "
        f"style={style} | course={course[0]} | seed={args.seed}"
    )


if __name__ == "__main__":
    main()