# Player and metadata extensions

These additions require the patched MetroFuse UI SDK host release. API 1.1.0 constructor signatures remain unchanged, so the API version alone does not identify a host with these extensions. Build native plugins against the matching exported API and SDK JARs.

## Playback occurrences and upcoming queue

`PlaybackState.currentIndex` is the current queue index when known. `playbackInstanceId` identifies the actual playback occurrence, including repeat plays of the same track. Both are nullable body properties. They participate in equality so occurrence changes reach observers. Kotlin's generated `copy()` does not copy body properties; assign them explicitly when constructing a new snapshot.

The optional `UpcomingQueuePlayer` interface adds `replaceUpcomingQueue(List<Track>)`. Check the interface and the `replaceUpcomingQueue` player capability before calling. The JavaScript equivalents are `host.playerCapabilities()` and `host.replaceUpcomingQueue(tracks)`. The host preserves the current entry and replaces only entries after it. Duplicate tracks remain distinct entries. The limit is 1,000 upcoming tracks. Empty input clears upcoming entries, so a provider must reject incomplete server snapshots before calling.

`host.locale()` returns the system language tag, country and time zone. Use these values rather than hardcoded account-market defaults.

## Canvas and artist details

Register `artwork.canvas/v1` to receive `{track}` and return `{url}` when matching Canvas is available. The host calls the selected service only for its enabled, logged-in owner and discards results after account or owner changes. It routes the result into its existing Canvas renderer. Return an absent URL when no matching artwork exists.

Register `catalog.artist-metadata/v1` to receive `{id}` and return artist details directly or inside `metadata`. The host selects the service belonging to the catalog owner. Supported fields are `biography`, `monthlyListeners`, `featuring` as `CatalogAlbum` entries, `relatedArtists` as `CatalogArtist` entries, and `playlists` as `CatalogPlaylist` entries. `concerts` and `merch` entries supply a title or name and URL or URI, plus optional city, venue, startDateIso or price. The host validates external HTTPS links and bounds list and text sizes. Omit unavailable fields.

## Video button

Register `playback.video/v1` to hook the player's video button for any provider (direct MP4/WebM, HLS `.m3u8`, custom HTTP headers such as `Referer`/auth tokens, or optional SABR). The host resolves the track's audio through the plugin's `AudioSource` as usual, then calls this service with `{track, maxHeight?, allowSabr, allowHls}` (with `allowHls` defaulting to `true`) and expects `{url}` or `{sabr}` (or both), plus optional `headers`, `mimeType`, `codecs`, `width`, `height`, `bitrate`, `itag`, `contentLengthBytes`, `expiresAtMillis`, `availableHeights` and `mediaId`. The host merges any returned `headers` with the audio stream headers, keeps the audio it already resolved, and renders the returned video stream as the picture. Return an empty object when the track has no video; the host then reports video unavailable.

The host calls the service only for the enabled plugin that is the current music source, discards results if that selection changes, bounds `url` to 8192 characters, `sabr` to 256 KiB, `availableHeights` to 32 entries (`1..4320`), and `headers` to 32 entries, and times out after 15 seconds. Native plugins can use `PluginContext.registerVideoProvider(PluginVideoRequestProvider)` (or `PluginVideoProvider`) from the plugin SDK, which registers this service and handles the JSON shape.

## Native dialogs and Android packaging

Use the SDK's `PluginAlertDialog` for account dialogs compiled against the desktop SDK and packaged for Android. Its expect/actual implementations call each platform's Compose dialog API. A desktop-only Compose call can otherwise leave a `_skikoKt` reference in Android DEX.

Keep API, SDK, Compose and their resources compile-only. Reject bundled host classes and desktop Skiko references in Android package checks. The patched host retains `org.jetbrains.compose.resources`, including `StringResourcesKt`, in minified releases and loads those classes from the parent host.
