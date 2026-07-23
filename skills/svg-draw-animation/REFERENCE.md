# SVG Draw-On Animation — Reference

The technique: draw a logo's outline **progressively** with a `CustomPainter`
that strokes an increasing fraction of the path using `PathMetric.extractPath`.
The animation's "pen" is a round-cap `Paint`, so any logo built from
constant-width strokes reads as if hand-sketched.

There are two starting points depending on what the SVG actually contains — the
`inspect_svg.py` script tells you which.

---

## A. Real vector SVG (the easy case)

If `inspect_svg.py` reports real `<path>` elements, you already have the
geometry. Two ways to get it into Flutter:

1. **`path_drawing` package** (least work). Add `path_drawing` to pubspec, then
   in `LogoPaths.strokes()`:
   ```dart
   import 'package:path_drawing/path_drawing.dart';
   static List<Path> strokes() => [
     parseSvgPathData('M171 618 L171 462 Q171 403 230 403 ...'),
     parseSvgPathData('M399 561 L528 421 ...'),
   ];
   ```
   Copy each `d="..."` string from the SVG. Set `designWidth/Height` to the
   SVG `viewBox` dimensions.
2. **Hand-convert** `d` commands to `Path` calls (`moveTo/lineTo/quadraticBezierTo
   /cubicTo`) if you don't want the dependency.

Notes for the vector case:
- **Filled logos vs. stroked logos.** The painter strokes the path centerline.
  If the SVG art is a *filled* shape (most icon logos), stroking its outline
  animates the *outline being drawn*, then you cross-fade to the filled asset
  (`finalAsset`) — usually the look you want. If the SVG is already a *stroke*
  (constant width), set `strokeWidth` to match and you get a clean pen-draw with
  no fill needed.
- **Draw order = stroke order in the list.** Put the path you want drawn first
  first. Multiple sub-paths inside one `d` are handled (each becomes its own
  PathMetric and they draw in order).

---

## B. Raster wrapped in SVG (trace the centerline)

Figma/Canva often export a PNG base64-embedded in an `<svg><image></svg>` shell.
There are **no paths** — you reconstruct them. The mark is nearly always a few
**thick constant-width strokes**, so you trace the *centerline* of each stroke
and redraw it with `strokeWidth` ≈ the measured thickness.

### 1. Probe
```bash
python3 scripts/logo_probe.py extracted.png
```
Reads `.ascii.txt` (shape overview) and `.runs.txt` (exact pixel coordinates of
ink at each scan row/column) and prints the estimated stroke width. The run
tables are how you read off real coordinates: e.g. a horizontal run
`y=462: [128-215](88) [585-671](88)` tells you two vertical strokes ~88px wide
whose centers are at x≈171 and x≈628 at that row.

### 2. Trace into `paths.json`
```json
{
  "design_width": 800,
  "design_height": 820,
  "stroke_width": 88,
  "strokes": [
    [ ["M",171,618], ["L",171,462], ["Q",171,403,230,403],
      ["Q",252,403,273,425], ["L",540,722] ],
    [ ["M",399,561], ["L",528,421], ["Q",545,403,570,403] ]
  ]
}
```
Segment forms: `["M",x,y]`, `["L",x,y]`, `["Q",cx,cy,x,y]`,
`["C",c1x,c1y,c2x,c2y,x,y]`.

Tracing tips:
- **Fewest strokes possible.** Most logos are 1–3 continuous pen strokes. A
  single stroke that self-crosses (like an M inside a house) is fine and looks
  best — it reads as one confident gesture.
- **Follow the centerline**, not the edges. At a corner where two straight runs
  meet, the centerline turns with a small `Q` whose control point sits at the
  geometric corner.
- **Rounded corners** in the art → a `C`/`Q` in the trace. Sharp exterior
  corners of a rounded-rect → a quarter-circle cubic
  (`["C", x0, y0+k, x0+k, y1, x1, y1]` with k≈0.55·radius).
- **Caps.** Start/end each open stroke at the visual tip of the stroke; the
  round `StrokeCap` fills the rounded end automatically.

### 3. Verify (don't eyeball)
```bash
python3 scripts/trace_check.py extracted.png paths.json
```
Prints **IoU** and writes `overlay.png`:
grey = correct, **orange = logo pixels you missed**, **green = your stroke spilled
outside the logo**. Nudge the coordinates toward the orange, away from the green,
re-run. Target **IoU ≥ 0.93** (0.95+ is achievable and looks pixel-perfect).

Common IoU fixes:
- Uniform green halo everywhere → `stroke_width` too big.
- Orange along one edge only → that segment's centerline is offset; move it.
- Orange blob at a corner → add/curve a `Q` so the centerline actually reaches
  into the corner.

### 4. Preview the motion
```bash
python3 scripts/logo_probe.py extracted.png --frames paths.json --stroke 88
```
Writes `.frames.png` — a 6-step strip of the draw-on. Confirm the stroke order
tells a nice story (e.g. base → up → over the top → down) before wiring it in.

---

## C. Wiring into the app

