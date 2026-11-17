#!/usr/bin/env python3
"""Zero-dependency asset inventory validator; run from repository root."""
import json
import pathlib
import struct
import sys

root = pathlib.Path(__file__).resolve().parents[2]
catalog = json.loads((root / "creative-studio/asset-catalog.json").read_text())
missing, invalid = [], []
print("YUNA Creative Studio — asset audit")
for asset in catalog["assets"]:
    p = root / asset["path"]
    if not p.is_file():
        missing.append(asset["path"])
        continue
    raw = p.read_bytes()[:24]
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        invalid.append(asset["path"])
        continue
    width, height = struct.unpack(">II", raw[16:24])
    print(f"{asset['role']:18} {width:5}x{height:<5} {asset['path']}")
print(f"Inventariados: {len(catalog['assets'])}; ausentes: {len(missing)}; PNG invalidos: {len(invalid)}")
for item in missing:
    print("MISSING:", item)
for item in invalid:
    print("INVALID:", item)
sys.exit(1 if missing or invalid else 0)
