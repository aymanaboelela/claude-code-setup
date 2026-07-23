#!/usr/bin/env python3
"""Shared path-sampling for candidate stroke definitions.

A candidate is JSON: either a list of strokes, or {"strokes": [...],
"stroke_width": N, "design_width": W, "design_height": H}. Each stroke is a
list of segments in one of these forms:
    ["M", x, y]                       moveTo
    ["L", x, y]                       lineTo
    ["Q", cx, cy, x, y]               quadratic bezier
    ["C", c1x, c1y, c2x, c2y, x, y]   cubic bezier
"""
import json
import math


def load_candidate(path):
    obj = json.load(open(path))
    if isinstance(obj, list):
        return {"strokes": obj}
    return obj


def sample_stroke(segs, step=1.5):
    """Return a list of (x, y) points densely sampled along the stroke."""
    pts = []
    cur = None
    for s in segs:
        kind = s[0]
        if kind == "M":
            cur = (s[1], s[2])
            pts.append(cur)
        elif kind == "L":
            x0, y0 = cur
            x2, y2 = s[1], s[2]
            n = max(1, int(math.hypot(x2 - x0, y2 - y0) / step))
            for i in range(1, n + 1):
                t = i / n
                pts.append((x0 + (x2 - x0) * t, y0 + (y2 - y0) * t))
            cur = (x2, y2)
        elif kind == "Q":
            x0, y0 = cur
            cx, cy, x2, y2 = s[1], s[2], s[3], s[4]
            d = math.hypot(cx - x0, cy - y0) + math.hypot(x2 - cx, y2 - cy)
            n = max(2, int(d / step))
            for i in range(1, n + 1):
                t = i / n
                mt = 1 - t
                pts.append((mt * mt * x0 + 2 * mt * t * cx + t * t * x2,
                            mt * mt * y0 + 2 * mt * t * cy + t * t * y2))
            cur = (x2, y2)
        elif kind == "C":
            x0, y0 = cur
            c1x, c1y, c2x, c2y, x2, y2 = s[1:7]
            d = (math.hypot(c1x - x0, c1y - y0) + math.hypot(c2x - c1x, c2y - c1y)
                 + math.hypot(x2 - c2x, y2 - c2y))
            n = max(2, int(d / step))
            for i in range(1, n + 1):
                t = i / n
                mt = 1 - t
                pts.append((mt**3 * x0 + 3 * mt * mt * t * c1x + 3 * mt * t * t * c2x + t**3 * x2,
                            mt**3 * y0 + 3 * mt * mt * t * c1y + 3 * mt * t * t * c2y + t**3 * y2))
            cur = (x2, y2)
        else:
            raise ValueError(f"unknown segment {kind!r}")
    return pts
