package com.galaxsee.app;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.AssetFileDescriptor;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.util.Log;
import android.util.Size;
import android.view.View;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.TimeZone;
import java.util.concurrent.ConcurrentHashMap;

public class MainActivity extends Activity {
    private static final String TAG = "GalaxseePro";
    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST_CODE = 1001;
    private static final int PERMISSION_REQUEST_CODE = 1002;
    private static final int FOLDER_PICKER_REQUEST_CODE = 1003;
    public static final String MEDIA_HOST = "galaxsee.local";

    // In-memory thread-safe URI cache to prevent URL-encoding corruption for external files
    private static final Map<String, Uri> sDirectUriMap = new ConcurrentHashMap<>();
    private String openedPhotoJson = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Process incoming intent if opened as default viewer or shared
        handleIncomingIntent(getIntent());

        // Hardware acceleration & dark window background
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED
        );

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(0xFF070A12);

        webView = new WebView(this);
        webView.setBackgroundColor(0xFF070A12);
        webView.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);

        // Register Native JavaScript Bridge
        NativeBridge nativeBridge = new NativeBridge();
        webView.addJavascriptInterface(nativeBridge, "GalaxseeAndroid");
        webView.addJavascriptInterface(nativeBridge, "AndroidBridge");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                injectNativeBridge();
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                injectNativeBridge();
                if (hasStoragePermission()) {
                    syncDeviceMediaToWeb();
                }
                if (openedPhotoJson != null) {
                    try {
                        dispatchIncomingPhoto(new JSONObject(openedPhotoJson));
                    } catch (Exception ignored) {}
                }
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if (uri != null && MEDIA_HOST.equalsIgnoreCase(uri.getHost())) {
                    return handleMediaRequest(uri);
                }
                return super.shouldInterceptRequest(view, request);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url.startsWith("file:") || url.contains(MEDIA_HOST) || url.startsWith("http://localhost")) {
                    return false;
                }
                try {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                } catch (Exception e) {
                    return false;
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage cm) {
                Log.d("GalaxseeJS", cm.message() + " -- Line " + cm.lineNumber() + " (" + cm.sourceId() + ")");
                return true;
            }

            @Override
            public void onPermissionRequest(PermissionRequest request) {
                request.grant(request.getResources());
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                if (MainActivity.this.filePathCallback != null) {
                    MainActivity.this.filePathCallback.onReceiveValue(null);
                }
                MainActivity.this.filePathCallback = filePathCallback;

                Intent intent = fileChooserParams.createIntent();
                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE);
                } catch (Exception e) {
                    MainActivity.this.filePathCallback = null;
                    return false;
                }
                return true;
            }
        });

        root.addView(webView, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        ));

        setContentView(root);

        // Check permissions and load
        checkAndRequestPermissions();
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIncomingIntent(intent);
    }

    private void handleIncomingIntent(Intent intent) {
        if (intent == null) return;
        String action = intent.getAction();
        if (Intent.ACTION_VIEW.equals(action) || Intent.ACTION_SEND.equals(action) || Intent.ACTION_EDIT.equals(action)) {
            Uri dataUri = intent.getData();
            if (dataUri == null && Intent.ACTION_SEND.equals(action)) {
                dataUri = intent.getParcelableExtra(Intent.EXTRA_STREAM);
            }
            if (dataUri != null) {
                try {
                    int flags = intent.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                    if (flags != 0) {
                        try {
                            getContentResolver().takePersistableUriPermission(dataUri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        } catch (Exception ignored) {}
                    }
                    JSONObject photo = resolvePhotoFromUri(dataUri);
                    if (photo != null) {
                        openedPhotoJson = photo.toString();
                        Log.d(TAG, "Resolved incoming photo from intent: " + openedPhotoJson);
                        if (webView != null) {
                            runOnUiThread(() -> dispatchIncomingPhoto(photo));
                        }
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error resolving incoming intent uri: " + dataUri, e);
                }
            }
        }
    }

    private JSONObject resolvePhotoFromUri(Uri uri) {
        try {
            String name = null;
            long size = 0;
            String mime = null;
            int width = 0;
            int height = 0;

            if ("content".equalsIgnoreCase(uri.getScheme())) {
                try {
                    mime = getContentResolver().getType(uri);
                } catch (Exception ignored) {}

                try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
                    if (cursor != null && cursor.moveToFirst()) {
                        int nameIdx = cursor.getColumnIndex(MediaStore.MediaColumns.DISPLAY_NAME);
                        if (nameIdx == -1) nameIdx = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_DISPLAY_NAME);
                        if (nameIdx != -1) {
                            String n = cursor.getString(nameIdx);
                            if (n != null && !n.isEmpty()) name = n;
                        }

                        int sizeIdx = cursor.getColumnIndex(MediaStore.MediaColumns.SIZE);
                        if (sizeIdx == -1) sizeIdx = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_SIZE);
                        if (sizeIdx != -1) size = cursor.getLong(sizeIdx);

                        int mimeIdx = cursor.getColumnIndex(MediaStore.MediaColumns.MIME_TYPE);
                        if (mimeIdx == -1) mimeIdx = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_MIME_TYPE);
                        if (mimeIdx != -1) {
                            String m = cursor.getString(mimeIdx);
                            if (m != null && !m.isEmpty()) mime = m;
                        }

                        int wIdx = cursor.getColumnIndex(MediaStore.MediaColumns.WIDTH);
                        if (wIdx != -1) width = cursor.getInt(wIdx);
                        int hIdx = cursor.getColumnIndex(MediaStore.MediaColumns.HEIGHT);
                        if (hIdx != -1) height = cursor.getInt(hIdx);
                    }
                } catch (Exception ignored) {}
            } else if ("file".equalsIgnoreCase(uri.getScheme())) {
                String p = uri.getPath();
                if (p != null) {
                    File f = new File(p);
                    if (f.exists()) {
                        name = f.getName();
                        size = f.length();
                    }
                }
            }

            if (name == null || name.isEmpty()) {
                String lastSeg = uri.getLastPathSegment();
                if (lastSeg != null && !lastSeg.isEmpty()) {
                    name = lastSeg;
                } else {
                    name = "Photo_" + System.currentTimeMillis();
                }
            }

            // Accurate file size resolution via descriptor if cursor gave 0
            if (size <= 0) {
                try {
                    AssetFileDescriptor afd = getContentResolver().openAssetFileDescriptor(uri, "r");
                    if (afd != null) {
                        long len = afd.getLength();
                        afd.close();
                        if (len > 0) size = len;
                    }
                } catch (Exception ignored) {}
            }
            if (size <= 0) {
                try {
                    ParcelFileDescriptor pfd = getContentResolver().openFileDescriptor(uri, "r");
                    if (pfd != null) {
                        long len = pfd.getStatSize();
                        pfd.close();
                        if (len > 0) size = len;
                    }
                } catch (Exception ignored) {}
            }
            if (size <= 0 && "file".equalsIgnoreCase(uri.getScheme()) && uri.getPath() != null) {
                try {
                    File f = new File(uri.getPath());
                    if (f.exists()) size = f.length();
                } catch (Exception ignored) {}
            }

            // Fallback MIME detection from file extension
            String lowerName = name.toLowerCase();
            if (mime == null || mime.isEmpty() || "application/octet-stream".equals(mime)) {
                if (lowerName.endsWith(".png")) mime = "image/png";
                else if (lowerName.endsWith(".webp")) mime = "image/webp";
                else if (lowerName.endsWith(".avif")) mime = "image/avif";
                else if (lowerName.endsWith(".heic") || lowerName.endsWith(".heif")) mime = "image/heic";
                else if (lowerName.endsWith(".gif")) mime = "image/gif";
                else if (lowerName.endsWith(".bmp")) mime = "image/bmp";
                else if (lowerName.endsWith(".mp4") || lowerName.endsWith(".mkv") || lowerName.endsWith(".mov") || lowerName.endsWith(".webm")) mime = "video/mp4";
                else if (lowerName.endsWith(".dng") || lowerName.endsWith(".raw") || lowerName.endsWith(".cr2") || lowerName.endsWith(".cr3") || lowerName.endsWith(".arw") || lowerName.endsWith(".nef")) mime = "image/x-raw";
                else mime = "image/jpeg";
            }

            // Accurate image dimensions via BitmapFactory
            if (width <= 0 || height <= 0) {
                try (InputStream is = getContentResolver().openInputStream(uri)) {
                    if (is != null) {
                        BitmapFactory.Options options = new BitmapFactory.Options();
                        options.inJustDecodeBounds = true;
                        BitmapFactory.decodeStream(is, null, options);
                        if (options.outWidth > 0) width = options.outWidth;
                        if (options.outHeight > 0) height = options.outHeight;
                    }
                } catch (Exception ignored) {}
            }

            if (width <= 0) width = 1920;
            if (height <= 0) height = 1080;
            double aspect = (double) width / (double) height;

            SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US);
            isoFormat.setTimeZone(TimeZone.getTimeZone("UTC"));
            String dateIso = isoFormat.format(new Date());

            // Generate clean unique key in cache to prevent double-encoding URL corruption
            String uriKey = "intent_" + Math.abs(uri.toString().hashCode());
            sDirectUriMap.put(uriKey, uri);

            boolean isVideo = mime.startsWith("video/");
            boolean isRaw = lowerName.endsWith(".dng") || lowerName.endsWith(".raw") || lowerName.endsWith(".cr2") || lowerName.endsWith(".cr3") || lowerName.endsWith(".arw") || lowerName.endsWith(".nef");

            // Format friendly file size
            String sizeStr = "";
            if (size > 0) {
                if (size >= 1048576) {
                    sizeStr = String.format(Locale.US, " (%.1f MB)", (double) size / 1048576.0);
                } else {
                    sizeStr = String.format(Locale.US, " (%d KB)", size / 1024);
                }
            }

            JSONObject photo = new JSONObject();
            photo.put("id", "intent-opened-" + uriKey);
            photo.put("title", name.replaceFirst("[.][^.]+$", ""));
            photo.put("description", name + sizeStr);
            photo.put("url", "https://" + MEDIA_HOST + "/direct_uri/" + uriKey);
            photo.put("thumbnailUrl", "https://" + MEDIA_HOST + "/direct_uri/" + uriKey);
            photo.put("width", width);
            photo.put("height", height);
            photo.put("aspectRatio", aspect);
            photo.put("date", dateIso);
            photo.put("category", isVideo ? "Videos" : "Photos");
            photo.put("fileType", mime);
            photo.put("fileSize", size > 0 ? size : 2048000);
            photo.put("isFavorite", false);
            photo.put("isVault", false);
            photo.put("isHidden", false);
            photo.put("isRaw", isRaw);
            photo.put("isHdr", false);
            photo.put("isLivePhoto", false);
            photo.put("cloudSource", "local");
            photo.put("rating", 0);

            JSONObject exif = new JSONObject();
            exif.put("cameraMake", "Device");
            exif.put("cameraModel", "External File");
            exif.put("iso", 100);
            photo.put("exif", exif);

            JSONArray tags = new JSONArray();
            tags.put("device");
            tags.put("opened");
            photo.put("tags", tags);
            photo.put("people", new JSONArray());

            return photo;
        } catch (Exception e) {
            Log.e(TAG, "Failed to build photo JSON for URI: " + uri, e);
            return null;
        }
    }

    private void dispatchIncomingPhoto(JSONObject photo) {
        if (webView == null || photo == null) return;
        String escaped = JSONObject.quote(photo.toString());
        String js = "(function() {" +
            "  try {" +
            "    var p = JSON.parse(" + escaped + ");" +
            "    if (typeof window.__galaxsee_onExternalPhoto === 'function') {" +
            "      window.__galaxsee_onExternalPhoto(p);" +
            "    }" +
            "    window.dispatchEvent(new CustomEvent('galaxseeOpenExternalPhoto', { detail: { photo: p } }));" +
            "  } catch(e) {" +
            "    console.error('Error dispatching external photo:', e);" +
            "  }" +
            "})();";
        webView.evaluateJavascript(js, null);
    }

    private void injectNativeBridge() {
        String js = "(function() {" +
            "  if (window.__galaxsee_native_injected) return;" +
            "  window.__galaxsee_native_injected = true;" +
            "  window.electronAPI = {" +
            "    isElectron: true," +
            "    isAndroid: true," +
            "    scanDevicePhotos: async function() {" +
            "      try {" +
            "        var json = window.GalaxseeAndroid.getDevicePhotosJson();" +
            "        var photos = JSON.parse(json);" +
            "        return { photos: photos, total: photos.length };" +
            "      } catch (e) {" +
            "        console.error('Failed to scan device photos:', e);" +
            "        return { photos: [] };" +
            "      }" +
            "    }," +
            "    getInitialOpenedPhoto: function() {" +
            "      try {" +
            "        var json = window.GalaxseeAndroid.getInitialOpenedPhotoJson();" +
            "        return json ? JSON.parse(json) : null;" +
            "      } catch (e) { return null; }" +
            "    }," +
            "    openDefaultAppsSettings: function() {" +
            "      if (window.GalaxseeAndroid && typeof window.GalaxseeAndroid.setAsDefaultViewer === 'function') {" +
            "        window.GalaxseeAndroid.setAsDefaultViewer();" +
            "      }" +
            "    }," +
            "    setAsDefaultViewer: function() {" +
            "      if (window.GalaxseeAndroid && typeof window.GalaxseeAndroid.setAsDefaultViewer === 'function') {" +
            "        window.GalaxseeAndroid.setAsDefaultViewer();" +
            "      }" +
            "    }," +
            "    pickFiles: async function() {" +
            "      return { canceled: false, filePaths: [] };" +
            "    }," +
            "    openFolder: function() {" +
            "      if (window.GalaxseeAndroid && typeof window.GalaxseeAndroid.openFolderPicker === 'function') {" +
            "        window.GalaxseeAndroid.openFolderPicker();" +
            "      }" +
            "    }" +
            "  };" +
            "  console.log('Galaxsee Android Native Bridge Initialized');" +
            "})();";
        webView.evaluateJavascript(js, null);
    }

    private WebResourceResponse handleMediaRequest(Uri uri) {
        try {
            String path = uri.getPath();
            if (path == null) return null;

            if (path.startsWith("/direct_uri/")) {
                String key = path.substring("/direct_uri/".length());
                Uri targetUri = sDirectUriMap.get(key);
                if (targetUri == null) {
                    try {
                        targetUri = Uri.parse(Uri.decode(key));
                    } catch (Exception ignored) {}
                }
                if (targetUri != null) {
                    return openDocStream(targetUri);
                }
                return null;
            } else if (path.startsWith("/thumbnail/")) {
                String idStr = path.substring("/thumbnail/".length());
                if (idStr.startsWith("doc_")) {
                    String docKey = idStr.substring(4);
                    Uri docUri = sDirectUriMap.get(docKey);
                    if (docUri == null) {
                        try { docUri = Uri.parse(Uri.decode(docKey)); } catch (Exception ignored) {}
                    }
                    if (docUri != null) return openDocStream(docUri);
                    return null;
                }
                long id = Long.parseLong(idStr);
                Bitmap thumb = null;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    try {
                        Uri contentUri = ContentUris.withAppendedId(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, id);
                        thumb = getContentResolver().loadThumbnail(contentUri, new Size(512, 512), null);
                    } catch (Exception ignored) {}
                }
                if (thumb == null) {
                    thumb = MediaStore.Images.Thumbnails.getThumbnail(
                        getContentResolver(), id, MediaStore.Images.Thumbnails.MINI_KIND, null
                    );
                }
                if (thumb != null) {
                    ByteArrayOutputStream bos = new ByteArrayOutputStream();
                    thumb.compress(Bitmap.CompressFormat.JPEG, 85, bos);
                    byte[] data = bos.toByteArray();
                    Map<String, String> headers = new HashMap<>();
                    headers.put("Access-Control-Allow-Origin", "*");
                    headers.put("Cache-Control", "max-age=86400");
                    return new WebResourceResponse("image/jpeg", null, 200, "OK", headers, new ByteArrayInputStream(data));
                }
                return openImageStream(id);
            } else if (path.startsWith("/image/")) {
                String idStr = path.substring("/image/".length());
                if (idStr.startsWith("doc_")) {
                    String docKey = idStr.substring(4);
                    Uri docUri = sDirectUriMap.get(docKey);
                    if (docUri == null) {
                        try { docUri = Uri.parse(Uri.decode(docKey)); } catch (Exception ignored) {}
                    }
                    if (docUri != null) return openDocStream(docUri);
                    return null;
                }
                long id = Long.parseLong(idStr);
                return openImageStream(id);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error handling media request: " + uri, e);
        }
        return null;
    }

    private WebResourceResponse openImageStream(long id) {
        try {
            Uri contentUri = ContentUris.withAppendedId(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, id);
            InputStream is = getContentResolver().openInputStream(contentUri);
            String mimeType = getContentResolver().getType(contentUri);
            if (mimeType == null || mimeType.isEmpty()) mimeType = "image/jpeg";
            if (is != null) {
                Map<String, String> headers = new HashMap<>();
                headers.put("Access-Control-Allow-Origin", "*");
                headers.put("Cache-Control", "no-cache");
                return new WebResourceResponse(mimeType, null, 200, "OK", headers, is);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error opening stream for media id " + id, e);
        }
        return null;
    }

    private WebResourceResponse openDocStream(Uri docUri) {
        try {
            InputStream is = null;
            String mimeType = null;
            if ("file".equalsIgnoreCase(docUri.getScheme())) {
                String path = docUri.getPath();
                if (path != null) {
                    File file = new File(path);
                    if (file.exists()) {
                        is = new FileInputStream(file);
                    }
                }
            }
            if (is == null) {
                is = getContentResolver().openInputStream(docUri);
                try {
                    mimeType = getContentResolver().getType(docUri);
                } catch (Exception ignored) {}
            }
            if (mimeType == null || mimeType.isEmpty() || "application/octet-stream".equals(mimeType)) {
                String p = docUri.getPath();
                if (p != null) {
                    String lower = p.toLowerCase();
                    if (lower.endsWith(".png")) mimeType = "image/png";
                    else if (lower.endsWith(".webp")) mimeType = "image/webp";
                    else if (lower.endsWith(".avif")) mimeType = "image/avif";
                    else if (lower.endsWith(".heic") || lower.endsWith(".heif")) mimeType = "image/heic";
                    else if (lower.endsWith(".gif")) mimeType = "image/gif";
                    else if (lower.endsWith(".bmp")) mimeType = "image/bmp";
                    else if (lower.endsWith(".mp4") || lower.endsWith(".mkv") || lower.endsWith(".mov")) mimeType = "video/mp4";
                    else mimeType = "image/jpeg";
                } else {
                    mimeType = "image/jpeg";
                }
            }
            if (is != null) {
                Map<String, String> headers = new HashMap<>();
                headers.put("Access-Control-Allow-Origin", "*");
                headers.put("Cache-Control", "no-cache");
                return new WebResourceResponse(mimeType, null, 200, "OK", headers, is);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error opening stream for doc URI " + docUri, e);
        }
        return null;
    }

    public class NativeBridge {
        @JavascriptInterface
        public String getDevicePhotosJson() {
            return scanMediaStorePhotos();
        }

        @JavascriptInterface
        public String getInitialOpenedPhotoJson() {
            return openedPhotoJson != null ? openedPhotoJson : "";
        }

        @JavascriptInterface
        public boolean hasPermissions() {
            return hasStoragePermission();
        }

        @JavascriptInterface
        public void requestAppPermissions() {
            runOnUiThread(() -> checkAndRequestPermissions());
        }

        @JavascriptInterface
        public void setAsDefaultViewer() {
            runOnUiThread(() -> {
                try {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                        Intent intent = new Intent(android.provider.Settings.ACTION_MANAGE_DEFAULT_APPS_SETTINGS);
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(intent);
                    } else {
                        Intent intent = new Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                        intent.setData(Uri.parse("package:" + getPackageName()));
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(intent);
                    }
                } catch (Exception e) {
                    try {
                        Intent intent = new Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                        intent.setData(Uri.parse("package:" + getPackageName()));
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(intent);
                    } catch (Exception ex) {
                        Log.e(TAG, "Failed to launch default apps settings", ex);
                    }
                }
            });
        }

        @JavascriptInterface
        public void openFolderPicker() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
                intent.addFlags(
                    Intent.FLAG_GRANT_READ_URI_PERMISSION |
                    Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
                );
                try {
                    startActivityForResult(intent, FOLDER_PICKER_REQUEST_CODE);
                } catch (Exception e) {
                    Log.e(TAG, "Failed to launch folder picker", e);
                }
            });
        }

        @JavascriptInterface
        public void pickFolder() {
            openFolderPicker();
        }

        @JavascriptInterface
        public void openFolder() {
            openFolderPicker();
        }
    }

    private String scanMediaStorePhotos() {
        JSONArray photosArray = new JSONArray();
        SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US);
        isoFormat.setTimeZone(TimeZone.getTimeZone("UTC"));

        Uri[] uris = new Uri[]{
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            MediaStore.Video.Media.EXTERNAL_CONTENT_URI
        };

        for (Uri baseUri : uris) {
            boolean isVideo = baseUri.equals(MediaStore.Video.Media.EXTERNAL_CONTENT_URI);
            String[] projection = new String[]{
                MediaStore.MediaColumns._ID,
                MediaStore.MediaColumns.DISPLAY_NAME,
                MediaStore.MediaColumns.SIZE,
                MediaStore.MediaColumns.MIME_TYPE,
                MediaStore.MediaColumns.DATE_ADDED,
                MediaStore.MediaColumns.DATE_MODIFIED,
                MediaStore.MediaColumns.WIDTH,
                MediaStore.MediaColumns.HEIGHT
            };

            String sortOrder = MediaStore.MediaColumns.DATE_ADDED + " DESC";
            int count = 0;

            try (Cursor cursor = getContentResolver().query(baseUri, projection, null, null, sortOrder)) {
                if (cursor != null && cursor.moveToFirst()) {
                    int idCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns._ID);
                    int nameCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.DISPLAY_NAME);
                    int sizeCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.SIZE);
                    int mimeCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.MIME_TYPE);
                    int dateAddedCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.DATE_ADDED);
                    int widthCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.WIDTH);
                    int heightCol = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.HEIGHT);

                    do {
                        long id = cursor.getLong(idCol);
                        String name = cursor.getString(nameCol);
                        long size = cursor.getLong(sizeCol);
                        String mime = cursor.getString(mimeCol);
                        long dateAdded = cursor.getLong(dateAddedCol);
                        int width = cursor.getInt(widthCol);
                        int height = cursor.getInt(heightCol);

                        if (name == null || name.isEmpty()) name = "Media_" + id;
                        if (mime == null || mime.isEmpty()) mime = isVideo ? "video/mp4" : "image/jpeg";
                        if (width <= 0) width = 1920;
                        if (height <= 0) height = 1080;

                        double aspect = (double) width / (double) height;
                        String dateIso = isoFormat.format(new Date(dateAdded * 1000L));

                        JSONObject photo = new JSONObject();
                        photo.put("id", "android-media-" + id);
                        photo.put("title", name.replaceFirst("[.][^.]+$", ""));
                        photo.put("description", name + (size > 0 ? " (" + (size / 1024) + " KB)" : ""));
                        photo.put("url", "https://" + MEDIA_HOST + "/image/" + id);
                        photo.put("thumbnailUrl", "https://" + MEDIA_HOST + "/thumbnail/" + id);
                        photo.put("width", width);
                        photo.put("height", height);
                        photo.put("aspectRatio", aspect);
                        photo.put("date", dateIso);
                        photo.put("category", isVideo ? "Videos" : "Photos");
                        photo.put("fileType", mime);
                        photo.put("fileSize", size);
                        photo.put("isFavorite", false);
                        photo.put("isVault", false);
                        photo.put("isHidden", false);
                        photo.put("isRaw", name.toLowerCase().endsWith(".dng") || name.toLowerCase().endsWith(".raw"));
                        photo.put("isHdr", false);
                        photo.put("isLivePhoto", false);
                        photo.put("cloudSource", "local");
                        photo.put("rating", 0);

                        JSONObject exif = new JSONObject();
                        exif.put("cameraMake", "Android");
                        exif.put("cameraModel", "Device Camera");
                        exif.put("iso", 100);
                        photo.put("exif", exif);

                        JSONArray tags = new JSONArray();
                        tags.put("device");
                        tags.put(isVideo ? "video" : "photo");
                        photo.put("tags", tags);
                        photo.put("people", new JSONArray());

                        photosArray.put(photo);
                        count++;
                    } while (cursor.moveToNext() && count < 350);
                }
            } catch (Exception e) {
                Log.e(TAG, "Error querying media uri: " + baseUri, e);
            }
        }

        Log.d(TAG, "Scanned total device media items: " + photosArray.length());
        return photosArray.toString();
    }

    private void scanDocumentTree(Uri treeUri) {
        new Thread(() -> {
            try {
                JSONArray newPhotos = new JSONArray();
                SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US);
                isoFormat.setTimeZone(TimeZone.getTimeZone("UTC"));

                String rootDocId = DocumentsContract.getTreeDocumentId(treeUri);
                scanDirectoryRecursive(treeUri, rootDocId, newPhotos, isoFormat, 0);

                if (newPhotos.length() > 0) {
                    runOnUiThread(() -> {
                        String escaped = JSONObject.quote(newPhotos.toString());
                        String js = "(function() {" +
                            "  try {" +
                            "    var imported = JSON.parse(" + escaped + ");" +
                            "    var existing = JSON.parse(localStorage.getItem('galaxsee_imported_photos') || '[]');" +
                            "    var idMap = new Set(existing.map(function(p){ return p.id; }));" +
                            "    var combined = imported.filter(function(p){ return !idMap.has(p.id); }).concat(existing);" +
                            "    localStorage.setItem('galaxsee_imported_photos', JSON.stringify(combined));" +
                            "    window.dispatchEvent(new CustomEvent('folderPhotosImported', { detail: { photos: imported, total: combined.length } }));" +
                            "    window.dispatchEvent(new CustomEvent('galaxseePhotosUpdated', { detail: { photos: combined } }));" +
                            "    console.log('Imported ' + imported.length + ' photos from folder.');" +
                            "  } catch(e) {" +
                            "    console.error('Error handling imported folder photos:', e);" +
                            "  }" +
                            "})();";
                        webView.evaluateJavascript(js, null);
                    });
                }
            } catch (Exception e) {
                Log.e(TAG, "Error scanning document tree: " + treeUri, e);
            }
        }).start();
    }

    private void scanDirectoryRecursive(Uri treeUri, String parentDocId, JSONArray newPhotos, SimpleDateFormat isoFormat, int depth) {
        if (depth > 4 || newPhotos.length() >= 500) return;
        try {
            Uri childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, parentDocId);
            String[] projection = new String[]{
                DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                DocumentsContract.Document.COLUMN_MIME_TYPE,
                DocumentsContract.Document.COLUMN_SIZE,
                DocumentsContract.Document.COLUMN_LAST_MODIFIED
            };

            try (Cursor cursor = getContentResolver().query(childrenUri, projection, null, null, null)) {
                if (cursor != null && cursor.moveToFirst()) {
                    int idCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DOCUMENT_ID);
                    int nameCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DISPLAY_NAME);
                    int mimeCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_MIME_TYPE);
                    int sizeCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_SIZE);
                    int modCol = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_LAST_MODIFIED);

                    do {
                        String docId = cursor.getString(idCol);
                        String name = cursor.getString(nameCol);
                        String mime = cursor.getString(mimeCol);
                        long size = cursor.getLong(sizeCol);
                        long mod = cursor.getLong(modCol);

                        if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                            scanDirectoryRecursive(treeUri, docId, newPhotos, isoFormat, depth + 1);
                        } else if (mime != null && (mime.startsWith("image/") || mime.startsWith("video/"))) {
                            Uri docUri = DocumentsContract.buildDocumentUriUsingTree(treeUri, docId);
                            String docKey = "tree_" + Math.abs(docUri.toString().hashCode()) + "_" + Math.abs(docId.hashCode());
                            sDirectUriMap.put(docKey, docUri);

                            boolean isVideo = mime.startsWith("video/");
                            String dateIso = isoFormat.format(new Date(mod > 0 ? mod : System.currentTimeMillis()));

                            JSONObject photo = new JSONObject();
                            photo.put("id", "tree-doc-" + docKey);
                            photo.put("title", name != null ? name.replaceFirst("[.][^.]+$", "") : "Imported File");
                            photo.put("description", (name != null ? name : "File") + " (" + (size / 1024) + " KB)");
                            photo.put("url", "https://" + MEDIA_HOST + "/image/doc_" + docKey);
                            photo.put("thumbnailUrl", "https://" + MEDIA_HOST + "/thumbnail/doc_" + docKey);
                            photo.put("width", 1920);
                            photo.put("height", 1080);
                            photo.put("aspectRatio", 1.77);
                            photo.put("date", dateIso);
                            photo.put("category", isVideo ? "Videos" : "Imported Folder");
                            photo.put("fileType", mime);
                            photo.put("fileSize", size > 0 ? size : 2048000);
                            photo.put("isFavorite", false);
                            photo.put("isVault", false);
                            photo.put("isHidden", false);
                            photo.put("isRaw", false);
                            photo.put("isHdr", false);
                            photo.put("isLivePhoto", false);
                            photo.put("cloudSource", "local");
                            photo.put("rating", 0);

                            newPhotos.put(photo);
                        }
                    } while (cursor.moveToNext() && newPhotos.length() < 500);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "Error reading child document directory: " + parentDocId, e);
        }
    }

    private void syncDeviceMediaToWeb() {
        new Thread(() -> {
            String photosJson = scanMediaStorePhotos();
            runOnUiThread(() -> {
                if (webView != null) {
                    String escapedJson = JSONObject.quote(photosJson);
                    String js = "(function() {" +
                        "  var raw = " + escapedJson + ";" +
                        "  try {" +
                        "    var photos = JSON.parse(raw);" +
                        "    if (Array.isArray(photos) && photos.length > 0) {" +
                        "      localStorage.setItem('galaxsee_imported_photos', JSON.stringify(photos));" +
                        "      window.dispatchEvent(new CustomEvent('galaxseePhotosUpdated', { detail: { photos: photos } }));" +
                        "      console.log('Successfully synced ' + photos.length + ' device photos to Galaxsee gallery.');" +
                        "    }" +
                        "  } catch (e) {" +
                        "    console.error('Error syncing photos to web:', e);" +
                        "  }" +
                        "})();";
                    webView.evaluateJavascript(js, null);
                }
            });
        }).start();
    }

    private boolean hasStoragePermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            return checkSelfPermission("android.permission.READ_MEDIA_IMAGES") == PackageManager.PERMISSION_GRANTED;
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            return checkSelfPermission("android.permission.READ_EXTERNAL_STORAGE") == PackageManager.PERMISSION_GRANTED;
        }
        return true;
    }

    private void checkAndRequestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            String[] permissions;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                permissions = new String[]{
                    "android.permission.READ_MEDIA_IMAGES",
                    "android.permission.READ_MEDIA_VIDEO",
                    "android.permission.READ_MEDIA_AUDIO",
                    "android.permission.ACCESS_MEDIA_LOCATION",
                    "android.permission.CAMERA"
                };
            } else {
                permissions = new String[]{
                    "android.permission.READ_EXTERNAL_STORAGE",
                    "android.permission.WRITE_EXTERNAL_STORAGE",
                    "android.permission.CAMERA"
                };
            }

            boolean needRequest = false;
            for (String p : permissions) {
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) {
                    needRequest = true;
                    break;
                }
            }
            if (needRequest) {
                requestPermissions(permissions, PERMISSION_REQUEST_CODE);
            } else {
                syncDeviceMediaToWeb();
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean granted = false;
            for (int r : grantResults) {
                if (r == PackageManager.PERMISSION_GRANTED) {
                    granted = true;
                    break;
                }
            }
            if (granted) {
                Log.d(TAG, "Storage permissions granted. Auto-loading device media...");
                syncDeviceMediaToWeb();
                if (webView != null) {
                    webView.reload();
                }
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (filePathCallback != null) {
                Uri[] results = null;
                if (resultCode == Activity.RESULT_OK && data != null) {
                    if (data.getData() != null) {
                        results = new Uri[]{data.getData()};
                    } else if (data.getClipData() != null) {
                        int count = data.getClipData().getItemCount();
                        results = new Uri[count];
                        for (int i = 0; i < count; i++) {
                            results[i] = data.getClipData().getItemAt(i).getUri();
                        }
                    }
                }
                filePathCallback.onReceiveValue(results);
                filePathCallback = null;
            }
        } else if (requestCode == FOLDER_PICKER_REQUEST_CODE && resultCode == Activity.RESULT_OK && data != null) {
            Uri treeUri = data.getData();
            if (treeUri != null) {
                try {
                    getContentResolver().takePersistableUriPermission(
                        treeUri,
                        Intent.FLAG_GRANT_READ_URI_PERMISSION
                    );
                } catch (Exception ignored) {}
                scanDocumentTree(treeUri);
            }
        } else {
            super.onActivityResult(requestCode, resultCode, data);
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null) {
            webView.evaluateJavascript(
                "(function() { " +
                "  if (window.__galaxseeHandleBackPressed && window.__galaxseeHandleBackPressed()) { return true; } " +
                "  const backBtn = document.querySelector(\"button[title*=\\\"Back\\\"], button[aria-label*=\\\"Back\\\"], button.galaxsee-back-btn\"); " +
                "  if (backBtn) { backBtn.click(); return true; } " +
                "  return false; " +
                "})()",
                result -> {
                    if (!"true".equals(result)) {
                        if (webView.canGoBack()) {
                            webView.goBack();
                        } else {
                            MainActivity.super.onBackPressed();
                        }
                    }
                }
            );
            return;
        }
        super.onBackPressed();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) webView.onResume();
    }

    @Override
    protected void onPause() {
        if (webView != null) webView.onPause();
        super.onPause();
    }

    @Override
    protected void onDestroy() {
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}
