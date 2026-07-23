// Self-drawing logo animation. Drop this into e.g. lib/core/widgets/ and:
//   1. Paste your verified centerline paths into `LogoPaths` below.
//   2. Set designWidth / designHeight / strokeWidth to match your trace.
//   3. Set `brandColor` (reuse the app's color constant) and, optionally,
//      `finalAsset` (the real logo image to cross-fade to on the splash).
//
// Two public widgets:
//   AnimatedDrawLogo        -> splash hero: draws once, then fades in finalAsset.
//   DrawingLoadingIndicator -> looping loader: draw -> hold -> fade out -> repeat.
//
// Requires only the Flutter SDK (dart:ui PathMetrics). No extra packages.
// On Flutter < 3.27 replace `.withValues(alpha: x)` with `.withOpacity(x)`.

import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/material.dart';

/// ===========================================================================
/// EDIT THIS BLOCK for your logo.
/// ===========================================================================
class LogoPaths {
  /// The coordinate space your paths are traced in (from paths.json).
  static const double designWidth = 800;
  static const double designHeight = 820;

  /// Full stroke width in the same design space.
  static const double strokeWidth = 88;

  /// Brand color for the drawn strokes.
  static const Color brandColor = Color(0xFFDC562B);

  /// Optional: the real logo asset to cross-fade to at the end of the splash
  /// draw. Set to null to keep the drawn strokes as the final frame.
  static const String? finalAsset = 'assets/images/logo.png';

  /// Your traced strokes, in draw order. Each returns one continuous Path.
  /// Replace the example below with your own from paths.json.
  static List<Path> strokes() => [
        Path()
          ..moveTo(171, 618)
          ..lineTo(171, 462)
          ..quadraticBezierTo(171, 403, 230, 403)
          ..quadraticBezierTo(252, 403, 273, 425)
          ..lineTo(540, 722)
          ..quadraticBezierTo(588, 775, 642, 775)
          ..cubicTo(705.5, 775, 757, 711.5, 757, 660)
          ..lineTo(757, 434)
          ..quadraticBezierTo(757, 374, 713, 333)
          ..lineTo(415, 55)
          ..quadraticBezierTo(400, 41, 385, 55)
          ..lineTo(87, 333)
          ..quadraticBezierTo(43, 374, 43, 434)
          ..lineTo(43, 660)
          ..cubicTo(43, 723.5, 94.5, 775, 158, 775)
          ..quadraticBezierTo(205, 775, 250, 730)
          ..lineTo(318, 667),
        Path()
          ..moveTo(399, 561)
          ..lineTo(528, 421)
          ..quadraticBezierTo(545, 403, 570, 403)
          ..quadraticBezierTo(629, 403, 629, 462)
          ..lineTo(629, 620),
      ];
}

/// ===========================================================================
/// Painter — draws the strokes progressively via PathMetric.extractPath.
/// ===========================================================================
class _DrawingPainter extends CustomPainter {
  _DrawingPainter({
    required this.progress,
    required this.color,
    this.opacity = 1,
  });

  final double progress; // 0 -> nothing, 1 -> complete
  final Color color;
  final double opacity;

  // Metrics are cached statically: the paths are constant, and iterating
  // PathMetrics once up front is cheaper than per-frame recomputation.
  static final List<ui.PathMetric> _metrics = [
    for (final p in LogoPaths.strokes()) ...p.computeMetrics(),
  ];
  static final double _total =
      _metrics.fold(0.0, (sum, m) => sum + m.length);

  @override
  void paint(Canvas canvas, Size size) {
    if (progress <= 0 || opacity <= 0) return;
    final scale = math.min(
      size.width / LogoPaths.designWidth,
      size.height / LogoPaths.designHeight,
    );
    canvas.save();
    canvas.translate(
      (size.width - LogoPaths.designWidth * scale) / 2,
      (size.height - LogoPaths.designHeight * scale) / 2,
    );
    canvas.scale(scale);

    final paint = Paint()
      ..color = color.withValues(alpha: opacity.clamp(0.0, 1.0))
      ..style = PaintingStyle.stroke
      ..strokeWidth = LogoPaths.strokeWidth
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    var remaining = progress.clamp(0.0, 1.0) * _total;
    for (final m in _metrics) {
      if (remaining <= 0) break;
      canvas.drawPath(m.extractPath(0, math.min(remaining, m.length)), paint);
      remaining -= m.length;
    }
    canvas.restore();
  }

