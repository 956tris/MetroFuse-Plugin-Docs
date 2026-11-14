# Packaging, installation and lifecycle

## Archive contents

| Format | Required contents | Install on |
| --- | --- | --- |
| MFP | Root manifest.json, JavaScript entrypoint, relative modules/assets | Desktop and Android |
| JAR | Root manifest.json, entrypoint class and plugin-private JVM classes/assets | Desktop |
| APK | assets/metrofuse/manifest.json, classes.dex or multidex, Android resources, optional native libraries | Android host |

MFP is a ZIP archive with a distinct extension. It cannot wrap a native JAR or APK. The included packer writes normalized paths, SHA-256 payload hashes and fixed timestamps:

```powershell
.\tooling\pack-mfp.ps1 -Source .\plugins\javascript\settings -Output .\build\plugin-examples\settings.mfp
Get-FileHash -Algorithm SHA256 -LiteralPath .\build\plugin-examples\settings.mfp
```

The [native guide](native-plugin-development.md) supplies Gradle tasks for actual JAR/DEX/resource packaging. Do not rename a ZIP of Kotlin source to a JAR, or rename a JAR to an APK. Android needs real DEX code. Keep host-provided classes out of both artifacts.

## Import and enable

Open Plugins or Settings → Plugins in the host. Import the file for your platform, inspect its metadata, then enable it. Installation begins disabled. Importing requires no registry or network connection.

The host validates API/ABI, paths, sizes, integrity and dependencies. It keeps native artifacts intact in private installation storage. Activation stages registrations and exposes them together after `init` or `start` succeeds. Failures clear staged registrations and record a FAILED state.

Home appears only after an enabled plugin declares `home` and supplies Home callbacks. The account button is tied to the selected source's `login` capability. Audio, search and catalog need their own registered providers. All variants with the same ID represent one installed plugin; import one implementation at a time.

## Update, reload and remove

Use the same stable plugin ID, increase the version, package the new implementation and import it. The host stages and validates updates before replacing active code. It preserves a backup and attempts rollback if activation fails. Arbitrary native side effects cannot be rolled back.

Disable/reload cancels owned operations and event subscriptions, removes providers and UI, then releases the runtime. Your plugin must honor coroutine cancellation and clean up resources in `stop()` or `dispose()`. Do not keep global jobs or stale host contexts. Failed initialization removes enabled state rather than repeatedly running failed code on restart.

Settings and ordinary plugin data survive disable and application restarts. Uninstall currently retains the data namespace for reinstall. Successful login credentials use a separate encrypted host store on Windows and Android. Logout clears saved credentials. Disabling clears active account UI and cancels pending work; it does not mean the user has logged out of the service.

JVM activation uses private JAR copies so Windows can replace installed files. APK activation uses read-only private copies and DexClassLoader. Android native libraries require restarting the host before replacement. Closing a loader does not guarantee JVM/ART class unloading. Document additional restart requirements if you load JNI yourself.

## Release

Publish the exact tested bytes with a version and SHA-256 checksum. Keep source, GPL and dependency notices available. Test the downloaded artifact rather than only your loose source folder. Use the [marketplace guide](plugin-marketplace.md) for a static HTTPS registry, platform download fields and review requirements.
