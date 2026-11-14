# Testing and troubleshooting

Verify the package and the host behavior separately. A passing compilation does not establish audible playback, service availability or Android credential restoration.

## Before distribution

1. Package the real artifact and inspect its manifest location, explicit API, native ABI and entrypoint.
2. Verify ZIP integrity and SHA-256, including each declared MFP payload digest. Keep host libraries out of native packages.
3. Import into a separate development profile, enable, disable, reload, update and uninstall. Check cleanup and restart persistence.
4. Exercise provider success, empty results, errors, timeout and cancellation. Use licensed local audio for deterministic playback checks.
5. Test the downloaded release package on every claimed platform and architecture. Record the host version, artifact hash, OS and result.

No examples from this guide are installed automatically. Keep test packages and credentials separate from your normal listening profile.

## Relevant source tests

Run these from the application checkout:

```powershell
.\gradlew.bat :engine:desktopTest
.\gradlew.bat :plugin-jiosaavn-native:desktopTest
```

The engine includes `JavaScriptRuntimeTest`, `NativePluginTest`, `PluginHomeTest`, `PluginLoginTest`, `NativeLoginPluginTest` and JioSaavn bridge/routing tests. They exercise real modules, loaders, limits, ownership and lifecycle behavior. The shared host includes plugin playback and frontend/account integration tests. Consult the source when selecting a narrower test filter.

Android runtime validation needs a connected device or emulator and the required plugin packages as test assets. `JavaScriptAndroidTest`, `NativeApkTest` and `JioSaavnApkTest` cover ART/DEX and asynchronous calls. The native fixture test exercises Android MediaPlayer; the application's actual playback path still needs its own check. Credential restoration must be checked across process recreation on a device.

Service-dependent JioSaavn tests are opt-in with `METROFUSE_JIOSAAVN_LIVE=1`, or the instrumentation argument `jiosaavnLive=true` for the documented APK test. A service test can fail independently of package/API correctness. Never publish an opt-in test as passed if it was skipped.

## Home and account checks

For Home, confirm Offline is first, enabled sources appear, selection persists, mixed track/album/artist/playlist items navigate correctly, layouts render and disable/removal switches to Offline. Check slow/error responses, cached content and Retry. Check the desktop popup at different rail widths and with long names; repeat touch selection on Android.

For login, supply only real service-specific callback logic. Check form masking, successful/failed authentication, reactive session expiry, logout and encrypted restoration. Use distinct test plugin IDs to verify account ownership. Credentials must not appear in ordinary storage, diagnostic strings, URLs or logs. Windows uses DPAPI; Android uses Keystore AES-GCM. Linux/macOS credential persistence is unavailable in this implementation.

## Troubleshooting

| Symptom | What to inspect |
| --- | --- |
| Import rejected | Explicit API, correct artifact type/platform, native composeAbi, archive paths and integrity. |
| Enable fails | Diagnostic state, public no-argument entrypoint or globalThis.plugin.init, required dependencies and initialization exceptions. |
| No Home entry | Plugin enabled, `home` capability and implemented HomePlugin or registered host.home callback. |
| No account button | Selected source declares `login` and implements LoginPlugin or registers host.login. JioSaavn does not declare login. |
| Empty search or playback failure | Provider registration, original provider identifiers, configured fixture/service data, supported transport and player capabilities. |
| UI disappears after reload | Expected ownership cleanup; register new controls during the new activation. Never retain old action callbacks. |
| APK replacement needs restart | Bundled native libraries cannot be unloaded safely by ART/JNI. |
| Login cannot persist on desktop | Only Windows currently implements the plugin credential store. |
| HTTP redirects or binary data fail | HTTP returns redirects and UTF-8 text; binary response bodies and automatic host sessions are unsupported. |
| Native plugin hangs the process | Native code must cooperate with cancellation. The host cannot forcibly interrupt arbitrary blocking native code. |

Share version, OS, artifact format/hash and a minimal reproduction with diagnostic codes. Remove tokens, account values and signed media URLs from reports.

## Available verification for this API snapshot

The KMP core Home/login change compiled desktop and Android successfully. Relevant shared checks recorded 37 tests without failures, and the final selected engine checks recorded 26 tests with no failures/errors and one skipped opt-in live test. Native JioSaavn checks recorded four tests without failures. These local results do not assert Android device login checks, Linux/macOS credential support, every native ABI or current public service availability. The documentation examples are validated separately by packaging and checksum checks.
