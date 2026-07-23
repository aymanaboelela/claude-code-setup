# REFERENCE — Dynamic App Icon & Splash (generic)

Replace `<applicationId>` with the target project's Android applicationId / iOS bundle id. MethodChannel = `<applicationId>/dynamic_app_icon`. If the project uses flavor suffixes (e.g. `.dev`), the base package for Android alias resolution is the un-suffixed id.

Worked example — **TLN**: `<applicationId>` = `tln.app.com` (dev suffix `.dev`), channel `tln.app.com/dynamic_app_icon`, already has `cached_network_image`, `shared_preferences`, `firebase_messaging`, `flutter_native_splash`; needs to add `flutter_dynamic_icon_plus`.

Supported icon keys (extend as needed): `default`, `ramadan`, `eid_fitr`, `eid_adha`, `white_friday`, `national_day`.

---

## 0. Dependency

```yaml
# pubspec.yaml
dependencies:
  flutter_dynamic_icon_plus: ^1.2.0   # check pub.dev for latest
  cached_network_image: ^3.4.1        # if not already present
  shared_preferences: ^2.5.3          # if not already present
```

---

## 1. Generate icon assets (macOS `sips`)

From one square source PNG (e.g. `RAMADAN.PNG`, ≥1024px):

**Android** (place under `android/app/src/main/res/mipmap-*`):
```bash
sips -z 48  48  RAMADAN.PNG --out mipmap-mdpi/ic_launcher_ramadan.png
sips -z 72  72  RAMADAN.PNG --out mipmap-hdpi/ic_launcher_ramadan.png
sips -z 96  96  RAMADAN.PNG --out mipmap-xhdpi/ic_launcher_ramadan.png
sips -z 144 144 RAMADAN.PNG --out mipmap-xxhdpi/ic_launcher_ramadan.png
sips -z 192 192 RAMADAN.PNG --out mipmap-xxxhdpi/ic_launcher_ramadan.png
```

**iOS** (place under `ios/Runner/` — filenames must match `Info.plist` keys):
```bash
sips -z 120 120 RAMADAN.PNG --out ramadan@2x.png       # iPhone
sips -z 180 180 RAMADAN.PNG --out ramadan@3x.png       # iPhone
sips -z 152 152 RAMADAN.PNG --out ramadan~ipad@2x.png  # iPad (optional)
```
Repeat for every occasion key. Also bundle a 512×512 preview per icon under `assets/icon_previews/` for the splash error fallback.

---

## 2. iOS — Info.plist

`CFBundlePrimaryIcon` stays your normal AppIcon asset-catalog entry.

```xml
<key>CFBundleIcons</key>
<dict>
  <key>CFBundleAlternateIcons</key>
  <dict>
    <key>ramadan</key>
    <dict>
      <key>CFBundleIconFiles</key><array><string>ramadan</string></array>
      <key>UIPrerenderedIcon</key><false/>
    </dict>
    <key>eid_fitr</key>
    <dict>
      <key>CFBundleIconFiles</key><array><string>eid_fitr</string></array>
      <key>UIPrerenderedIcon</key><false/>
    </dict>
    <!-- eid_adha, white_friday, national_day … same shape -->
  </dict>
</dict>

<!-- iPad variants (only if you ship ipad icons) -->
<key>CFBundleIcons~ipad</key>
<dict>
  <key>CFBundleAlternateIcons</key>
  <dict>
    <key>ramadan</key>
    <dict>
      <key>CFBundleIconFiles</key><array><string>ramadan~ipad</string></array>
      <key>UIPrerenderedIcon</key><false/>
    </dict>
  </dict>
</dict>
```

iOS shows a system alert ("You have changed the icon…") on switch — unavoidable with the public API. De-dupe so it only fires on an actual change.

---

## 3. Android — AndroidManifest.xml

Keep the real `<activity android:name=".MainActivity">` with its launcher intent-filter (the DEFAULT), then add one alias per occasion. Aliases use a **relative name** (`.ramadan`) which resolves against `<applicationId>` regardless of flavor suffix.

```xml
<activity-alias
    android:name=".ramadan"
    android:enabled="false"
    android:exported="true"
    android:icon="@mipmap/ic_launcher_ramadan"
    android:label="@string/app_name"
    android:targetActivity=".MainActivity">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity-alias>
<!-- repeat: .eid_fitr, .eid_adha, .white_friday, .national_day -->
```

Model: treat the base `MainActivity` as `default`; only ONE launcher component is enabled at a time. Enable target, disable the rest.

---

## 4. Android — MainActivity MethodChannel

`android/app/src/main/kotlin/…/MainActivity.kt` (package = `<applicationId>`):

```kotlin
package <applicationId>   // e.g. tln.app.com

import android.content.ComponentName
import android.content.pm.PackageManager
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val channel = "<applicationId>/dynamic_app_icon"
    private val aliases = listOf(
        "ramadan", "eid_fitr", "eid_adha", "white_friday", "national_day"
    )

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channel)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "setIcon" -> {
                        val key = call.argument<String>("icon") ?: "default"
                        try { setIcon(key); result.success(true) }
                        catch (e: Exception) { result.error("SET_ICON_FAILED", e.message, null) }
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun setIcon(key: String) {
        val pm = packageManager
        val pkg = packageName                 // may carry a flavor suffix
        val base = "<applicationId>"          // un-suffixed base for alias resolution
        val enable = if (key == "default") "$base.MainActivity" else "$base.$key"
        val all = aliases.map { "$base.$it" } + "$base.MainActivity"
        all.forEach { comp ->
            val state = if (comp == enable)
                PackageManager.COMPONENT_ENABLED_STATE_ENABLED
            else PackageManager.COMPONENT_ENABLED_STATE_DISABLED
            pm.setComponentEnabledSetting(
                ComponentName(pkg, comp), state, PackageManager.DONT_KILL_APP
            )
        }
    }
}
```

