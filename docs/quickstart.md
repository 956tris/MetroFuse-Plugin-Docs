# Build your first plugin

Keep each plugin in its own repository. Use JavaScript for one MFP package that runs on desktop and Android. Use Kotlin for direct typed providers or native Compose UI, with a desktop JAR and Android APK. Both use API 1.1.0.

## Build the reference plugin

[MetroFuse-JioSaavn](https://github.com/956tris/MetroFuse-JioSaavn) is a separate repository with source, build tools and JAR/APK/MFP downloads.

```powershell
git clone https://github.com/956tris/MetroFuse-JioSaavn.git
cd MetroFuse-JioSaavn
./tooling/pack-mfp.ps1 -Source ./javascript -Output ./build/plugin-examples/jiosaavn.mfp
```

Open MetroFuse's Plugins page, or Settings → Plugins. Import the MFP, then enable it. JioSaavn supplies Home, search, metadata, catalog and audio. It has no login capability. The native JAR or APK can replace the same owner; choose one implementation at a time.

## Create your own JavaScript plugin

Create a separate repository with a root `manifest.json` and `index.js`. Start with this complete manifest:

```json
{
  "id": "example.lyrics",
  "name": "Example lyrics",
  "author": "Plugin author",
  "version": "1.0.0",
  "api": "1.1.0",
  "runtime": "javascript",
  "platforms": ["desktop", "android"],
  "script": "index.js",
  "capabilities": ["lyrics"]
}
```

Implement the entrypoint in `index.js`:

```javascript
globalThis.plugin = {
  init(host) {
    host.lyrics('example.lyrics.provider', async request => ({
      source: 'Local example',
      lines: [{text: request.identity.canonicalId, timeMs: 0}]
    }));
  }
};
```

This demonstrates a callback contract rather than retrieving real lyrics. Choose your own unique ID and actual author credit before distributing it. Implement the service or local-data lookup you need. The host removes this registration on disable.

Copy the [MFP packer](../tooling/pack-mfp.ps1) into your plugin repository and run it with `-Source` pointing at your package folder and `-Output` pointing at a `.mfp` file outside that folder. Avoid packaging build outputs recursively. Then import and enable the artifact in a development profile. Use the [JavaScript guide](javascript-plugin-development.md) for HTTP, data, UI and lifecycle callbacks.

## Create a native plugin

Install Java 25. Match Kotlin 2.4.21, Compose 1.13.0-beta02 and API 1.1.0. Android packaging needs SDK platform `android-37.0` and build tools `37.0.0`.

Obtain the API JAR by running `:plugin-api:desktopJar` in a separate MetroFuse KMP checkout. Compile your plugin in its own repository against `plugin-api/build/libs/plugin-api-desktop-1.1.0.jar` as a compile-only dependency. The application does not currently publish a Maven SDK.

Use JioSaavn's independent Gradle configuration as a working reference:

```powershell
./gradlew.bat :native:desktopTest :native:packagePluginJar :native:packagePluginApk '-PmetrofuseApiJar=../MetroFuse/plugin-api/build/libs/plugin-api-desktop-1.1.0.jar' --no-configuration-cache
```

Run this from the JioSaavn repository and adjust the API JAR path. Configure `ANDROID_HOME` or untracked `local.properties` before APK packaging. On Linux/macOS use `./gradlew`. Outputs are in `build/plugin-examples`. Import the JAR on desktop or the APK inside the Android host, rather than installing the plugin as a separate app.

For your own implementation, choose a unique ID, update the entry class and give it a public no-argument constructor implementing `NativePlugin`. Declare host API/runtime dependencies as compile-only and package only your compiled code, assets and required notices. Use [native development](native-plugin-development.md) for dependency declarations, packaging and lifecycle requirements.
