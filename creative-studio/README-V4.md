# YUNA Creative Studio V4 — Drop-in Upgrade Package

This package upgrades the existing **Creative Studio** module of the [YUNA Academy](https://github.com/InstructorMap/yuna-academy) repository from V3.2 to V4.

## Scope (strict)

- **Only** `creative-studio/` and its GitHub Actions workflow.
- **Does not** modify campus, courses, authentication, database or the public website.
- **Does not** publish anything automatically.

## Contents

```
yuna-creative-studio-v4/
├── README.md
├── INTEGRATION.md              ← start here
├── CHANGELOG_AND_RISKS.md
├── requirements-v4.txt
├── creative-studio/
│   ├── config/
│   │   └── svg_presets.json
│   └── scripts/
│       ├── svg_engine.py
│       └── production_pipeline.py   (replaces the V3.2 version)
└── .github/workflows/
    └── yuna-creative-v4.yml
```

## Quick start

1. Read `INTEGRATION.md`.
2. Copy the files into a feature branch of the official repository.
3. Run the local smoke test.
4. Trigger the new GitHub Action with `quick_test=true`.
5. Review the generated 8-second clip visually.
6. Only after visual approval, produce full 24-second Shorts.

## Design pillars

- Realistic photographic backgrounds (kept).
- Official SVG overlays only (no decorative PNGs).
- Cinematic multi-layer motion.
- Deterministic, zero-cost, GitHub Actions compatible.
- Clear brand identity: **YUNA Academy** + **Yuna Sound Holistic**.
- Every artifact is a **draft** that requires human visual approval.

Official site: https://yuna-academy.vercel.app/


## Ajustes de integración
- Se incluye `creative-studio/resources/branding/yuna-academy-lockup.svg` como **identificador tipográfico SVG provisional**, NO como logo oficial validado. Sustituir únicamente tras confirmar el SVG de marca oficial.
- Las pruebas rápidas y las producciones completas requieren audio; si falta o falla su generación, el pipeline detiene la entrega.
- Se eliminó `cache: pip` del workflow para evitar el fallo de setup-python cuando no existe un manifiesto de dependencias en la raíz.
- No se han realizado pruebas de renderizado en GitHub Actions todavía.