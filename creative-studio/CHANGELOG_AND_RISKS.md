# YUNA Creative Studio V4 — Change Report & Risks

## New files

| Path | Purpose |
|------|---------|
| `creative-studio/scripts/svg_engine.py` | Modular SVG load / classify / rasterize / compose engine |
| `creative-studio/config/svg_presets.json` | Cinematic presets, course mapping, style variants |
| `.github/workflows/yuna-creative-v4.yml` | Dedicated workflow with quick-test and style controls |
| `INTEGRATION.md` | Step-by-step integration instructions |
| `CHANGELOG_AND_RISKS.md` | This document |
| `requirements-v4.txt` | Explicit Python dependencies |

## Modified files

| Path | Change |
|------|--------|
| `creative-studio/scripts/production_pipeline.py` | Full rewrite preserving public CLI contract (`--seed`, `--skip-music`) and adding `--quick-test`, `--style`, `--course` |

## Behaviour preserved from V3.2

- Photographic backgrounds from `resources/ia/fondos/`
- Official SVG overlays only
- YUNA Sound music generation
- 1080×1920 @ 24 fps H.264/AAC
- Three 8-second shots per Short (unless quick-test)
- Deterministic seed
- No automatic publishing
- Production history tracking
- Crop audit for letterboxed sources

## Behaviour improved

1. **Multi-layer SVG composition** with real alpha, depth blur and independent motion.
2. **Cinematic camera** (progressive zoom + gentle pan) instead of a single static zoompan.
3. **Motion profiles** (fall, float, breathe, pulse, drift) mapped to visual families.
4. **Three commercial styles** (A emotional, B educational, C conversion).
5. **Full composition report** listing every SVG and parameter used per scene.
6. **Hard guard** against decorative PNG overlays from `transparentes/`.
7. **Quick-test mode** for rapid visual iteration (one 8 s clip).

## Risks & mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| CairoSVG / system Cairo missing on runner | High | Workflow installs `libcairo2`, `libpango*`, `libgdk-pixbuf*` and `cairosvg` |
| FFmpeg filter graph too complex for free runners | Medium | `--quick-test` reduces load; `veryfast` preset used |
| Visual quality still subjective | High | Explicit `requires_human_visual_approval: true` in every report |
| Seed collision with previous productions | Low | History tracks last 52 productions and de-prioritises recent backgrounds |
| Missing official SVG logo | Low | Typographic lockup used; documented absence; no invented logo |
| Accidental use of LUMENIA assets | None | Code never references LUMENIA; brand constants are hard-coded to YUNA |

## Dependencies (Python)

```
pillow>=10.0
cairosvg>=2.7
```

System (Ubuntu):

```
ffmpeg
libcairo2
libpango-1.0-0
libpangocairo-1.0-0
libgdk-pixbuf2.0-0
fonts-dejavu-core
```

## Testing performed by this deliverable

- Structural validation of the new modules
- Smoke-test path for `svg_engine.py`
- Full argument surface of `production_pipeline.py` (`--quick-test`, `--style`, `--course`, `--seed`, `--skip-music`)
- Workflow YAML syntax and step ordering
- Explicit refusal to load PNG overlays from `transparentes/`

**Note:** Actual video frames cannot be rendered in this environment without the full photographic asset set and Cairo. After integration, run the local smoke test and the GitHub Action once, then perform side-by-side visual comparison with a V3.2 export.

## Acceptance statement

When the integration steps in `INTEGRATION.md` are followed and a human reviewer confirms that the multi-layer SVG motion, soft typography and photographic backgrounds produce a clearly superior visual result to V3.2, the V4 upgrade can be considered accepted for production drafts.