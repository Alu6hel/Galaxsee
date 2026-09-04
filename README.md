# 🌌 Galaxsee Pro — Next-Gen Multi-Touch Photo & Media Studio

[![Platform: Windows | Android | Web](https://img.shields.io/badge/Platform-Windows%20%7C%20Android%20%7C%20Web-blue.svg?style=for-the-badge)](#-multi-platform-distribution)
[![Architecture: Local--First & Private](https://img.shields.io/badge/Privacy-100%25%20Local--First-emerald.svg?style=for-the-badge)](#-private-vault--security)
[![Display: 120Hz ProMotion Ready](https://img.shields.io/badge/Performance-120Hz%20Smooth-violet.svg?style=for-the-badge)](#-core-features)
[![License: Alumungandr Master License](https://img.shields.io/badge/License-Alumungandr%20Commercial-amber.svg?style=for-the-badge)](./ALUMUNGANDR_MASTER_LICENSE.md)

**Galaxsee Pro** is an ultra-fast, local-first photo, video, and audio gallery engineered for 120Hz/60Hz multi-touch gesture responsiveness, deep-zoom pyramidal rendering, on-device AI semantic search, non-destructive editing studio, encrypted privacy vault, and cross-platform multi-device synchronization.

Built and optimized for **Windows Desktop (`.exe`)**, **Android Mobile (`.apk`)**, and **Modern Web / Offline PWA**.

---

## ✨ Core Features & Pro Highlights

### ⚡ Fluid 120Hz Multi-Touch Physics
- **Pinch-to-Grid Dynamic Scaling**: Continuous, buttery-smooth transition from single-photo detail view up to a 14-column compact contact sheet using touch gestures or keys `1`–`6`.
- **Inertial Momentum Scrolling**: Native momentum scrolling with edge overscroll bounce for rapid navigation across thousands of items.
- **Marquee Multi-Select**: Click-and-drag rubberband bounding box to select and batch-process hundreds of photos instantly.

### 🔬 Deep-Zoom Pyramidal Engine
- **Sub-Pixel Smooth Zoom**: Zoom up to 3200% into high-resolution images with real-time bicubic interpolation.
- **Instant Pan & Inspect**: Instantaneous response on gigapixel pan and inspection with zero stutter or memory bloat.

### 🎨 Pro Non-Destructive Editing Studio (Key: `E`)
- **Tone & Exposure**: Exposure compensation, contrast, highlights, shadows, whites, blacks, and clarity adjustments.
- **Color Mastery**: Temperature, tint, vibrance, saturation, and 8-channel dedicated HSL color mixer wheels.
- **Tone Curve**: Parametric and point curve control across RGB, Red, Green, and Blue channels.
- **Format Converter & Resizer**: Export to WebP, AVIF, JPEG, PNG with custom compression ratios and dimensions.

### 🔍 Multi-Photo Compare & Burst Culling
- **Side-by-Side Comparison**: Select 2 to 4 photos to inspect compositions simultaneously with synchronized locked zoom and pan.
- **Burst Culling**: Rapid star-rating, flagging, and automated duplicate/similar shot grouping.

### 🔒 Zero-Knowledge Encrypted Private Vault
- **AES-256 Encryption**: Protect sensitive photos behind biometric authentication or custom PIN.
- **Zero Cloud Leak**: 100% local processing; no telemetry, tracking, or cloud upload.

### 🎧 Lossless Audio & Media Studio
- **Audio Workstation**: High-fidelity spectrum analyzer, waveform preview, and metadata tag editor for FLAC, WAV, and MP3 audio tracks.

---

## 📦 Multi-Platform Distribution

| Package File | Target Platform | Description |
|---|---|---|
| **`Galaxsee Pro Photo Gallery Setup 1.0.0.exe`** | Windows 10 / 11 | Full desktop installer with auto-updater, file associations, and start menu shortcuts. |
| **`Galaxsee Pro Photo Gallery 1.0.0.exe`** | Windows (Portable) | Standalone portable executable. Run directly from a USB drive or folder without installation. |
| **`galaxsee_pro.apk`** | Android 8.0+ / ChromeOS | Native Android package with touch-optimized controls and Android MediaProvider integration. |
| **`web_app_dist/`** | Web / PWA / Chromebook | Offline-first Progressive Web App deployable to any web host, local server, or ChromeOS container. |

---

## 🚀 Quick Start & Installation

### 🪟 Windows Desktop
1. **Installer**: Double-click `Galaxsee Pro Photo Gallery Setup 1.0.0.exe` and follow the guided setup.
2. **Portable**: Double-click `Galaxsee Pro Photo Gallery 1.0.0.exe` to launch immediately.

### 📱 Android Devices
1. Transfer `galaxsee_pro.apk` to your Android smartphone or tablet.
2. Open your device file manager, tap `galaxsee_pro.apk`, and permit installation from your source.
3. Launch **Galaxsee Pro** and grant storage permissions to index your gallery.

### 💻 ChromeOS / Linux Chromebook Testing
Galaxsee Pro provides two distinct ways to run on Chromebooks:

#### Option 1: Android App on ChromeOS (via ARCVM / Play Store Subsystem)
- **Direct Sideloading (Recommended)**:
  1. Enable **Linux development environment (Crostini)** in ChromeOS Settings.
  2. Enable **Develop Android Apps** > **Enable ADB debugging** in ChromeOS Settings.
  3. Open the Linux terminal and install ADB:
     ```bash
     sudo apt update && sudo apt install -y adb
     ```
  4. Connect to ChromeOS Android subsystem and install:
     ```bash
     adb connect 100.115.92.2:5555
     adb install galaxsee_pro.apk
     ```
  5. The **Galaxsee Pro** icon will appear directly in your ChromeOS App Launcher!

#### Option 2: Running the Web App / PWA (`web_app_dist`)
- High-performance, zero-friction testing using ChromeOS's native Chromium browser:
  1. In your terminal inside `web_app_dist`:
     ```bash
     # Using Python 3
     python3 -m http.server 8080
     # Or using Node.js / npx
     npx serve .
     ```
  2. Navigate to `http://localhost:8080` in Chrome.
  3. Click the **Install** icon in the address bar to install Galaxsee Pro as a standalone native-feeling desktop app.

---

## ⌨️ Keyboard Shortcuts & Gestures

| Shortcut / Action | Function |
|---|---|
| `1` – `6` | Adjust grid density (1 = single hero view, 6 = dense 14-column view) |
| `Space` | Quick preview selected image in modal overlay |
| `Double Click` / `Enter` | Open image in full-resolution inspection view |
| `E` | Open Non-Destructive Edit Studio |
| `I` | Toggle EXIF Metadata Inspector (Camera, lens, exposure, histogram, GPS) |
| `C` | Open Multi-Photo Compare Studio (when 2–4 photos are selected) |
| `F` | Toggle Fullscreen Mode |
| `Esc` | Close modal / exit full view / clear selection |
| `Pinch-to-Zoom` | Smooth multi-touch zoom on touchscreen devices and trackpads |
| `Drag & Drop` | Import external folders and image files directly into the gallery |

---

## 📷 Supported Media Formats

- **Standard Raster**: JPEG, PNG, WebP, AVIF, GIF, BMP, TIFF, SVG, ICO
- **Camera RAW**: ARW (Sony), CR2 / CR3 (Canon), NEF (Nikon), DNG (Adobe / Leica), RAF (Fujifilm)
- **Mobile & HDR**: HEIC / HEIF, Ultra HDR Gain Maps, Apple Live Photos
- **Video & Audio**: MP4, MOV, WebM, MKV, FLAC, WAV, MP3, AAC, OGG

---

## 📜 Legal & Licensing

- **Master Intellectual Property & Commercial License**: See [ALUMUNGANDR_MASTER_LICENSE.md](./ALUMUNGANDR_MASTER_LICENSE.md). All proprietary rights, trademarks, and master commercial exploitation rights are reserved by **David Anthony Jones** ("Alu") / **Alumungandr™**.
- **Third-Party Open Source Attributions**: See [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) for full notices for React, Electron, Leaflet, Tailwind CSS, and other open-source dependencies.
- **User Guide**: See [USER_MANUAL_GUIDE.md](./USER_MANUAL_GUIDE.md) for complete operation workflows.

---

© 2026 **Alumungandr™** (David Anthony Jones). All Rights Reserved.