  @override
  bool shouldRepaint(_DrawingPainter old) =>
      old.progress != progress ||
      old.color != color ||
      old.opacity != opacity;
}

/// ===========================================================================
/// Splash hero with a SEAMLESS handoff from the native splash screen.
/// Frame 0 is the solid logo (identical to the static native splash), then the
/// logo "comes to life": it dims to a faint guide while the pen inks the crisp
/// mark on top, ending solid. Render at the native logo's fixed point size and
/// center it in the whole screen so the native->Flutter switch is invisible.
/// Requires `finalAsset` (the real logo image) for the solid frames.
/// ===========================================================================
class AnimatedDrawLogo extends StatefulWidget {
  const AnimatedDrawLogo({
    super.key,
    this.size = 160,
    this.duration = const Duration(milliseconds: 2600),
    this.color = LogoPaths.brandColor,
  });

  final double size; // rendered width; height follows the aspect ratio
  final Duration duration;
  final Color color;

  @override
  State<AnimatedDrawLogo> createState() => _AnimatedDrawLogoState();
}

class _AnimatedDrawLogoState extends State<AnimatedDrawLogo>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c =
      AnimationController(vsync: this, duration: widget.duration)..forward();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final height =
        widget.size * LogoPaths.designHeight / LogoPaths.designWidth;
    return SizedBox(
      width: widget.size,
      height: height,
      child: AnimatedBuilder(
        animation: _c,
        builder: (context, _) {
          final t = _c.value;
          // 0.00-0.14: hold the solid logo (matches the native splash frame).
          // 0.14-1.00: pen inks the crisp mark while the solid logo dims to a
          //            faint guide (1.0 -> 0.15), so the shape is always present.
          const hold = 0.14;
          final draw = Curves.easeInOutCubic
              .transform(((t - hold) / (1 - hold)).clamp(0.0, 1.0));
          final dim =
              Curves.easeInOut.transform(((t - hold) / 0.30).clamp(0.0, 1.0));
          final imageOpacity = 1.0 - 0.85 * dim; // 1.0 -> 0.15
          return Stack(
            fit: StackFit.expand,
            children: [
              // Bottom: the authentic asset — solid at the handoff, then a ghost.
              if (LogoPaths.finalAsset != null)
                Opacity(
                  opacity: imageOpacity,
                  child: Image.asset(LogoPaths.finalAsset!, fit: BoxFit.contain),
                ),
              // Top: the pen draws the crisp mark over the guide.
              CustomPaint(
                painter: _DrawingPainter(progress: draw, color: widget.color),
              ),
            ],
          );
        },
      ),
    );
  }
}

/// ===========================================================================
/// Loading indicator: draw -> hold -> fade out -> repeat.
/// ===========================================================================
class DrawingLoadingIndicator extends StatefulWidget {
  const DrawingLoadingIndicator({
    super.key,
    this.size = 64,
    this.duration = const Duration(milliseconds: 1800),
    this.color = LogoPaths.brandColor,
  });

  final double size; // rendered height; width follows the aspect ratio
  final Duration duration;
  final Color color;

  @override
  State<DrawingLoadingIndicator> createState() =>
      _DrawingLoadingIndicatorState();
}

class _DrawingLoadingIndicatorState extends State<DrawingLoadingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c =
      AnimationController(vsync: this, duration: widget.duration)..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final width =
        widget.size * LogoPaths.designWidth / LogoPaths.designHeight;
    return SizedBox(
      width: width,
      height: widget.size,
      child: RepaintBoundary(
        child: AnimatedBuilder(
          animation: _c,
          builder: (context, _) {
            final t = _c.value;
            final draw =
                Curves.easeInOutCubic.transform((t / 0.68).clamp(0.0, 1.0));
            final opacity =
                1 - Curves.easeIn.transform(((t - 0.82) / 0.18).clamp(0.0, 1.0));
            return CustomPaint(
              painter: _DrawingPainter(
                progress: draw,
                color: widget.color,
                opacity: opacity,
              ),
            );
          },
        ),
      ),
    );
  }
}
