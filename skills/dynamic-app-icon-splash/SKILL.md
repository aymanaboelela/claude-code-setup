---
name: dynamic-app-icon-splash
description: Change a Flutter app's launcher icon and in-app splash screen for holidays/occasions (Ramadan, Eid, White Friday, national days, sales) WITHOUT shipping a store update, driven by remote config. Use for ANY Flutter project when the user wants seasonal/occasion app icons, a themed splash, "تغيير الأيقونة في العيد/رمضان/المناسبات", alternate app icons, dynamic splash, or remote-controlled branding. Covers iOS alternate icons, Android activity-alias, flutter_dynamic_icon_plus, remote splash loading, and a DynamicAppIconService. Substitute the project's own applicationId/bundle id for the placeholders.
---

# Dynamic App Icon & Splash (Flutter, any project)

Swap the launcher icon and the in-app splash for occasions **without a store release**, controlled remotely. Generic — replace `<applicationId>` with the target project's Android applicationId / iOS bundle id. (Worked example: TLN uses `tln.app.com`.)

## The one rule that shapes everything

- **Launcher icons are build-time.** iOS and Android can only *toggle between icons that already shipped in the binary*. So every occasion icon (ramadan, eid_fitr, eid_adha, white_friday, national_day, default) must be **pre-bundled**. A brand-new icon still needs a release.
- **Splash images are runtime.** The in-app Dart splash loads an image from a URL, so it changes freely with no release. The *native* launch screen (`flutter_native_splash`) is build-time — do NOT try to make it remote.

Play each season: pre-ship a batch of icons once, then remotely activate the right one + push a splash URL.

## Architecture

- **iOS**: `CFBundleAlternateIcons` in `ios/Runner/Info.plist` + `flutter_dynamic_icon_plus`.
- **Android**: one `<activity-alias>` per icon (all `enabled="false"` except DEFAULT) in `android/app/src/main/AndroidManifest.xml`, toggled via `MethodChannel("<applicationId>/dynamic_app_icon")` in `MainActivity`.
- **Remote config source**: the project's own backend/config service. Firestore works (original article), but if the app already has a backend API prefer a small config endpoint there; an FCM **data** message can trigger an immediate re-check.
- **Splash host**: any CDN/URL. Cache-bust with `?v=<version>`.
- **Service**: a `DynamicAppIconService` that validates keys, de-dupes (skip if already active), persists last-good config to `shared_preferences`, handles the iOS change-alert/cooldown, and always falls back to DEFAULT.

## Config shape (served remotely)

```json
{
  "icon": { "enabled": true, "active_icon": "ramadan", "icon_version": 2 },
  "splash": { "use_default": false, "image_url": "https://.../ramadan-splash.webp", "image_version": 4 }
}
```

## Splash load strategy (never block launch)

```
Start → read cached splash config → show it immediately
      → fetch config in background → precache new image
      → on success: save config → use it next launch
      → on any failure: keep last-good / bundled default
```

**Guiding principle:** the feature must *improve* experience, never become a launch blocker. Every error degrades gracefully to last-known-good.

## Do this in order

1. `flutter_dynamic_icon_plus` (+ `cached_network_image`, `shared_preferences` if missing) in `pubspec.yaml`.
2. Generate icon sizes for every occasion (REFERENCE.md — `sips` commands).
3. iOS: drop icons in `ios/Runner/` + register in `Info.plist` (incl. `~ipad`).
4. Android: add `<activity-alias>` blocks + `MainActivity` MethodChannel handler.
5. Build `DynamicAppIconService` + the remote splash widget.
6. Wire remote config (backend/Firestore + optional FCM refresh trigger).
7. Test: kill/relaunch after each toggle; verify DEFAULT fallback on config failure.

## Full code + platform setup

See [REFERENCE.md](REFERENCE.md) — exact Info.plist entries, AndroidManifest aliases, MainActivity Kotlin, the Dart service, and splash widget. Replace `<applicationId>` throughout with the project's id before use.
