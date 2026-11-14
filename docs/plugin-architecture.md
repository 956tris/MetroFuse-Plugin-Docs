# Plugin architecture

MetroFuse retains the upstream KMP/Compose host and native playback engines. `plugin-api` contains versioned Kotlin contracts; `engine` contains the unified registry, lifecycle, package installation, provider pipelines and QuickJS bridge. Shared JVM host adapters attach capabilities to the existing player. Android and desktop use the same registry rather than separate plugin systems.

There are two ecosystems: universal JavaScript ZIP archives named `.mfp`, and native Kotlin plugins compiled as desktop `.jar` or Android `.apk`. There is no native `.mfp` or hybrid plugin format. Native developers share source and compile separate platform artifacts. Native plugins run in process as trusted code, with direct Kotlin calls and parent delegation to the host API; classloader close does not guarantee immediate class unloading.

The plugin API and engine derive from earlier MetroFuse prototype implementations. Only their API and runtime were integrated into the KMP host. The host playback backend and application UI remain based on Metrolist. Contributor headers and the GPL-3.0 license remain intact. See [provenance](../PROVENANCE.md).

Provider resolution uses immutable registry snapshots, bounded timeouts, cancellation and stable priority ordering. Native calls remain typed. JSON is used at the JavaScript boundary and versioned general service boundary. Registration is staged during initialization, then published as a batch. Disabling removes capabilities and UI, cancels plugin coroutines/listeners and releases the runtime.

`AudioQuery.quality.preset` preserves the actual application selection (`AUTO`, `LOW`, `HIGH`, `MP4`) for native and JavaScript providers. Providers interpret it against their available formats: automatic choice, economical/low bitrate, highest quality, or MP4 audio preference. The host does not invent fixed bitrate ceilings or treat `HIGH` as a lossless request. Explicit `maxBitrate`, `lossless` and `preferredCodecs` remain separate typed preferences. The upstream YouTube resolver continues to receive the original `AudioQuality` unchanged when plugin resolution falls back.

`shared/src/desktopTest/kotlin/com/metrolist/shared/plugins/PluginPlaybackIntegrationTest.kt` authors real JAR and `.mfp` fixture packages, installs/enables each through the application host, resolves through `PluginStreamResolver`, and prepares/plays local PCM through the existing `MusicPlayer` and FFmpeg decoder. The deterministic output line checks readiness, position and state without requiring speaker hardware. The test also checks all quality presets and provider/session removal; actual execution results are recorded separately.

QuickJS 1.0.15 supplies Windows x64 and Android native libraries. Contexts are retained per activation, with memory/stack budgets, evaluation interruption and asynchronous host functions. The previous desktop package policy prohibiting QuickJS is replaced by checks requiring the chosen runtime and Windows library; other integrity checks remain enabled.

See [testing and platform limits](testing.md) before distributing a package. Tests in source are separate from evidence that a particular packaged app passed them.
