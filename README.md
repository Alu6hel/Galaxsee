# 🌌 Galaxsee — Next-Gen Multi-Touch Photo & Media Gallery

[![Platform: Android | Web](https://img.shields.io/badge/Platform-Android%20%7C%20Web-blue.svg?style=for-the-badge)](#-multi-platform-distribution)
[![Architecture: Local--First & Private](https://img.shields.io/badge/Privacy-100%25%20Local--First-emerald.svg?style=for-the-badge)](#-private-vault--security)
[![Display: 120Hz ProMotion Ready](https://img.shields.io/badge/Performance-120Hz%20Smooth-violet.svg?style=for-the-badge)](#-core-features)

**Galaxsee** is an ultra-fast, local-first photo, video, and audio gallery engineered for 120Hz/60Hz multi-touch gesture responsiveness, smooth deep-zoom rendering, non-destructive editing, encrypted privacy vault, native Android MediaStore integration, and recursive folder imports.

Built and optimized for **Android Mobile (`.apk`)** and **Modern Web / Offline PWA**.

---

## ✨ Core Features

### ⚡ Fluid 120Hz Multi-Touch Physics
- **Pinch-to-Grid Dynamic Scaling**: Continuous, buttery-smooth transition from single-photo detail view up to a multi-column contact sheet using touch gestures.
- **Inertial Momentum Scrolling**: Native momentum scrolling with edge overscroll bounce for rapid navigation across thousands of items.
- **Marquee Multi-Select**: Click-and-drag rubberband bounding box to select and batch-process photos.

### 🔬 Sub-Pixel Smooth Deep-Zoom Engine
- **Touch / Pinch-to-Zoom**: Smooth, continuous zoom and pan with seamless 2-to-1 finger anchor transitions and zero edge snap-back.
- **Instant Pan & Inspect**: Instantaneous response on high-resolution image inspection.

### 📱 Android Native Integration
- **Direct MediaStore Scanning**: Automatically queries Android MediaStore on startup and synchronizes local DCIM, Pictures, and Downloads folders.
- **Storage Access Framework (SAF)**: Native recursive directory picker (`ACTION_OPEN_DOCUMENT_TREE`) supporting deep nested folder ingestion up to 4 levels.
- **Tab History & Hardware Back Button**: Intuitive per-tab back stack navigation.

### 🔒 Zero-Knowledge Encrypted Private Vault
- **AES-256 Encryption**: Protect sensitive photos behind biometric authentication or custom PIN.
- **Zero Cloud Leak**: 100% local processing; no telemetry, tracking, or cloud upload.

---

## 📦 Distribution Packages

| Package File | Target Platform | Description |
|---|---|---|
| **`galaxsee.apk`** | Android 8.0+ / ChromeOS | Native Android package with touch-optimized controls and Android MediaProvider integration. |
| **`web_app_dist/`** | Web / PWA / Chromebook | Offline-first Progressive Web App deployable to any web host, local server, or ChromeOS container. |

---

## 📄 License & Attribution

Copyright © 2026 Alu / Alumungandr. All rights reserved.
Open-source third-party dependencies are acknowledged under their respective permissive licenses (MIT, ISC, BSD-2-Clause).
