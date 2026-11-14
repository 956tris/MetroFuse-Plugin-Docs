# Plugin Home and login capabilities

These are optional capabilities of API 1.1.0. Existing plugins keep the same entrypoint and loader contracts. Offline is built into the host and never registers as a plugin.

## Login

Add `"login"` to the manifest's existing `capabilities` array. The account button appears only for the selected enabled plugin with this capability. JioSaavn does not declare login, so it has no account button.

Native JAR and APK entrypoints can additionally implement `dev.metrofuse.api.LoginPlugin`. This separate interface leaves previously compiled `NativePlugin` implementations compatible. It has safe signed-out defaults, `loginState: StateFlow<PluginLoginState>`, `isLoggedIn()`, `loginRequest()`, `login(LoginCredentials)` and `logout()`.

Return a `LoginRequest` with one to eight fields and optional instructions. The host renders the form and masks secret fields. Return `PluginLoginState(loggedIn = true, accountName = ...)` only after authenticating the supplied values. Update the state flow when the account changes or expires. `logout()` should release the plugin's in-memory session.

JavaScript plugins register the same conceptual callbacks during initialization:

```javascript
host.login({
  request: async () => ({
    fields: [{id: 'token', label: 'Access token', secret: true}],
    instructions: 'Enter the token issued for your account.'
  }),
  login: async credentials => {
    const account = await authenticate(credentials.values.token);
    const state = {loggedIn: true, accountName: account.name};
    host.loginState(state);
    return state;
  },
  logout: async () => {
    await releaseSession();
    host.loginState({loggedIn: false});
  }
});
```

`authenticate` and `releaseSession` are the plugin's service-specific functions. Login UI belongs to the host; this contract supplies a form rather than an embedded browser. It does not implement a service's OAuth flow or reuse the old YouTube account session.

The host stores successful credentials by plugin ID and restores them through that plugin's bound callback on activation. There is no credential lookup by arbitrary plugin ID in either plugin API. Credentials do not enter ordinary settings or host error logs. Android excludes these files from app backups; Windows ciphertext files may be backed up. `LoginCredentials.toString()` redacts values, and login failures expose host error codes rather than exception text.

Windows uses user-bound DPAPI with plugin-specific entropy. Android uses a separate Android Keystore AES-GCM key per plugin, with credentials under the app's no-backup directory. Only ciphertext reaches disk. Other desktop platforms currently reject credential persistence rather than using plaintext storage. Native plugins remain trusted in-process code; host API scoping does not sandbox arbitrary native filesystem or OS calls.

Callbacks run in activation-owned scopes with deadlines. QuickJS retains its execution interrupt and wall deadline. Disabling or unloading a plugin cancels its login operations and removes its account state and form. Plugins must keep credentials in memory or let the host restore them; they must not copy credentials into ordinary storage or logs.

## Home

Add `"home"` to `capabilities`. Optional manifest metadata is:

```json
{
  "home": {
    "title": "My music",
    "icon": "assets/home.png"
  }
}
```

The title defaults to the plugin name. The icon defaults to the manifest icon or the host's extension icon. Only installed, enabled plugins declaring Home appear after the built-in Offline row. Search and catalog registrations alone do not create a Home source.

Native JAR and APK entrypoints can additionally implement `HomePlugin.getHome(HomeRequest): List<HomeShelf>`. The safe default returns an empty list. JavaScript registers `host.home(async request => shelves)` during initialization:

```javascript
host.home(async request => [{
  title: 'Featured',
  layout: 'CARDS',
  items: [{track: {id: 'one', title: 'Track one', artist: 'Artist', album: ''}}]
}]);
```

Each item contains exactly one `track`, `album`, `artist`, or `playlist`, using the existing catalog models. `CARDS` is a horizontal artwork shelf; `ROWS_GRID` uses compact rows in four-row columns. Host rendering uses the same shelf components on desktop and Android. Explicit layouts take precedence over title-based Home heuristics. The host namespaces every identifier and preserves original track IDs for playback and catalog navigation.

`HomeRequest.language` and `country` come from content settings or the system locale. A source keeps its latest successful page while refreshing or after an error. Retry requests a new page. Requests have a 15-second deadline in addition to QuickJS's active evaluation interrupt. Each source owns its request, cache and cancellation scope, so one source cannot hold up another or Offline.

The saved Home selection is `offline` or `plugin:<id>`; legacy raw owner values migrate after plugin restoration. Disabling, uninstalling or quarantining the selected source silently persists Offline. No Home providers means no dropdown arrow. Offline is always the first menu row, with no leading hamburger; plugin rows have icons, active checkmarks and truncated long names in a bounded scrollable menu anchored below the header. On desktop the menu's horizontal offset follows the measured content pane so it clears the navigation rail, including while the rail expands.

[JioSaavn's separate native and JavaScript implementations](https://github.com/956tris/MetroFuse-JioSaavn) declare Home and parse the launch API's module titles and mixed catalog shelves. They retain their existing search, catalog and audio providers.

## Lifecycle limits and manual checks

JAR unload closes its classloader and releases owned operations. APK unload releases the loader, resource and private artifact references; Android ART does not provide forced class unloading. QuickJS contexts are disposed. Native plugins run trusted code in the host process: deadlines cancel suspended work and stop accepting stale results, but cannot safely terminate arbitrary blocking native code or bypass OS filesystem permissions.

On Windows and Android, check install, enable, disable, reload and uninstall while that plugin is selected; the Home and account UI should update without restarting. Restart with a saved available source, then with it removed. Check long names, many entries, icons, keyboard/touch selection and popup position at narrow and wide widths.

Use two login fixtures to check that logging into one leaves the other signed out, credentials restore only to their owner, and logout removes the saved credential. Check Android process recreation and Keystore persistence on a device. Exercise expired sessions and a plugin that throws or loops during login and Home loading; the host should stay usable, cached shelves should remain visible with Retry, and switching to Offline should respond immediately.
