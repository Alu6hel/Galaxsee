package com.galaxsee.app;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import android.util.Log;
import java.io.File;
import java.io.FileNotFoundException;

public class GalaxseeMediaProvider extends ContentProvider {
    private static final String TAG = "GalaxseeMediaProvider";
    public static final String AUTHORITY = "com.galaxsee.app.provider";
    public static final Uri CONTENT_URI = Uri.parse("content://" + AUTHORITY);

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder) {
        if (projection == null) {
            projection = new String[]{ OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE };
        }
        MatrixCursor cursor = new MatrixCursor(projection);
        File file = getFileForUri(uri);
        if (file != null && file.exists()) {
            MatrixCursor.RowBuilder row = cursor.newRow();
            for (String col : projection) {
                if (OpenableColumns.DISPLAY_NAME.equals(col)) {
                    row.add(file.getName());
                } else if (OpenableColumns.SIZE.equals(col)) {
                    row.add(file.length());
                } else {
                    row.add(null);
                }
            }
        }
        return cursor;
    }

    @Override
    public String getType(Uri uri) {
        String path = uri.getPath();
        if (path != null) {
            String lower = path.toLowerCase();
            if (lower.endsWith(".png")) return "image/png";
            if (lower.endsWith(".webp")) return "image/webp";
            if (lower.endsWith(".gif")) return "image/gif";
            if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
        }
        return "image/jpeg";
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        File file = getFileForUri(uri);
        if (file != null && file.exists()) {
            return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
        }
        Log.e(TAG, "File not found for uri: " + uri);
        throw new FileNotFoundException("GalaxseeMediaProvider: File not found for " + uri);
    }

    private File getFileForUri(Uri uri) {
        if (getContext() == null) return null;
        String path = uri.getPath();
        if (path == null) return null;
        while (path.startsWith("/")) {
            path = path.substring(1);
        }
        File clipboardDir = new File(getContext().getCacheDir(), "clipboard");
        File file = new File(clipboardDir, path);
        if (file.exists()) return file;

        // Fallback: look for any file in clipboard dir
        File[] files = clipboardDir.listFiles();
        if (files != null && files.length > 0) {
            for (File f : files) {
                if (f.isFile() && f.length() > 0) return f;
            }
        }
        return null;
    }

    @Override public Uri insert(Uri uri, ContentValues values) { return null; }
    @Override public int delete(Uri uri, String selection, String[] selectionArgs) { return 0; }
    @Override public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) { return 0; }
}
