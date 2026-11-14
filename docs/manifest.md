# Manifest and compatibility

Every package needs a JSON manifest. The API value must be explicit and exactly `1.1.0`. Native plugins additionally use `composeAbi: "kotlin-2.4.21_compose-1.13.0-beta02_api-1.1.0"`.

Use [the quickstart manifest](quickstart.md#create-your-own-javascript-plugin) as a working JavaScript example. JARs put `manifest.json` at the root. APKs put it at `assets/metrofuse/manifest.json`. MFPs put it at the root with their JavaScript entrypoint.

| Field | Author requirement |
| --- | --- |
| id | Stable, unique lowercase ASCII identifier, such as `example.catalog`. Use the same ID when updating. |
| name, author | Human-readable plugin name and actual author credit. |
| version | Stable `major.minor.patch`; increase it for distributed updates. |
| api | Explicit exact supported API version. |
| runtime | `javascript` for MFP; `kotlin` for JAR/APK. |
| platforms | Supported host names, `desktop` and/or `android`. |
| script | Packaged JavaScript entry module, only for MFP. |
| entryClass | Public no-argument NativePlugin entrypoint, only for JAR/APK. |
| composeAbi | Exact host ABI tag for native plugins. |
| capabilities | Advertised functionality. Include `home` or `login` for corresponding host integration. |
| home | Optional `{title, icon}` for the Home source. Icons must be packaged safe asset paths. |
| icon, description | Optional packaged icon and description. |
| dependencies | Required plugin ID to minimum stable version, for example `{"example.base": ">=1.2.0"}`. |
| minimumHostVersion | Optional required stable host version; unavailable/incompatible host versions are rejected. |
| settings | Manifest-defined settings the host may expose and persist. |
| integrity | Payload path to SHA-256 mapping. The MFP packer generates it. |

Dependency cycles, missing dependencies and insufficient versions fail activation. Dependencies order lifecycle and service access; they do not merge native classpaths or download packages automatically.

Paths must remain inside the archive and use `/`. Include only required modules, assets and notices. Never package local settings, build caches, credentials or another native artifact inside an MFP.

## Settings

```json
{
  "settings": [
    {"key": "enabled", "title": "Enable provider", "type": "BOOLEAN", "default": true},
    {"key": "quality", "title": "Preferred quality", "type": "ENUM", "default": "auto", "options": ["auto", "high"]},
    {"key": "limit", "title": "Result limit", "type": "NUMBER", "default": 20, "minimum": 1, "maximum": 100}
  ]
}
```

This fragment belongs inside a complete manifest. STRING and OBJECT are also supported. The host validates definitions and values; unknown keys and incorrect types fail. Do not put secrets in settings or ordinary JSON storage. Use the owner-scoped host login contract for credentials.

See [API reference](plugin-api.md) for exact types and [source contracts](../reference/api/Settings.kt) for serialized settings definitions.
