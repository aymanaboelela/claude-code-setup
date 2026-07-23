---
name: svg-draw-animation
description: Turn an SVG or logo image into a Flutter "self-drawing" animation (the mark strokes itself on, like being sketched by a pen) for splash screens and loading indicators. Use when the user sends an SVG/logo/PNG and wants it to draw/animate itself, mentions a splash-screen draw-on animation, a branded/custom loading spinner from their logo, "بتترسم"/"كأنها بترسم"/self-drawing/stroke-on/animated logo, or asks to replace a Lottie/CircularProgressIndicator with their own logo.
---

# SVG / Logo Draw-On Animation (Flutter)

Produce a logo that **draws itself stroke-by-stroke** using a `CustomPainter` +
`PathMetric.extractPath`. Works for a splash hero (draw once, optionally fade in
the real asset on top) and for a looping loading indicator (draw → hold → fade →
repeat). This is resolution-independent, tiny, and on-brand — no Lottie/GIF.

## First decision: is the SVG real vectors, or a raster in an SVG wrapper?

Run this before anything else — it decides the whole approach:

```bash
python3 scripts/inspect_svg.py <file.svg>
```

- **Real vector paths** (`<path d="…">`, polygons, etc.) → the easy path.
  Pull the `d=""` strings straight out and hand them to the Flutter template as
  `parseSvgPathData(...)` (package `path_drawing`) or convert to `Path` calls.
  Skip tracing entirely. See [REFERENCE.md](REFERENCE.md) §A.
- **A `<image … base64>` raster wrapped in SVG** (very common from Figma/Canva
  exports) → there are **no paths to animate**. The script extracts the PNG next
  to the file. You must **trace the centerline** yourself (§ below).

## Workflow for a raster logo (trace the centerline)

The mark is almost always a few **thick constant-width strokes**. You recover the
*centerline* of those strokes and redraw them with a round-cap stroke.

1. **Probe the pixels** to see the geometry as text (no image libs needed):
   ```bash
   python3 scripts/logo_probe.py <extracted.png>
   ```
   Prints an ASCII rendering + horizontal/vertical run-length tables and the
   estimated stroke width. Use these to read off coordinates.
2. **Trace** the mark as the fewest continuous pen strokes possible (often 1–2).
   Write candidate paths to a JSON file — segment forms: `["M",x,y]`,
   `["L",x,y]`, `["Q",cx,cy,x,y]`, `["C",c1x,c1y,c2x,c2y,x,y]`. See
   [REFERENCE.md](REFERENCE.md) §B for the format and tracing tips.
3. **Verify against the original, don't eyeball it:**
   ```bash
   python3 scripts/trace_check.py <extracted.png> paths.json --stroke 88
   ```
   Prints **IoU** vs the real logo and writes `overlay.png` (grey=match,
   orange=missed, green=excess). Adjust coordinates and re-run until **IoU ≥ 0.93**.
4. **Generate the Flutter code:** copy `assets/logo_draw_animation.dart` into the
   project (e.g. `lib/core/widgets/`), then paste your verified paths into
   `LogoPaths` and set `designWidth/Height` + `strokeWidth`. The file already
   contains the painter, the splash widget, and the loading widget.

## Wiring into the app

- **Splash:** replace the static/opacity logo with `AnimatedDrawLogo(size: …)`.
  Its first frame is the solid logo, then it "comes to life" (dims to a guide
  while the pen inks over it) — so it hands off **seamlessly from the native
  splash**. Render at the native logo's fixed point size, centered in the whole
  screen. Keep any existing navigation timer. See [REFERENCE.md](REFERENCE.md) §E
  for matching the native splash frame (you cannot animate the native splash
  itself — iOS forbids it; the seamless handoff is the professional answer).
- **Loading:** point the app's existing loader widget(s) at
  `DrawingLoadingIndicator(size: …)`. Keep the old widget's class name and
  constructor params so the ~N call sites don't change.
- Match the repo: reuse its color constants, `flutter_screenutil` sizing, and
  `withValues(alpha:)` (not deprecated `withOpacity`) on modern Flutter.

## Verify it actually runs

`flutter analyze` the changed files, then drive the app (`flutter run`, or the
Dart MCP `launch_app`) and watch the splash/loader. If the device build is
blocked by unrelated native issues, render the draw frames with
`scripts/logo_probe.py --frames paths.json` to confirm the stroke order reads well.

Full details, the vector-path shortcut, tracing methodology, and tuning knobs:
[REFERENCE.md](REFERENCE.md).
