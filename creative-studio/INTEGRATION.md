# YUNA Creative Studio V4 — Integration Guide

## What changed (summary)

V4 elevates the existing V3.2 pipeline without touching campus, courses, authentication, database or the main website.

| Area | V3.2 | V4 |
|------|------|----|
| Overlays | Single SVG, basic alpha | Multi-layer SVG engine with depth, blur, independent motion |
| Animation | Simple zoompan + one overlay | Cinematic camera (zoom + pan), parallax by depth, fade curves |
| Identity | Basic “YUNA” text | Soft gradient, brand lockup, three commercial styles (A/B/C) |
| Config | Hard-coded | `config/svg_presets.json` + course → preset mapping |
| QA | Technical only | Technical + full composition report (resources used per scene) |
| Modes | Always 3 Shorts | Full production **or** `--quick-test` (single 8 s clip) |

## Files to add / replace

```
creative-studio/
├── config/
│   └── svg_presets.json          ← NEW
├── scripts/
│   ├── svg_engine.py             ← NEW
│   └── production_pipeline.py    ← REPLACE (backward-compatible flags)
└── generated/                    ← created at runtime (gitignored)

.github/workflows/
└── yuna-creative-v4.yml          ← NEW (does not remove old workflows)
```

**Do not delete** the existing workflows (`yuna-integrated-production.yml`, `yuna-creative-short-pilot.yml`, etc.). The new workflow is additive and can be run independently.

## Prerequisites (already present in the repo)

- Photographic backgrounds: `creative-studio/resources/ia/fondos/*.png`
- Official SVG overlays: `creative-studio/resources/overlays/*.svg`
- YUNA Sound engine: `automation/yuna-sound/`
- CairoSVG + Pillow + FFmpeg (installed by the workflow)

## Local smoke test

```bash
# From repository root
python -m pip install pillow cairosvg
python creative-studio/scripts/svg_engine.py
python creative-studio/scripts/production_pipeline.py --quick-test --skip-music --seed 2026
```

Expected output:

- `creative-studio/generated/svg_engine_smoke.png`
- `creative-studio/generated/production/yuna-quick-test.mp4`
- `creative-studio/generated/production/visual-qa.json`
- `creative-studio/generated/production/production.json`

## Full production (3 Shorts × 24 s)

```bash
python creative-studio/scripts/production_pipeline.py --seed 202611 --style A
```

## GitHub Actions

1. Go to **Actions → YUNA Creative Studio V4 → Run workflow**
2. Optional inputs: seed, style (A/B/C), course, quick_test, skip_music
3. Download the artifact `yuna-creative-v4-drafts`
4. Perform **human visual review** before any publication

## Design decisions enforced

1. **Photographic backgrounds** from `resources/ia/fondos/` are kept.
2. **PNG candidates** in `resources/ia/transparentes/` are **never** used as decorative layers.
3. Only SVGs from `resources/overlays/` are used for effects.
4. Original YUNA Sound music is preserved.
5. Format: 1080×1920, 24 fps, H.264 + AAC.
6. Zero external paid services.
7. **No automatic publishing** — every artifact is marked `draft_requires_approval`.

## Brand identity

- Brand: **YUNA Academy**
- Music brand: **Yuna Sound Holistic**
- Official URL: https://yuna-academy.vercel.app/
- No LUMENIA assets or naming are used.
- Logo: the pipeline uses a clean typographic lockup. If an official SVG logo is later added under `resources/`, the engine can incorporate it; none was found as a definitive official SVG at integration time.

## Acceptance criteria checklist

- [ ] SVG engine loads and classifies all overlays
- [ ] Layers keep real RGBA transparency
- [ ] Multiple simultaneous SVG layers with independent motion
- [ ] No PNG decorative overlays appear in composition reports
- [ ] Videos contain both video and audio streams (when music is enabled)
- [ ] Resolution 1080×1920, duration correct
- [ ] `visual-qa.json` and `production.json` generated
- [ ] `--quick-test` produces a single 8-second clip
- [ ] Human visual review still required (technical QA is not sufficient)

## Risk notes

- **CairoSVG** must be available; the workflow installs system Cairo libraries.
- Long-running GitHub Actions free-tier jobs may hit the 6-hour limit if many variants are requested; use `--quick-test` for iteration.
- Determinism is seed-based; the same seed + same assets produce the same composition.
- Visual quality is subjective; always perform a side-by-side review against V3.2 before considering V4 production-ready.

## Rollback

Keep the previous `production_pipeline.py` under version control. To revert:

```bash
git checkout HEAD~1 -- creative-studio/scripts/production_pipeline.py
# or restore from your branch history
```

The new files (`svg_engine.py`, `svg_presets.json`, the V4 workflow) can simply be left unused.