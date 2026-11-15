# Native Kotlin plugins in a separate repository

Native plugins implement `dev.metrofuse.api.NativePlugin`, API 1.1.0. Keep the plugin's source and releases in its own repository. [MetroFuse-JioSaavn](https://github.com/956tris/MetroFuse-JioSaavn) is the complete native reference with an independent Gradle wrapper, Kotlin source, tests and JAR/APK packaging tasks.

## Obtain the host API

No public Maven SDK is currently published. Clone the application KMP branch into a separate directory and run its API export:

```powershell
git clone --branch KMP --recurse-submodules https://github.com/956tris/MetroFuse.git MetroFuse
cd MetroFuse
./gradlew.bat :plugin-api:desktopJar --no-configuration-cache
```

The output is `plugin-api/build/libs/plugin-api-desktop-1.1.0.jar`. Do not copy application source or plugin code into the host to develop a separate plugin. Use this API JAR only on the plugin's compile classpath.

For plugin-owned WebView screens, also export `:plugin-sdk:desktopJar`. Add `plugin-sdk/build/libs/plugin-sdk-desktop-1.1.0.jar` as a compile-only dependency and enable the matching Compose compiler plugin. The host supplies SDK classes at runtime. Keep those classes out of JAR/APK payloads, while including the SDK on D8's classpath and your test runtime. Windows SDK export requires .NET SDK 10; `-PdotnetExecutable=<path>` selects a local SDK. See [browser sign-in](browser-login.md) and the separate YTM reference for complete build configuration.

The current toolchain is Java 25, Kotlin 2.4.21 and Compose 1.13.0-beta02. Bytecode targets JVM 21. The native manifest ABI is exactly `kotlin-2.4.21_compose-1.13.0-beta02_api-1.1.0`. Rebuild when the host changes that tag. Android packaging additionally requires SDK platform `android-37.0` and build tools `37.0.0`.

## Declare compile-only host dependencies

The reference's `native/build.gradle.kts` accepts `metrofuseApiJar`:

```kotlin
val hostApiJar = providers.gradleProperty("metrofuseApiJar").map { file(it) }
kotlin {
    sourceSets {
        getByName("desktopMain").dependencies {
            compileOnly(files(hostApiJar))
            compileOnly(libs.runtime)
            compileOnly(libs.foundation)
            compileOnly(libs.material3)
            compileOnly(libs.kotlinx.coroutines.core)
            compileOnly(libs.kotlinx.serialization.json)
        }
    }
}
```

Use the pinned version catalog from the reference. Kotlin's plugin supplies the matching standard library for compilation. The packaging tasks include only plugin class outputs, manifest, assets and notices. They exclude host Kotlin, Compose, coroutines, serialization and API class definitions. The importer rejects duplicate host class definitions. Add the matching dependencies separately to your test runtime when tests load the API.

Keep plugin-private dependencies separate. Package the libraries you actually need, honor their licenses and check D8/API compatibility. Cross-plugin dependencies order activation and services; they do not merge classpaths. Use versioned host services to cooperate with another plugin.

## Build JAR and APK

In the separate JioSaavn repository:

```powershell
./gradlew.bat :native:desktopTest :native:packagePluginJar :native:packagePluginApk '-PmetrofuseApiJar=../MetroFuse/plugin-api/build/libs/plugin-api-desktop-1.1.0.jar' --no-configuration-cache
```

Adjust the API JAR path. On Linux/macOS use `./gradlew`. Configure `ANDROID_HOME` or `sdk.dir` in untracked `local.properties` for Android. Do not commit local paths or keys. The existing APK tasks use Gradle script closures and require configuration cache to be disabled.

The JAR is `build/plugin-examples/jiosaavn.jar`, containing compiled classes and root `manifest.json`. The APK is `build/plugin-examples/jiosaavn.apk`, containing D8-compiled DEX, resources and `assets/metrofuse/manifest.json`. AAPT2 links the resource container and zipalign aligns it. Paths use `/`; `resources.arsc` remains stored. APKs are unsigned plugin containers loaded by the host, not separately installed Android apps.

Both artifacts compile one JVM-compatible implementation. Android-specific plugins can use an Android Gradle module with compile-only host APIs instead; their Activities/Services/Receivers/Providers are not installed components. Native libraries need supported device ABIs and documented restart requirements.

## Entrypoint and registration

Give the native entrypoint a public no-argument constructor and implement `start(context)`. Register typed audio, metadata, lyrics, search and catalog providers through `PluginContext`. Use `context.scope` for background work and honor cancellation. Implement `stop()` to release files, sockets and service sessions.

Registrations are staged until startup succeeds. Disable/reload cancels operations, removes providers and UI, calls stop and releases owned loader resources. Keep no global jobs or stale host contexts. Provider calls remain direct Kotlin calls. Initialization must avoid blocking the UI thread.

Native Compose UI uses `NativeScreen.Content(UiContext)` and `NativeComponent.Content(UiNode,UiContext)`. Apply the matching Kotlin Compose compiler plugin in your own build when declaring composable implementations. `UiContext` exposes player, metadata, navigation and optional cooperative extensions. Use REPLACE, BEFORE and AFTER layers. Do not package Compose runtime copies.

Assets are available through `context.resources.readAsset("assets/path")`. Android exposes its public `Resources` object through `platformResources`; desktop has no Android resource table. Do not use hidden AssetManager reflection or expect APK components to become host Activities.

Add `HomePlugin` or `LoginPlugin` alongside `NativePlugin` only when you implement the corresponding optional capability. These companion interfaces preserve existing NativePlugin ABI. See [Home and login](plugin-home-login.md) for shelves, reactive account state and encrypted credential behavior.

## Lifetime and trust

Desktop activation uses private JAR copies to avoid Windows replacement locks. Loaders delegate host API, Kotlin and Compose classes to the host and isolate plugin-private dependencies. Closing a JVM classloader releases owned handles but does not guarantee immediate class unloading.

Android loads read-only private APK copies through DexClassLoader, including multidex and supported bundled native libraries. APKs with native libraries require process restart before replacement. ART/JNI cannot forcibly unload classes/libraries. A desktop plugin can load JNI independently; document its restart requirements.

Native plugins execute trusted code in the host process. Deadlines can cancel suspended operations and discard stale results, but cannot safely terminate arbitrary blocking native code, memory corruption or process termination. Test cleanup and error handling before release.

Use [API reference](plugin-api.md), [testing](testing.md) and the [JioSaavn source](https://github.com/956tris/MetroFuse-JioSaavn/tree/main/native) for complete contracts and a tested independent build.
