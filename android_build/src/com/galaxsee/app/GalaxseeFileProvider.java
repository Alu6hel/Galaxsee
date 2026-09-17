package com.galaxsee.app;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;

public class GalaxseeFileProvider extends ContentProvider {
    public static final String AUTHORITY = "com.galaxsee.app.fileprovider";

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        if (getContext() == null) throw new FileNotFoundException("Context is null");
        String path = uri.getPath();
        if (path != null && path.startsWith("/")) path = path.substring(1);
        
        File file = new File(getContext().getCacheDir(), path);
        if (!file.exists() && getContext().getExternalCacheDir() != null) {
            file = new File(getContext().getExternalCacheDir(), path);
        }
        if (!file.exists()) {
            throw new FileNotFoundException("File not found: " + path);
        }
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public String getType(Uri uri) {
        String path = uri.getPath();
        if (path != null && path.endsWith(".apk")) {
            return "application/vnd.android.package-archive";
        }
        if (path != null && path.endsWith(".svg")) {
            return "image/svg+xml";
        }
        return "application/octet-stream";
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder) {
        if (projection == null) {
            projection = new String[] { OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE };
        }
        MatrixCursor cursor = new MatrixCursor(projection, 1);
        if (getContext() == null) return cursor;
        String path = uri.getPath();
        if (path != null && path.startsWith("/")) path = path.substring(1);
        File file = new File(getContext().getCacheDir(), path);
        if (!file.exists() && getContext().getExternalCacheDir() != null) {
            file = new File(getContext().getExternalCacheDir(), path);
        }
        if (file.exists()) {
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
    public Uri insert(Uri uri, ContentValues values) { return null; }

    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) { return 0; }

    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) { return 0; }
}
