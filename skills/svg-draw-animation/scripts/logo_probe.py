#!/usr/bin/env python3
"""Read a raster logo as TEXT so you can trace its centerline by hand.

Usage:
    python3 logo_probe.py <image.png>              # ASCII + run tables + stroke width
    python3 logo_probe.py <image.png> --frames paths.json [--stroke N]
                                                   # render draw-on frames as a PNG strip

Outputs (next to the image):
    <name>.ascii.txt   ~100-col ASCII rendering of the mask
    <name>.runs.txt    horizontal + vertical run-length tables (for reading coords)
    <name>.frames.png  (only with --frames) progressive drawing preview strip
No third-party dependencies.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import decode_png, encode_png_rgb, foreground_mask  # noqa: E402
from pathlib_seg import load_candidate, sample_stroke  # noqa: E402


def estimate_stroke_width(mask, w, h):
    """Median width of horizontal ink runs — a good proxy for stroke width."""
    widths = []
    for y in range(0, h, max(1, h // 200)):
        x = 0
        while x < w:
            if mask[y * w + x]:
                x0 = x
                while x < w and mask[y * w + x]:
                    x += 1
                widths.append(x - x0)
            else:
                x += 1
    widths.sort()
    return widths[len(widths) // 4] if widths else 0  # lower quartile ~ single stroke


def write_ascii(mask, w, h, out):
    cell = max(1, w // 100)
    lines = []
    for cy in range(0, h - cell + 1, cell * 2):
        row = []
        for cx in range(0, w - cell + 1, cell):
            s = 0
            for yy in range(cy, min(cy + cell * 2, h)):
                for xx in range(cx, min(cx + cell, w)):
                    s += mask[yy * w + xx]
            frac = s / (cell * cell * 2)
            row.append("#" if frac > 0.6 else ("+" if frac > 0.25 else ("." if frac > 0.05 else " ")))
        lines.append("".join(row))
    open(out, "w").write("\n".join(lines))


def write_runs(mask, w, h, out):
    with open(out, "w") as f:
        f.write("== HORIZONTAL RUNS  y=row: [xstart-xend](width) ... ==\n")
        for y in range(10, h, 20):
            runs = []
            x = 0
            while x < w:
                if mask[y * w + x]:
                    x0 = x
                    while x < w and mask[y * w + x]:
                        x += 1
                    runs.append((x0, x - 1))
                else:
                    x += 1
            f.write(f"y={y:4d}: " + "  ".join(f"[{a}-{b}]({b - a + 1})" for a, b in runs) + "\n")
        f.write("\n== VERTICAL RUNS  x=col: [ystart-yend](height) ... ==\n")
        for x in range(10, w, 20):
            runs = []
            y = 0
            while y < h:
                if mask[y * w + x]:
                    y0 = y
                    while y < h and mask[y * w + x]:
                        y += 1
                    runs.append((y0, y - 1))
                else:
                    y += 1
            f.write(f"x={x:4d}: " + "  ".join(f"[{a}-{b}]({b - a + 1})" for a, b in runs) + "\n")


def render_frames(cand, img_w, img_h, stroke_w, out):
    dw = cand.get("design_width", img_w)
    dh = cand.get("design_height", img_h)
    S = 0.28
    fw, fh = int(dw * S) + 8, int(dh * S) + 8
    r = stroke_w / 2 * S
    ri = int(math.ceil(r))
    disk = [(dx, dy) for dy in range(-ri, ri + 1) for dx in range(-ri, ri + 1)
            if dx * dx + dy * dy <= r * r]
    strokes = [sample_stroke(s, step=1.0 / S) for s in cand["strokes"]]

    def cum(pts):
        acc = [0.0]
        for i in range(1, len(pts)):
            acc.append(acc[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
        return acc

    accs = [cum(p) for p in strokes]
    offsets, running = [], 0.0
    for a in accs:
        offsets.append(running)
        running += a[-1]
    total = running or 1.0

    fracs = [0.12, 0.28, 0.45, 0.62, 0.80, 1.0]
    n = len(fracs)
    W, H = fw * n, fh
    rgb = bytearray([255]) * (W * H * 3)
    for fi, fr in enumerate(fracs):
        target = fr * total
        canvas = bytearray(fw * fh)
        for pts, acc, off in zip(strokes, accs, offsets):
            for i, (x, y) in enumerate(pts):
                if off + acc[i] > target:
                    break
                icx, icy = int(round(x * S)) + 4, int(round(y * S)) + 4
                for dx, dy in disk:
                    px, py = icx + dx, icy + dy
                    if 0 <= px < fw and 0 <= py < fh:
                        canvas[py * fw + px] = 1
        for y in range(fh):
            for x in range(fw):
                if canvas[y * fw + x]:
                    idx = (y * W + fi * fw + x) * 3
                    rgb[idx:idx + 3] = bytes((220, 86, 43))
    encode_png_rgb(out, W, H, rgb)


def main():
    if len(sys.argv) < 2:
        print("usage: logo_probe.py <image.png> [--frames paths.json] [--stroke N]", file=sys.stderr)
        return 1
    img = sys.argv[1]
    base, _ = os.path.splitext(img)
    w, h, nch, px = decode_png(img)
    mask = foreground_mask(w, h, nch, px)
    sw = estimate_stroke_width(mask, w, h)

    if "--frames" in sys.argv:
        cand = load_candidate(sys.argv[sys.argv.index("--frames") + 1])
        stroke_w = cand.get("stroke_width", sw)
        if "--stroke" in sys.argv:
            stroke_w = float(sys.argv[sys.argv.index("--stroke") + 1])
        out = f"{base}.frames.png"
        render_frames(cand, w, h, stroke_w, out)
        print(f"wrote {out}  (6-frame draw-on preview, stroke={stroke_w})")
        return 0

    write_ascii(mask, w, h, f"{base}.ascii.txt")
    write_runs(mask, w, h, f"{base}.runs.txt")
    print(f"image: {w}x{h}  channels: {nch}")
    print(f"estimated stroke width: ~{sw}px")
    print(f"wrote {base}.ascii.txt  and  {base}.runs.txt")
    print("Read the ASCII + run tables, trace the centerline as 1-2 pen strokes,")
    print("write paths.json, then run trace_check.py to score it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
