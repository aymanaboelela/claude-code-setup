#!/usr/bin/env python3
"""Score a candidate centerline trace against the real logo (IoU) and write a
diagnostic overlay. Iterate on paths.json until IoU >= 0.93.

Usage:
    python3 trace_check.py <original.png> <paths.json> [--stroke N] [--out overlay.png]

paths.json: see pathlib_seg.py for the segment format. If it carries
"design_width"/"design_height" the coords are in that space; otherwise coords
are assumed to be in the original image's pixel space.

overlay.png: grey = correct, orange = logo pixels you MISSED,
green = pixels your stroke added that AREN'T in the logo.
No third-party dependencies.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import decode_png, encode_png_rgb, foreground_mask  # noqa: E402
from pathlib_seg import load_candidate, sample_stroke  # noqa: E402


def main():
    if len(sys.argv) < 3:
        print("usage: trace_check.py <original.png> <paths.json> [--stroke N] [--out overlay.png]",
              file=sys.stderr)
        return 1
    orig_path, cand_path = sys.argv[1], sys.argv[2]
    cand = load_candidate(cand_path)
    w0, h0, nch, px = decode_png(orig_path)
    orig = foreground_mask(w0, h0, nch, px)

    dw = cand.get("design_width", w0)
    dh = cand.get("design_height", h0)
    stroke_w = cand.get("stroke_width", 88)
    if "--stroke" in sys.argv:
        stroke_w = float(sys.argv[sys.argv.index("--stroke") + 1])
    out = "overlay.png"
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]

    # Render candidate at half the ORIGINAL resolution for speed, mapping design
    # coords -> original pixels -> half-res canvas.
    W, H = (w0 + 1) // 2, (h0 + 1) // 2
    sx, sy = W / dw, H / dh
    r = stroke_w / 2 * min(sx, sy)
    ri = int(math.ceil(r))
    disk = [(dx, dy) for dy in range(-ri, ri + 1) for dx in range(-ri, ri + 1)
            if dx * dx + dy * dy <= r * r]

    canvas = bytearray(W * H)
    for stroke in cand["strokes"]:
        for (x, y) in sample_stroke(stroke, step=1.2 / min(sx, sy)):
            icx, icy = int(round(x * sx)), int(round(y * sy))
            for dx, dy in disk:
                px2, py2 = icx + dx, icy + dy
                if 0 <= px2 < W and 0 <= py2 < H:
                    canvas[py2 * W + px2] = 1

    # Downsample original mask to the same half-res grid.
    om = bytearray(W * H)
    for y in range(H):
        for x in range(W):
            om[y * W + x] = orig[min(h0 - 1, y * 2) * w0 + min(w0 - 1, x * 2)]

    inter = union = missed = excess = 0
    rgb = bytearray(W * H * 3)
    for i in range(W * H):
        o, c = om[i], canvas[i]
        if o or c:
            union += 1
        if o and c:
            inter += 1
            col = (70, 70, 70)
        elif o:
            missed += 1
            col = (230, 90, 40)
        elif c:
            excess += 1
            col = (0, 180, 90)
        else:
            col = (255, 255, 255)
        rgb[i * 3:i * 3 + 3] = bytes(col)
    encode_png_rgb(out, W, H, rgb)

    iou = inter / union if union else 0.0
    print(f"IoU = {iou:.4f}   missed(orange)={missed}  excess(green)={excess}")
    print(f"design={dw}x{dh}  stroke={stroke_w}  -> wrote {out}")
    if iou >= 0.93:
        print("GOOD: trace matches the logo. Paste these paths into the Flutter template.")
    else:
        print("Adjust coordinates where you see orange/green in the overlay, then re-run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