Copy `assets/logo_draw_animation.dart` into the project (e.g.
`lib/core/widgets/logo_draw_animation.dart`), then edit the `LogoPaths` block:
paste `strokes()`, set `designWidth/Height`, `strokeWidth`, `brandColor`
(reuse the repo's color constant), and `finalAsset` (or null).

**Splash.** Swap the static logo for:
```dart
AnimatedDrawLogo(size: 150.w) // draws, then fades to finalAsset
```
Keep the screen's existing navigation timer. If the app uses a `Hero`, keep it
wrapping the widget.

**Loading.** Repoint the app's loader wrapper(s) at `DrawingLoadingIndicator`,
**keeping the old class name and constructor signature** so existing call sites
compile unchanged:
```dart
class CustomLoading extends StatelessWidget {
  const CustomLoading({super.key, this.height});
  final double? height;
  @override
  Widget build(BuildContext context) =>
      Center(child: DrawingLoadingIndicator(size: (height ?? 80) * 0.8));
}
```
Grep for every call site (`grep -rn CustomLoading lib/`) and sanity-check tight
layouts (rows, buttons) since the drawn logo's width = `size * dw/dh`.

## D. Tuning knobs

- **Draw speed / cadence.** `AnimatedDrawLogo.duration` (~2.4–2.8s reads well on
  a splash). In the widget, the `0.74` split is draw-vs-fade; the loader's
  `0.68` / `0.82` are draw / hold-then-fade boundaries.
- **Curve.** `Curves.easeInOutCubic` gives a natural accel/decel. `Curves.linear`
  feels mechanical; `easeOutCubic` feels like it "lands."
- **Color pulse.** For extra life, lerp `color` over the draw, or add a subtle
  scale (`Transform.scale`) on the fade-in.
- **Flutter version.** `.withValues(alpha:)` needs Flutter ≥ 3.27; on older
  Flutter use `.withOpacity(...)`.
- **Performance.** The loader wraps its `CustomPaint` in a `RepaintBoundary`.
  The painter's PathMetrics are cached in `static final` fields — safe at runtime,
  but a hot reload won't pick up path edits (do a hot **restart** after changing
  `LogoPaths`).

## E. Native splash screen — seamless handoff

**You cannot run the draw-on on the true native splash.** The OS draws the
native splash (iOS `LaunchScreen.storyboard`, Android `launch_background` /
Android-12 `SplashScreen`) *before* the Flutter engine boots, so no Dart /
`CustomPainter` runs there. iOS forbids launch-screen animation outright;
Android < 12 is static; Android 12+ allows only a short (~1s, circle-masked)
`AnimatedVectorDrawable`.

The professional result is a **seamless handoff**: keep the native splash a
static frame that is *pixel-identical* to the Flutter animation's first frame,
so the native→Flutter switch is invisible, then let the draw-on play in Flutter.
This needs **zero native-asset changes** if you design the first frame to match:

1. **Match the background** — native splash `color` == the Flutter `Scaffold`
   background (both usually white).
2. **Match size + position** — the native logo shows at a fixed *point* size
   (e.g. `flutter_native_splash` LaunchImage @1x/@2x/@3x = 240/480/720 px →
   **240pt**), centered in the screen. Render the Flutter widget at that **same
   fixed point size** (`size: 240`, not a `.w`/`.sp` responsive size, so it
   doesn't drift per device) and center it in the *whole* screen (a `Stack`
   with `Center` + a bottom-aligned version label), not in a `Column` that
   offsets it.
3. **Match the first frame's appearance** — the native splash shows the *solid*
   logo, so the Flutter animation's frame 0 must also be the solid logo. Don't
   start the draw from blank (that jump-cuts). Instead **hold the solid logo for
   the first ~0.14 of the timeline, then have it "come to life"**: dim the solid
   asset to a faint guide (opacity 1.0 → ~0.15) while the pen inks the crisp
   mark on top, ending solid again. The shape is always on screen, so there is
   no flicker — see `AnimatedDrawLogo`'s builder for this exact timeline.

Check the native display size before choosing the Flutter `size`: for
`flutter_native_splash`, the generated `LaunchImage@3x.png` width ÷ 3 = the point
size. Confirm the storyboard centers the image in the full screen (contentMode
`center`, edges pinned) so `Center` matches it.

If you specifically want a *native* draw-on on Android 12+, hand-author an
`AnimatedVectorDrawable` from the same traced paths using an `<objectAnimator
android:propertyName="trimPathEnd" 0→1>`, referenced by
`windowSplashScreenAnimatedIcon` with `windowSplashScreenAnimationDuration`
≤ 1000ms. iOS still can't animate, so pair it with the seamless handoff above.

## F. Gotchas

- A single full-canvas `<rect fill="url(#pattern)">` in the SVG is the raster
  wrapper, not real art — `inspect_svg.py` already ignores it.
- If `logo_probe.py` shows a **filled silhouette** (no interior holes) rather
  than strokes, the logo isn't stroke-based; animate its **outline** (trace the
  perimeter as one closed stroke) and cross-fade to the filled asset, or use a
  mask-reveal instead of a pen-draw.
- Keep the design coordinate space consistent between `paths.json`,
  `trace_check.py`, and `LogoPaths` — mixing image-pixel and viewBox spaces is
  the usual cause of a wildly wrong IoU.
