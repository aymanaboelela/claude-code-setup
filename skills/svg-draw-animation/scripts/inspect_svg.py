#!/usr/bin/env python3
"""Classify an SVG: does it contain real vector paths, or is it a raster
(base64 <image>) wrapped in an SVG shell? Extract any embedded rasters.

Usage:
    python3 inspect_svg.py <file.svg>

Exit codes: 0 real vectors present, 2 raster-wrapped only, 1 error.
No third-party dependencies.
"""
import base64
import os
import re
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: inspect_svg.py <file.svg>", file=sys.stderr)
        return 1
    path = sys.argv[1]
    try:
        data = open(path, "r", encoding="utf-8", errors="replace").read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Count drawable vector elements. A single full-canvas <rect> that only
    # carries a pattern/image fill is NOT real vector art, so ignore rects
    # whose fill points at a url(#...) pattern.
    paths = re.findall(r"<path\b[^>]*\bd\s*=", data)
    polys = re.findall(r"<(?:polygon|polyline)\b", data)
    circles = re.findall(r"<(?:circle|ellipse)\b", data)
    lines = re.findall(r"<line\b", data)
    # rects that are real shapes (fill is a color, not a pattern/image)
    real_rects = []
    for rect in re.findall(r"<rect\b[^>]*>", data):
        fill = re.search(r'fill\s*=\s*"([^"]*)"', rect)
        if not fill or not fill.group(1).lower().startswith("url("):
            real_rects.append(rect)

    vector_count = len(paths) + len(polys) + len(circles) + len(lines) + len(real_rects)

    # Embedded rasters
    images = re.findall(
        r'xlink:href\s*=\s*"data:image/(png|jpe?g);base64,([A-Za-z0-9+/=\s]+)"'
        r'|href\s*=\s*"data:image/(png|jpe?g);base64,([A-Za-z0-9+/=\s]+)"',
        data,
    )
    extracted = []
    base, _ = os.path.splitext(path)
    for i, m in enumerate(images):
        ext = m[0] or m[2]
        b64 = (m[1] or m[3]).strip().replace("\n", "").replace(" ", "")
        try:
            raw = base64.b64decode(b64)
        except Exception:  # noqa: BLE001
            continue
        suffix = ".extracted.png" if ext.startswith("png") else ".extracted.jpg"
        out = f"{base}{'' if i == 0 else '.' + str(i)}{suffix}"
        with open(out, "wb") as fh:
            fh.write(raw)
        extracted.append((out, len(raw)))

    print(f"file: {path}")
    print(f"vector elements: {len(paths)} <path>, {len(polys)} poly, "
          f"{len(circles)} circle/ellipse, {len(lines)} line, "
          f"{len(real_rects)} real <rect>")
    print(f"embedded rasters: {len(images)}")
    for out, n in extracted:
        print(f"  extracted -> {out} ({n} bytes)")

    if len(paths) + len(polys) >= 1 and not extracted:
        print("\nVERDICT: REAL VECTOR PATHS.")
        print("Use the d=\"\" strings directly (path_drawing.parseSvgPathData) —")
        print("no tracing needed. See REFERENCE.md section A.")
        return 0
    if extracted:
        print("\nVERDICT: RASTER WRAPPED IN SVG — there are no paths to animate.")
        print("Trace the centerline from the extracted image:")
        print(f"  python3 logo_probe.py {extracted[0][0]}")
        print("Then verify with trace_check.py. See REFERENCE.md section B.")
        return 2
    print("\nVERDICT: no drawable vectors and no rasters found — inspect by hand.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
