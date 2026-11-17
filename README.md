# MetroFuse plugin documentation

Build plugins for [MetroFuse](https://github.com/956tris/MetroFuse). This public guide covers API 1.1.0, universal JavaScript MFP archives, desktop Kotlin JARs and Android Kotlin APKs.

The application's core supplies plugin management, provider routing, the Home source switcher and a place to host each plugin's account screen. Plugins own their content, login UI and authentication callbacks. Reusable WebViews live in the plugin SDK. The profile menu and Settings remain available for every source. Offline playback belongs to the application.

| Start here | Guide |
| --- | --- |
| Build and import your first plugin | [Quickstart](docs/quickstart.md) |
| Required metadata, compatibility and settings | [Manifest](docs/manifest.md) |
| Universal JavaScript, HTTP, data, providers and UI | [JavaScript development](docs/javascript-plugin-development.md) |
| Binary HTTP and session-owned WebSockets | [Plugin networking](docs/plugin-network.md) |
| Playback occurrences, queue sync, Canvas and artist details | [Player and metadata extensions](docs/player-metadata-extensions.md) |
| Native Kotlin, Compose, JAR and APK builds | [Native development](docs/native-plugin-development.md) |
| Every public contract and ownership rules | [API reference](docs/plugin-api.md) |
| Home shelves and host-rendered login | [Home and login](docs/plugin-home-login.md) |
| WebView sign-in and automatic session capture | [Browser sign-in](docs/browser-login.md) |
| Package layout, local installation and updates | [Packaging and lifecycle](docs/packaging.md) |
| Publish downloadable packages and registry entries | [Marketplace](docs/plugin-marketplace.md) |
| Verify behavior and diagnose failures | [Testing and troubleshooting](docs/testing.md) |
| Understand the host integration | [Architecture](docs/plugin-architecture.md) |
| Complete JioSaavn source and JAR/APK/MFP downloads | [Source](https://github.com/956tris/MetroFuse-JioSaavn), [Releases](https://github.com/956tris/MetroFuse-JioSaavn/releases) |
| YouTube Music, InnerTubeX, WebView sign-in and Home | [Source](https://github.com/956tris/MetroFuse-YouTube-Music), [Releases](https://github.com/956tris/MetroFuse-YouTube-Music/releases) |
| Spotify metadata, login, Canvas and listening reports | [Source](https://github.com/956tris/MetroFuse-Spotify), [Releases](https://github.com/956tris/MetroFuse-Spotify/releases) |
| MetroFlow custom interface | [Source](https://github.com/956tris/MetroFuse-MetroFlow), [Releases](https://github.com/956tris/MetroFuse-MetroFlow/releases) |
| Source credits and license | [Provenance](PROVENANCE.md), [GPL-3.0](LICENSE) |

Each plugin has its own repository. [MetroFuse-JioSaavn](https://github.com/956tris/MetroFuse-JioSaavn) contains the complete reference implementation, independent build configuration and JAR/APK/MFP downloads. This repository contains the guide, [API source reference](reference/README.md) and authoring tools.

The API is experimental and exact-version checked. Native plugins must also match the Kotlin/Compose ABI. No public Maven SDK or official marketplace registry is currently provided. Native plugins execute trusted code inside the application process.
