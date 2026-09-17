# 📖 Galaxsee Standard — User Manual, Feature Guide & Developer Operations Guide

---

## 1. Overview & Architecture

**Galaxsee Standard** is a lightweight, local-first photo and video gallery engineered for 120Hz/60Hz touch gesture responsiveness, smooth pinch-to-zoom grid scaling, fast photo indexing, and private media storage.

### Core Principles:
- **100% Local-First & Private**: Zero external telemetry, zero tracking scripts, and zero cloud lock-in.
- **Fluid Touch Physics**: 120Hz smooth pan, pinch-to-grid scaling (1 to 14 columns), and momentum scrolling.
- **Zero-Dependency Android Runtime**: Native Android integration powered by standard Android SDK components and pure Java bridges.

---

## 2. Feature Matrix: Standard vs. Pro

| Feature Area | Galaxsee Standard | Galaxsee Pro Studio |
|---|---|---|
| **120Hz Gesture Physics & Pinch-to-Grid** | ✅ Included | ✅ Included |
| **Deep-Zoom Pyramidal Inspector** | ✅ Included | ✅ Included |
| **Encrypted Private Vault (AES-256)** | ✅ Included | ✅ Included |
| **Universal In-App Updater (GitHub Releases)** | ✅ Included | ✅ Included |
| **Direct Device File Saving (`/sdcard/Download/`)** | ✅ Included | ✅ Included |
| **Cull Studio (Eye Focus, Star Ratings, XMP Sidecar)** | ❌ Pro Exclusive | ✅ Included |
| **Algorithmic SVG Vector Converter Studio** | ❌ Pro Exclusive | ✅ Included |
| **8-Channel HSL Color Mixer Wheels & Tone Curves** | ❌ Pro Exclusive | ✅ Included |
| **Multi-Photo Compare Studio (Side-by-Side)** | ❌ Pro Exclusive | ✅ Included |
| **Lossless Audio Workstation & Spectrum Analyzer** | ❌ Pro Exclusive | ✅ Included |

---

## 3. Universal In-App Update System

Galaxsee Standard features an integrated, zero-dependency in-app update engine connecting directly to official releases.

### Checking for Updates:
1. Open Galaxsee and tap the **Settings** icon (gear in the sidebar or top bar).
2. Scroll to the **Application Updates & Version** card.
3. Tap **"Check for Updates"**.
4. If a newer build is available:
   - The **Update Modal** opens displaying the new release version and release notes.
   - Exact download package size (in MB) is verified.
5. Tap **"Download & Install Update"**:
   - The app downloads the `.apk` package while displaying a real-time progress bar.
   - The Android `PackageInstaller` is invoked via `GalaxseeFileProvider` to seamlessly update the application without data loss.

---

## 4. Developer Blueprint: How to Update Created Apps (Now & Future)

> [!IMPORTANT]
> This section provides the complete operational playbook for developers updating existing apps and designing updates for future applications.

### 🛠️ Strategy 1: Active Production Workflow (GitHub Releases Direct APK)

This is the fully implemented update system currently running in **Galaxsee Standard**.

#### Step 1: Bump Application Version
1. Open `android_build/AndroidManifest.xml`:
   ```xml
   <manifest xmlns:android="http://schemas.android.com/apk/res/android"
       package="com.galaxsee.app"
       android:versionCode="2"
       android:versionName="1.1.0">
   ```
2. Open `android_build/src/com/galaxsee/app/MainActivity.java`:
   - Verify the fallback current version matches `"1.1.0"`.
3. In `web_app_dist/assets/index-*.js`, update the version badge string:
   - Change `"v1.0.0"` to `"v1.1.0"`.

#### Step 2: Compile & Sign the Release APK
Run the zero-dependency build script from the repository root:
```bash
cd /home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build
./build_apk.sh
```
*The script compiles Java sources with `javac`, converts bytecode with `d8`, aligns with `zipalign`, and cryptographically signs with `apksigner`.*

#### Step 3: Publish the GitHub Release
Tag the git commit and publish the APK asset using the GitHub CLI (`gh`) or GitHub web interface:

```bash
cd /home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard
git tag v1.1.0
git push origin v1.1.0

gh release create v1.1.0 galaxsee.apk \
  --title "Galaxsee v1.1.0 — Performance & Stability Update" \
  --notes "### What's New in v1.1.0:
- Enhanced 120Hz gesture smoothness
- Improved media scanner indexing speed
- Integrated Universal In-App Update Engine
- Bug fixes and stability improvements"
```

#### Step 4: User Experience
1. Existing users tap **"Check for Updates"** in Galaxsee Settings.
2. The app queries `https://api.github.com/repos/Alu6hel/Galaxsee/releases/latest`.
3. The app detects `v1.1.0` > `v1.0.0`, displays the release notes and package size.
4. User taps **"Download & Install Update"**. The APK downloads and prompts installation directly on screen.

---

### ⚡ Strategy 2: Over-The-Air (OTA) Instant Web Bundle Updates (Future Apps)

For future apps built on a WebView / Hybrid architecture:
1. **Dynamic Asset Directory**: Store and serve HTML/JS assets from `context.getFilesDir() / "www"` rather than static `file:///android_asset/`.
2. **Background Sync**: On launch, fetch a lightweight JSON manifest (`https://yourserver.com/manifest.json`).
3. **Hot Unpack**: Download and unzip new web bundles in the background. On next launch, load the new bundle instantly without requiring users to reinstall an APK.

---

### 🏪 Strategy 3: Google Play Store & Android App Bundles (AAB)

When distributing through the Google Play Store:
1. **Build an Android App Bundle (.aab)** using `aapt2` and `bundletool`.
2. **Sign with Keystore**: Sign with your private release key using `jarsigner`.
3. **Google Play In-App Updates API**: Integrate `com.google.android.play:app-update` for automated flexible background updates or immediate blocking update dialogs.

---

### 🌐 Strategy 4: Self-Hosted Update Server (Custom REST API)

For enterprise or custom deployments:
- Host a lightweight endpoint (`https://api.yourdomain.com/v1/update`) returning JSON with `versionName`, `downloadUrl`, `size`, and `changelog`.
- Point `MainActivity.java` `apiUrl` to your custom endpoint. The built-in downloader and `GalaxseeFileProvider` handle installation seamlessly.

---

*Authored by the Alumungandr Engineering Team for Galaxsee Standard.*
