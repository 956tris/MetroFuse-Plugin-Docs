# Plugin-owned browser sign-in

Plugins own their account screens, service URLs, navigation rules, login labels and account verification. The reusable browser belongs to MetroFuse's `plugin-sdk` module. The application hosts the contributed screen and provides activation-scoped callbacks for credential storage and login/logout. Its profile menu and Settings stay available for every source.

The separate [YouTube Music reference plugin](https://github.com/956tris/MetroFuse-YouTube-Music) demonstrates native and JavaScript implementations. Use a KMP host containing `NativeLoginUi` and `plugin-sdk`. Existing `LoginPlugin`, `LoginRequest`, `WebLoginPlugin` and the legacy `web` callback remain compatible.

## Native plugins

Implement both `LoginPlugin` and `NativeLoginUi`. Build your account screen in the plugin, using the SDK's `WebViewLoginScreen`. Load labels from your plugin's resources. The browser request and account verification also belong to your plugin.

```kotlin
import androidx.compose.runtime.Composable
import dev.metrofuse.api.LoginUiContext
import dev.metrofuse.api.NativeLoginUi
import dev.metrofuse.sdk.WebViewLoginScreen
import dev.metrofuse.sdk.WebViewLoginUi

// Initialize during NativePlugin.start from plugin-owned navigation rules and resources.
private lateinit var accountScreen: WebViewLoginScreen

private fun configureAccountUi(ui: WebViewLoginUi) {
    accountScreen = WebViewLoginScreen(ui)
}

@Composable
override fun Content(context: LoginUiContext) {
    accountScreen.Content(context)
}
```

`LoginUiContext` exposes account status, loading/error status, request readiness and callbacks to request login, submit credentials, log out and dismiss. The SDK screen handles browser sign-in, retries, account display and logout. Native plugins can implement their own Compose screen using the same callbacks.

Keep `loginRequest()` as the credential contract. For browser capture it contains exactly one field whose ID equals `cookieField`; users do not type that field. `login()` must verify the candidate with your service before returning a signed-in account.

Export both SDK and API JARs from the matching host:

```powershell
./gradlew.bat :plugin-api:desktopJar :plugin-sdk:desktopJar --no-configuration-cache
```

Windows SDK packaging requires .NET SDK 10 and restores its pinned WebView2 package. Set `-PdotnetExecutable=<path>` when .NET is outside PATH. In your separate plugin repository, use `metrofuseApiJar` and `metrofuseSdkJar` as compile-only dependencies and enable the matching Compose compiler plugin. Add SDK and Compose dependencies to your test runtime. Include SDK/API JARs on D8's classpath, without bundling their classes into the APK. The importer rejects duplicate SDK, API or Compose definitions.

See [native development](native-plugin-development.md), [API account UI](../reference/api/LoginUi.kt), [SDK screen](../reference/sdk/WebView.kt) and the [complete native reference](https://github.com/956tris/MetroFuse-YouTube-Music/tree/main/native).

## JavaScript plugins

Return the SDK's serializable screen definition from `host.login`'s optional `ui` callback. Your plugin owns the entire definition:

```javascript
host.login({
  request: async () => ({fields: [{id: 'session', label: 'Provider session', secret: true}]}),
  ui: async () => ({
    request: {
      url: 'https://accounts.example.com/login',
      cookieUrl: 'https://music.example.com', cookieField: 'session',
      requiredCookies: ['AUTH'],
      allowedHosts: ['accounts.example.com', 'music.example.com']
    },
    labels: {
      title: 'Provider sign-in', hint: 'Sign in in the browser window.',
      error: 'Could not sign in.', retry: 'Try again', cancel: 'Cancel',
      login: 'Sign in', logout: 'Sign out'
    }
  }),
  login: async credentials => verifyAccount(credentials.values.session),
  logout: async () => clearSession()
});
```

The application decodes this SDK screen definition and supplies its generic lifecycle context. MFP plugins contain no platform executable payload. `verifyAccount` and `clearSession` are provider functions. Publish account changes through `host.loginState`. See the complete [JavaScript reference](https://github.com/956tris/MetroFuse-YouTube-Music/tree/main/universal).

## Capture and lifecycle

| Request field | SDK behavior |
| --- | --- |
| `url` | Opens this HTTPS URL for sign-in. |
| `cookieUrl` | Reads cookies for this HTTPS origin after navigation returns there. |
| `cookieField` | Places the captured header in this credential field. |
| `requiredCookies` | Waits until at least one named cookie has a nonempty value. |
| `allowedHosts` | Allows exact navigation hosts, without schemes or wildcards. |

The SDK rejects credential-bearing URLs, non-HTTPS schemes, unexpected ports and undeclared hosts. The credential field must match the plugin's login contract. Cookie presence signals a candidate session; the provider must verify its actual service account.

The SDK's Windows helper uses a private WebView2 profile, cleaned after exit or cancellation. Android embeds a WebView, uses the process cookie store and blocks screenshots during sign-in. Linux probes WebKitGTK before composing the browser; macOS uses its platform WebView. Missing browser support produces the plugin-supplied error text.

The host delivers credentials only to the matching plugin activation. A callback from a closed or replaced activation cannot submit to its replacement. Accepted sessions use Windows DPAPI or Android Keystore encryption. Linux and macOS persistence is currently unavailable. Credentials stay outside plugin settings and logs. Login/logout invalidate cached audio and metadata and refresh an already loaded Home page.

## Verification

Check SDK/API class separation, import and enable/disable, contributed account UI in native and MFP variants, guest cookies, malformed origins, stale activation callbacks, failed account replacement, logout and Home refresh. Actual service sign-in and device audio need manual verification separately from backend fixtures. Never include real account cookies in tests or releases.
