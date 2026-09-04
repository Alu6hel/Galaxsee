package com.galaxsee.app;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
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
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

public class MainActivity extends Activity {
    private static final String TAG = "GalaxseePro";
    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST_CODE = 1001;
    private static final int PERMISSION_REQUEST_CODE = 1002;
    private static final int FOLDER_PICKER_REQUEST_CODE = 1003;
    public static final String MEDIA_HOST = "galaxsee.local";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

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
        webView.addJavascriptInterface(new NativeBridge(), "GalaxseeAndroid");

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

            if (path.startsWith("/thumbnail/")) {
                String idStr = path.substring("/thumbnail/".length());
                if (idStr.startsWith("doc_")) {
                    String docUriStr = Uri.decode(idStr.substring(4));
                    Uri docUri = Uri.parse(docUriStr);
                    return openDocStream(docUri);
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
                    return new WebResourceResponse("image/jpeg", "UTF-8", new ByteArrayInputStream(data));
                }
                return openImageStream(id);
            } else if (path.startsWith("/image/")) {
                String idStr = path.substring("/image/".length());
                if (idStr.startsWith("doc_")) {
                    String docUriStr = Uri.decode(idStr.substring(4));
                    Uri docUri = Uri.parse(docUriStr);
                    return openDocStream(docUri);
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
            if (mimeType == null) mimeType = "image/jpeg";
            if (is != null) {
                return new WebResourceResponse(mimeType, "UTF-8", is);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error opening stream for media id " + id, e);
        }
        return null;
    }

    private WebResourceResponse openDocStream(Uri docUri) {
        try {
            InputStream is = getContentResolver().openInputStream(docUri);
            String mimeType = getContentResolver().getType(docUri);
            if (mimeType == null) mimeType = "image/jpeg";
            if (is != null) {
                return new WebResourceResponse(mimeType, "UTF-8", is);
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
        public boolean hasPermissions() {
            return hasStoragePermission();
        }

        @JavascriptInterface
        public void requestAppPermissions() {
            runOnUiThread(() -> checkAndRequestPermissions());
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

                        if (name == null) name = "Media_" + id;
                        if (mime == null) mime = isVideo ? "video/mp4" : "image/jpeg";
                        if (width <= 0) width = 1920;
                        if (height <= 0) height = 1080;

                        double aspect = (double) width / (double) height;
                        String dateIso = isoFormat.format(new Date(dateAdded * 1000L));

                        JSONObject photo = new JSONObject();
                        photo.put("id", "android-media-" + id);
                        photo.put("title", name.replaceFirst("[.][^.]+$", ""));
                        photo.put("description", name + " (" + (size / 1024) + " KB)");
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

                Uri childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(
                    treeUri,
                    DocumentsContract.getTreeDocumentId(treeUri)
                );

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

                            if (mime != null && (mime.startsWith("image/") || mime.startsWith("video/"))) {
                                Uri docUri = DocumentsContract.buildDocumentUriUsingTree(treeUri, docId);
                                String encoded = Uri.encode(docUri.toString());
                                boolean isVideo = mime.startsWith("video/");
                                String dateIso = isoFormat.format(new Date(mod > 0 ? mod : System.currentTimeMillis()));

                                JSONObject photo = new JSONObject();
                                photo.put("id", "tree-doc-" + Math.abs(docId.hashCode()));
                                photo.put("title", name != null ? name.replaceFirst("[.][^.]+$", "") : "Imported File");
                                photo.put("description", name + " (" + (size / 1024) + " KB)");
                                photo.put("url", "https://" + MEDIA_HOST + "/image/doc_" + encoded);
                                photo.put("thumbnailUrl", "https://" + MEDIA_HOST + "/thumbnail/doc_" + encoded);
                                photo.put("width", 1920);
                                photo.put("height", 1080);
                                photo.put("aspectRatio", 1.77);
                                photo.put("date", dateIso);
                                photo.put("category", isVideo ? "Videos" : "Imported Folder");
                                photo.put("fileType", mime);
                                photo.put("fileSize", size);
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
                        } while (cursor.moveToNext());
                    }
                }

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
                            "    console.log('Imported ' + imported.length + ' photos from folder.');" +
                            "    if (window.location) window.location.reload();" +
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
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
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
