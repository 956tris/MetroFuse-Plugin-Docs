# Player and metadata extensions

These additions require the patched MetroFuse UI SDK host release. API 1.1.0 constructor signatures remain unchanged, so the API version alone does not identify a host with these extensions. Build native plugins against the matching exported API and SDK JARs.

## Playback occurrences and upcoming queue

`PlaybackState.currentIndex` is the current queue index when known. `playbackInstanceId` identifies the actual playback occurrence, including repeat plays of the same track. Both are nullable body properties. They participate in equality so occurrence changes reach observers. Kotlin's generated `copy()` does not copy body properties; assign them explicitly when constructing a new snapshot.

The optional `UpcomingQueuePlayer` interface adds `replaceUpcomingQueue(List<Track>)`. Check the interface and the `replaceUpcomingQueue` player capability before calling. The JavaScript equivalents are `host.playerCapabilities()` and `host.replaceUpcomingQueue(tracks)`. The host preserves the current entry and replaces only entries after it. Duplicate tracks remain distinct entries. The limit is 1,000 upcoming tracks. Empty input clears upcoming entries, so a provider must reject incomplete server snapshots before calling.

`host.locale()` returns the system language tag, country and time zone. Use these values rather than hardcoded account-market defaults.

## Canvas and artist details

Register `artwork.canvas/v1` to receive `{track}` and return `{url}` when matching Canvas is available. The host calls the selected service only for its enabled, logged-in owner and discards results after account or owner changes. It routes the result into its existing Canvas renderer. Return an absent URL when no matching artwork exists.

Register `catalog.artist-metadata/v1` to receive `{id}` and return artist details directly or inside `metadata`. The host selects the service belonging to the catalog owner. Supported fields are `biography`, `monthlyListeners`, `featuring` as `CatalogAlbum` entries, `relatedArtists` as `CatalogArtist` entries, and `playlists` as `CatalogPlaylist` entries. `concerts` and `merch` entries supply a title or name and URL or URI, plus optional city, venue, startDateIso or price. The host validates external HTTPS links and bounds list and text sizes. Omit unavailable fields.

## Native dialogs and Android packaging

Use the SDK's `PluginAlertDialog` for account dialogs compiled against the desktop SDK and packaged for Android. Its expect/actual implementations call each platform's Compose dialog API. A desktop-only Compose call can otherwise leave a `_skikoKt` reference in Android DEX.

Keep API, SDK, Compose and their resources compile-only. Reject bundled host classes and desktop Skiko references in Android package checks. The patched host retains `org.jetbrains.compose.resources`, including `StringResourcesKt`, in minified releases and loads those classes from the parent host.