> Verify alias/component naming on a real device, including any flavor suffix build. Toggling the last enabled launcher component can briefly remove the icon; always enable-then-disable, `DONT_KILL_APP`, and re-check after relaunch.

---

## 5. Dart — DynamicAppIconService

```dart
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:flutter_dynamic_icon_plus/flutter_dynamic_icon_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

class DynamicAppIconService {
  static const _channel = MethodChannel('<applicationId>/dynamic_app_icon');
  static const _kActiveIcon = 'active_app_icon';
  static const _kIconVersion = 'active_icon_version';
  static const _supported = {
    'default', 'ramadan', 'eid_fitr', 'eid_adha', 'white_friday', 'national_day',
  };

  Future<void> apply({required String iconKey, required int version}) async {
    if (!_supported.contains(iconKey)) return;            // unknown → stay safe
    final prefs = await SharedPreferences.getInstance();
    final current = prefs.getString(_kActiveIcon) ?? 'default';
    final currentVer = prefs.getInt(_kIconVersion) ?? 0;
    if (current == iconKey && currentVer == version) return; // de-dupe

    try {
      if (Platform.isIOS) {
        await FlutterDynamicIconPlus.setAlternateIconName(
          iconName: iconKey == 'default' ? null : iconKey,
        );
      } else {
        await _channel.invokeMethod('setIcon', {'icon': iconKey});
      }
      await prefs.setString(_kActiveIcon, iconKey);
      await prefs.setInt(_kIconVersion, version);
    } catch (_) {
      // graceful fallback: keep last-good icon
    }
  }

  Future<void> resetToDefault() => apply(iconKey: 'default', version: 0);
}
```

Call `apply(...)` from config sync, after first frame — not on the cold-launch critical path.

---

## 6. Remote config sync

Fetch the JSON (see SKILL.md) from Firestore OR the project backend. Optional FCM **data** message `{"type":"app_theme_refresh"}` triggers an immediate re-sync.

```dart
class AppThemeConfig {
  final bool iconEnabled;
  final String activeIcon;
  final int iconVersion;
  final bool useDefaultSplash;
  final String? splashUrl;
  final int splashVersion;
  const AppThemeConfig({ this.iconEnabled = false,
    this.activeIcon = 'default', this.iconVersion = 0,
    this.useDefaultSplash = true, this.splashUrl, this.splashVersion = 0});

  factory AppThemeConfig.fromJson(Map<String, dynamic> j) => AppThemeConfig(
    iconEnabled: j['icon']?['enabled'] ?? false,
    activeIcon: j['icon']?['active_icon'] ?? 'default',
    iconVersion: j['icon']?['icon_version'] ?? 0,
    useDefaultSplash: j['splash']?['use_default'] ?? true,
    splashUrl: j['splash']?['image_url'],
    splashVersion: j['splash']?['image_version'] ?? 0,
  );
}

// After a successful fetch:
if (cfg.iconEnabled) {
  await DynamicAppIconService().apply(iconKey: cfg.activeIcon, version: cfg.iconVersion);
} else {
  await DynamicAppIconService().resetToDefault();
}
// persist cfg json to shared_preferences for the splash to read next launch
```

---

## 7. Remote splash widget

Shown after the native launch screen. Reads cached config first, shows immediately, refreshes in background.

```dart
Widget buildSplash(AppThemeConfig cfg) {
  if (cfg.useDefaultSplash || cfg.splashUrl == null) {
    return const DefaultSplash();             // existing branded splash
  }
  final url = '${cfg.splashUrl}?v=${cfg.splashVersion}'; // cache-bust on version bump
  return CachedNetworkImage(
    imageUrl: url,
    fit: BoxFit.cover,
    placeholder: (_, __) => const DefaultSplash(),
    errorWidget: (_, __, ___) => const DefaultSplash(), // graceful fallback
  );
}
```

Precache on config fetch so the *next* launch is instant:
```dart
if (!cfg.useDefaultSplash && cfg.splashUrl != null) {
  await precacheImage(
    CachedNetworkImageProvider('${cfg.splashUrl}?v=${cfg.splashVersion}'),
    context,
  );
}
```

---

## 8. Test checklist

- [ ] Toggle each icon → kill app → relaunch → correct icon (all flavors/suffixes).
- [ ] iOS system change-alert appears only on an actual change (de-dupe works).
- [ ] Airplane mode on first launch → last-good / default splash, never blank, never crashes.
- [ ] Config `enabled:false` → icon resets to default.
- [ ] Unknown `active_icon` key → ignored, stays on current.
- [ ] Splash `image_version` bump → new image after one launch cycle.

## Gotchas

- Android alias toggling can momentarily drop the launcher icon; enable-then-disable, `DONT_KILL_APP`.
- iOS alternate icon change always alerts the user — product should expect it.
- Native `flutter_native_splash` screen is **build-time only** — remote splash applies to the Dart splash, not the OS launch screen.
- Widget/badge/notification icons are separate; this covers the launcher icon + in-app splash only.
