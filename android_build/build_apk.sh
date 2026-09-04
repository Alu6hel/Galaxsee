#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$DIR")"
SDK_JAR="${ANDROID_HOME:-$HOME/Android/Sdk}/platforms/android-36/android.jar"
BUILD_TOOLS_DIR="${ANDROID_HOME:-$HOME/Android/Sdk}/build-tools/36.1.0"

cd "$DIR"
rm -rf gen bin compiled_res.zip *.apk
mkdir -p gen bin/classes

# Sync web assets
cp -r "$ROOT_DIR/web_app_dist"/* "$DIR/assets/"

echo "[1/6] Compiling resources with AAPT2..."
"$BUILD_TOOLS_DIR/aapt2" compile --dir res -o compiled_res.zip

echo "[2/6] Linking APK with AAPT2..."
"$BUILD_TOOLS_DIR/aapt2" link -I "$SDK_JAR" \
    --manifest AndroidManifest.xml \
    -A assets \
    compiled_res.zip \
    --java gen \
    --auto-add-overlay \
    -o base_unaligned.apk

echo "[3/6] Compiling Java source..."
javac -source 11 -target 11 -cp "$SDK_JAR" \
    -d bin/classes \
    gen/com/galaxsee/app/R.java \
    src/com/galaxsee/app/MainActivity.java

echo "[4/6] Generating classes.dex..."
"$BUILD_TOOLS_DIR/d8" bin/classes/com/galaxsee/app/*.class \
    --lib "$SDK_JAR" \
    --output bin/

cd bin && zip -u ../base_unaligned.apk classes.dex && cd ..

echo "[5/6] Zipalign..."
"$BUILD_TOOLS_DIR/zipalign" -p 4 base_unaligned.apk galaxsee_pro_aligned.apk

echo "[6/6] Signing APK..."
if [ ! -f debug.keystore ]; then
    keytool -genkey -v -keystore debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
fi

"$BUILD_TOOLS_DIR/apksigner" sign --ks debug.keystore --ks-pass pass:android --out "$ROOT_DIR/galaxsee_pro.apk" galaxsee_pro_aligned.apk

echo "SUCCESS! Production APK generated at: $ROOT_DIR/galaxsee_pro.apk"
