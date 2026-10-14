#!/usr/bin/env python3
import sys
import os
import subprocess
import json

def patch_css(css_file):
    print(f"Adding Language Picker styles to {css_file}")
    if not os.path.exists(css_file):
        return
    with open(css_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if ".language-picker-modal-card" in content:
        print("CSS already contains language-picker styles, skipping.")
        return

    css_addon = """
/* GALAXSEE PRO DISPLAY LANGUAGE PICKER (Matches media_1791935491031.png) */
.language-picker-modal-card {
  background: #0f172a !important;
  border: 2px solid #38bdf8 !important;
  border-radius: 16px !important;
  padding: 16px 14px 14px 14px !important;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.85), 0 0 25px rgba(56, 189, 248, 0.25) !important;
  width: 90% !important;
  max-width: 290px !important;
  color: #ffffff !important;
  animation: modalScaleIn 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
}
.language-picker-header {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding-bottom: 10px !important;
  margin-bottom: 8px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
}
.language-picker-title {
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.12em !important;
  color: #94a3b8 !important;
  text-transform: uppercase !important;
}
.lang-options-list {
  display: flex !important;
  flex-direction: column !important;
  gap: 5px !important;
}
.lang-option-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  width: 100% !important;
  padding: 9px 14px !important;
  border-radius: 24px !important;
  border: none !important;
  background: transparent !important;
  color: #ffffff !important;
  font-size: 14.5px !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
  text-align: left !important;
  outline: none !important;
}
.lang-option-btn:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}
.lang-option-btn:active {
  transform: scale(0.98) !important;
}
.lang-option-btn.selected {
  background: #38bdf8 !important;
  color: #04101d !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 14px rgba(56, 189, 248, 0.4) !important;
}
.lang-option-btn.selected,
.lang-option-btn.selected .lang-name,
.lang-option-btn.selected .lang-check {
  color: #04101d !important;
  font-weight: 900 !important;
}
.lang-option-left {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}
.lang-flag {
  font-size: 17px !important;
  line-height: 1 !important;
}
.lang-name {
  font-size: 14px !important;
  letter-spacing: -0.01em !important;
}
.lang-check {
  font-size: 15px !important;
  font-weight: 800 !important;
}
"""
    with open(css_file, "a", encoding="utf-8") as f:
        f.write("\n" + css_addon)
    print(f"Successfully added language-picker CSS to {css_file}")

def patch_js(js_file):
    print(f"\n=======================================================")
    print(f"PATCHING JS: {js_file}")
    print(f"=======================================================")
    
    if not os.path.exists(js_file):
        print(f"File {js_file} does not exist, skipping.")
        return

    with open(js_file, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)

    def check_step(step_name, current_code):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(current_code)
            tname = tf.name
        res = subprocess.run(["node", "-c", tname], capture_output=True, text=True)
        os.remove(tname)
        if res.returncode != 0:
            print(f"FAILED AT: {step_name}")
            print(res.stderr[:400])
            sys.exit(1)
        else:
            print(f"  [syntax ok: {step_name}]")

    # -------------------------------------------------------------
    # 1. Tv: Deduplicate "Photo Location & Storage" Cards (4 -> 1)
    # -------------------------------------------------------------
    card_sig = 'a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5",'
    starts = []
    p = 0
    while True:
        idx = code.find(card_sig, p)
        if idx == -1: break
        starts.append(idx)
        p = idx + len(card_sig)

    if len(starts) == 4:
        next_sec = 'a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2",'
        idx_next = code.find(next_sec, starts[1])
        if idx_next != -1:
            code = code[:starts[1]] + code[idx_next:]
            print("[1] Successfully removed 3 duplicate Photo Location & Storage cards in Tv (now exactly 1)")
    elif len(starts) == 1:
        print("[1] Note: Tv cards already deduplicated (exactly 1 present)")
    check_step("1. Tv", code)

    # -------------------------------------------------------------
    # 2. Inject Multilingual (i18n) Engine at the Top
    # -------------------------------------------------------------
    i18n_sig = "window.__galaxsee_i18n="
    if i18n_sig not in code:
        languages_data = [
            {"code": "en", "name": "English (US)", "flag": "🇺🇸"},
            {"code": "hi", "name": "हिन्दी", "flag": "🇮🇳"},
            {"code": "es", "name": "Español", "flag": "🇪🇸"},
            {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
            {"code": "fr", "name": "Français", "flag": "🇫🇷"},
            {"code": "ja", "name": "日本語", "flag": "🇯🇵"},
            {"code": "zh", "name": "简体中文", "flag": "🇨🇳"},
        ]
        translations_data = {
            "en": {
                "displayLanguage": "DISPLAY LANGUAGE",
                "copyClipboard": "Copy Photo to Clipboard",
                "openFullscreen": "Open / View Fullscreen",
                "addFavorite": "Add to Favorites",
                "removeFavorite": "Remove from Favorites",
                "convertToSvg": "Convert to SVG Vector",
                "editPhoto": "Edit Photo",
                "photoInfo": "Photo Info & EXIF",
                "setAppWallpaper": "Set as App Wallpaper",
                "setDesktopWallpaper": "Set photo as desktop wallpaper",
                "moveToTrash": "Move to Trash",
                "backToGrid": "Back to Grid",
                "fullScreen": "Full Screen",
                "edit": "Edit",
                "moreOptions": "More Options",
                "focusPeaking": "Focus Peaking (P)",
                "exposureZebras": "Exposure Zebras (Z)",
                "outdoorMode": "Max Brightness Outdoor Mode",
                "hdrBoost": "Ultra HDR Wide Gamut Boost",
                "exportPdf": "Export as PDF Document",
                "formatConverter": "Convert Format & SVG Vector Tracing",
                "resizeCompress": "Resize & Compress Image",
                "audioStudio": "Acoustic Mastering in Audio Studio",
                "gallery": "Gallery",
                "favorites": "Favorites",
                "folders": "Folders",
                "safeBox": "Safe Box",
                "cullStudio": "Cull Studio",
                "duplicates": "Duplicates Cleaner",
                "recycleBin": "Recycle Bin",
                "settings": "Settings",
                "import": "Import",
                "searchPlaceholder": "Search photos, folders, tags, dates, cameras...",
                "playStory": "Play Story",
                "selectAll": "Select All",
                "photoLocation": "Photo Location & Storage",
                "copyPath": "Copy Path",
                "openInTab": "Open in New Tab",
            },
            "hi": {
                "displayLanguage": "भाषा चुनें (DISPLAY LANGUAGE)",
                "copyClipboard": "फ़ोटो क्लिपबोर्ड पर कॉपी करें",
                "openFullscreen": "फ़ुलस्क्रीन में देखें",
                "addFavorite": "पसंदीदा में जोड़ें",
                "removeFavorite": "पसंदीदा से हटाएं",
                "convertToSvg": "SVG वेक्टर में बदलें",
                "editPhoto": "फ़ोटो संपादित करें",
                "photoInfo": "फ़ोटो जानकारी और EXIF",
                "setAppWallpaper": "ऐप वॉलपेपर बनाएं",
                "setDesktopWallpaper": "डेस्कटॉप वॉलपेपर बनाएं",
                "moveToTrash": "ट्रैश में डालें",
                "backToGrid": "ग्रिड पर वापस",
                "fullScreen": "पूर्ण स्क्रीन",
                "edit": "संपादित करें",
                "moreOptions": "अधिक विकल्प",
                "focusPeaking": "फ़ोकस पीकिंग (P)",
                "exposureZebras": "एक्सपोज़र ज़ेब्रा (Z)",
                "outdoorMode": "आउटडोर ब्राइटनेस मोड",
                "hdrBoost": "अल्ट्रा HDR बूस्ट",
                "exportPdf": "PDF दस्तावेज़ निर्यात करें",
                "formatConverter": "फ़ॉर्मैट कनवर्टर और SVG ट्रेसिंग",
                "resizeCompress": "छवि आकार बदलें और कंप्रेस करें",
                "audioStudio": "ऑडियो स्टूडियो मास्टरिंग",
                "gallery": "गैलरी",
                "favorites": "पसंदीदा",
                "folders": "फ़ोल्डर",
                "safeBox": "सुरक्षित तिजोरी",
                "cullStudio": "कल स्टूडियो",
                "duplicates": "डुप्लीकेट क्लीनर",
                "recycleBin": "रीसायकल बिन",
                "settings": "सेटिंग्स",
                "import": "आयात करें",
                "searchPlaceholder": "फ़ोटो, फ़ोल्डर, टैग खोजें...",
                "playStory": "कहानी चलाएं",
                "selectAll": "सभी चुनें",
                "photoLocation": "फ़ोटो स्थान और स्टोरेज",
                "copyPath": "पाथ कॉपी करें",
                "openInTab": "नए टैब में खोलें",
            },
            "es": {
                "displayLanguage": "IDIOMA VISUAL (DISPLAY LANGUAGE)",
                "copyClipboard": "Copiar foto al portapapeles",
                "openFullscreen": "Abrir en pantalla completa",
                "addFavorite": "Añadir a favoritos",
                "removeFavorite": "Quitar de favoritos",
                "convertToSvg": "Convertir a vector SVG",
                "editPhoto": "Editar foto",
                "photoInfo": "Información de foto y EXIF",
                "setAppWallpaper": "Fondo de la aplicación",
                "setDesktopWallpaper": "Fondo de escritorio",
                "moveToTrash": "Mover a la papelera",
                "backToGrid": "Volver a la cuadrícula",
                "fullScreen": "Pantalla completa",
                "edit": "Editar",
                "moreOptions": "Más opciones",
                "focusPeaking": "Pico de enfoque (P)",
                "exposureZebras": "Cebras de exposición (Z)",
                "outdoorMode": "Modo exterior máximo brillo",
                "hdrBoost": "Impulso Ultra HDR",
                "exportPdf": "Exportar documento PDF",
                "formatConverter": "Convertir formato y trazado SVG",
                "resizeCompress": "Redimensionar y comprimir",
                "audioStudio": "Masterización de audio",
                "gallery": "Galería",
                "favorites": "Favoritos",
                "folders": "Carpetas",
                "safeBox": "Caja fuerte",
                "cullStudio": "Estudio de descarte",
                "duplicates": "Limpiador de duplicados",
                "recycleBin": "Papelera de reciclaje",
                "settings": "Ajustes",
                "import": "Importar",
                "searchPlaceholder": "Buscar fotos, carpetas, etiquetas...",
                "playStory": "Reproducir historia",
                "selectAll": "Seleccionar todo",
                "photoLocation": "Ubicación de foto y almacenamiento",
                "copyPath": "Copiar ruta",
                "openInTab": "Abrir en nueva pestaña",
            },
            "de": {
                "displayLanguage": "ANZEIGESPRACHE (DISPLAY LANGUAGE)",
                "copyClipboard": "Foto in Zwischenablage kopieren",
                "openFullscreen": "Im Vollbildmodus öffnen",
                "addFavorite": "Zu Favoriten hinzufügen",
                "removeFavorite": "Aus Favoriten entfernen",
                "convertToSvg": "In SVG-Vektor umwandeln",
                "editPhoto": "Foto bearbeiten",
                "photoInfo": "Foto-Info & EXIF",
                "setAppWallpaper": "Als App-Hintergrund festlegen",
                "setDesktopWallpaper": "Als Desktop-Hintergrund festlegen",
                "moveToTrash": "In den Papierkorb verschieben",
                "backToGrid": "Zurück zur Übersicht",
                "fullScreen": "Vollbild",
                "edit": "Bearbeiten",
                "moreOptions": "Weitere Optionen",
                "focusPeaking": "Fokus-Peaking (P)",
                "exposureZebras": "Belichtungszebras (Z)",
                "outdoorMode": "Max. Helligkeit Outdoor-Modus",
                "hdrBoost": "Ultra HDR Verstärkung",
                "exportPdf": "Als PDF-Dokument exportieren",
                "formatConverter": "Formatkonvertierung & SVG-Vektorisierung",
                "resizeCompress": "Bild skalieren & komprimieren",
                "audioStudio": "Audio-Studio Mastering",
                "gallery": "Galerie",
                "favorites": "Favoriten",
                "folders": "Ordner",
                "safeBox": "Sicherheits-Tresor",
                "cullStudio": "Cull Studio",
                "duplicates": "Duplikate-Bereiniger",
                "recycleBin": "Papierkorb",
                "settings": "Einstellungen",
                "import": "Importieren",
                "searchPlaceholder": "Fotos, Ordner, Tags suchen...",
                "playStory": "Story abspielen",
                "selectAll": "Alles auswählen",
                "photoLocation": "Foto-Standort & Speicher",
                "copyPath": "Pfad kopieren",
                "openInTab": "In neuem Tab öffnen",
            },
            "fr": {
                "displayLanguage": "LANGUE D'AFFICHAGE (DISPLAY LANGUAGE)",
                "copyClipboard": "Copier la photo dans le presse-papier",
                "openFullscreen": "Ouvrir en plein écran",
                "addFavorite": "Ajouter aux favoris",
                "removeFavorite": "Retirer des favoris",
                "convertToSvg": "Convertir en vecteur SVG",
                "editPhoto": "Modifier la photo",
                "photoInfo": "Infos photo & EXIF",
                "setAppWallpaper": "Définir comme fond d'application",
                "setDesktopWallpaper": "Définir comme fond d'écran",
                "moveToTrash": "Déplacer dans la corbeille",
                "backToGrid": "Retour à la grille",
                "fullScreen": "Plein écran",
                "edit": "Modifier",
                "moreOptions": "Plus d'options",
                "focusPeaking": "Focus Peaking (P)",
                "exposureZebras": "Zèbres d'exposition (Z)",
                "outdoorMode": "Luminosité maximale extérieur",
                "hdrBoost": "Boost Ultra HDR",
                "exportPdf": "Exporter en document PDF",
                "formatConverter": "Conversion de format & vectorisation SVG",
                "resizeCompress": "Redimensionner & compresser",
                "audioStudio": "Mastering studio audio",
                "gallery": "Galerie",
                "favorites": "Favoris",
                "folders": "Dossiers",
                "safeBox": "Coffre-fort",
                "cullStudio": "Studio de tri",
                "duplicates": "Nettoyeur de doublons",
                "recycleBin": "Corbeille",
                "settings": "Paramètres",
                "import": "Importer",
                "searchPlaceholder": "Rechercher photos, dossiers, tags...",
                "playStory": "Lire l'histoire",
                "selectAll": "Tout sélectionner",
                "photoLocation": "Emplacement & stockage",
                "copyPath": "Copier le chemin",
                "openInTab": "Ouvrir dans un nouvel onglet",
            },
            "ja": {
                "displayLanguage": "表示言語 (DISPLAY LANGUAGE)",
                "copyClipboard": "写真をクリップボードにコピー",
                "openFullscreen": "全画面表示で開く",
                "addFavorite": "お気に入りに追加",
                "removeFavorite": "お気に入りから削除",
                "convertToSvg": "SVGベクターに変換",
                "editPhoto": "写真を編集",
                "photoInfo": "写真情報 & EXIF",
                "setAppWallpaper": "アプリの壁紙に設定",
                "setDesktopWallpaper": "デスクトップ壁紙に設定",
                "moveToTrash": "ゴミ箱に移動",
                "backToGrid": "グリッドに戻る",
                "fullScreen": "フルスクリーン",
                "edit": "編集",
                "moreOptions": "その他のオプション",
                "focusPeaking": "フォーカスピーキング (P)",
                "exposureZebras": "露出ゼブラ (Z)",
                "outdoorMode": "最大輝度屋外モード",
                "hdrBoost": "ウルトラHDRブースト",
                "exportPdf": "PDFドキュメントとしてエクスポート",
                "formatConverter": "フォーマット変換 & SVGトレース",
                "resizeCompress": "画像サイズ変更 & 圧縮",
                "audioStudio": "オーディオスタジオマスタリング",
                "gallery": "ギャラリー",
                "favorites": "お気に入り",
                "folders": "フォルダー",
                "safeBox": "セーフボックス",
                "cullStudio": "選別スタジオ",
                "duplicates": "重複クリーナー",
                "recycleBin": "ゴミ箱",
                "settings": "設定",
                "import": "インポート",
                "searchPlaceholder": "写真、フォルダー、タグを検索...",
                "playStory": "ストーリー再生",
                "selectAll": "すべて選択",
                "photoLocation": "写真の場所とストレージ",
                "copyPath": "パスをコピー",
                "openInTab": "新しいタブで開く",
            },
            "zh": {
                "displayLanguage": "显示语言 (DISPLAY LANGUAGE)",
                "copyClipboard": "复制照片到剪贴板",
                "openFullscreen": "全屏查看",
                "addFavorite": "添加到收藏",
                "removeFavorite": "从收藏中移除",
                "convertToSvg": "转换为SVG矢量图",
                "editPhoto": "编辑照片",
                "photoInfo": "照片信息与EXIF",
                "setAppWallpaper": "设为应用壁纸",
                "setDesktopWallpaper": "设为桌面壁纸",
                "moveToTrash": "移至回收站",
                "backToGrid": "返回网格",
                "fullScreen": "全屏",
                "edit": "编辑",
                "moreOptions": "更多选项",
                "focusPeaking": "对焦峰值 (P)",
                "exposureZebras": "曝光斑马纹 (Z)",
                "outdoorMode": "户外最高亮度模式",
                "hdrBoost": "Ultra HDR色彩增强",
                "exportPdf": "导出为PDF文档",
                "formatConverter": "格式转换与SVG矢量描摹",
                "resizeCompress": "调整大小与压缩",
                "audioStudio": "音频工作室母带制作",
                "gallery": "相册",
                "favorites": "收藏夹",
                "folders": "文件夹",
                "safeBox": "保险箱",
                "cullStudio": "挑选工作室",
                "duplicates": "重复清理",
                "recycleBin": "回收站",
                "settings": "设置",
                "import": "导入",
                "searchPlaceholder": "搜索照片、文件夹、标签...",
                "playStory": "播放幻灯片",
                "selectAll": "全选",
                "photoLocation": "照片位置与存储",
                "copyPath": "复制路径",
                "openInTab": "在新标签页打开",
            },
        }

        i18n_engine_code = f"""
// --- GALAXSEE PRO MULTILINGUAL (i18n) ENGINE ---
(function(){{
  const LANGUAGES = {json.dumps(languages_data, ensure_ascii=False)};
  const TRANSLATIONS = {json.dumps(translations_data, ensure_ascii=False)};

  let currentLang = 'en';
  try {{
    currentLang = localStorage.getItem('galaxsee_language') || 'en';
  }} catch(e) {{}}
  if (!TRANSLATIONS[currentLang]) currentLang = 'en';

  window.__galaxsee_i18n = {{
    languages: LANGUAGES,
    get currentLanguage() {{ return currentLang; }},
    setLanguage(lang) {{
      if (TRANSLATIONS[lang]) {{
        currentLang = lang;
        try {{ localStorage.setItem('galaxsee_language', lang); }} catch(e) {{}}
        window.dispatchEvent(new CustomEvent('galaxsee_language_changed', {{ detail: {{ lang }} }}));
      }}
    }},
    t(key) {{
      const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
      return dict[key] || TRANSLATIONS.en[key] || key;
    }}
  }};

  window.openGalaxseeLanguagePicker = function() {{
    const existing = document.getElementById('galaxsee-language-modal');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'galaxsee-language-modal';
    overlay.className = 'galaxsee-backdrop fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in';
    overlay.onclick = (e) => {{ if (e.target === overlay) overlay.remove(); }};

    const card = document.createElement('div');
    card.className = 'language-picker-modal-card';
    card.onclick = (e) => e.stopPropagation();

    const header = document.createElement('div');
    header.className = 'language-picker-header';
    header.innerHTML = `
      <span class="language-picker-title">${{window.__galaxsee_i18n.t('displayLanguage')}}</span>
      <button class="p-1 text-slate-400 hover:text-white text-xl leading-none cursor-pointer" aria-label="Close" onclick="document.getElementById('galaxsee-language-modal').remove()">&times;</button>
    `;
    card.appendChild(header);

    const list = document.createElement('div');
    list.className = 'lang-options-list';

    LANGUAGES.forEach(l => {{
      const isSel = l.code === currentLang;
      const btn = document.createElement('button');
      btn.className = `lang-option-btn ${{isSel ? 'selected' : ''}}`;
      btn.innerHTML = `
        <div class="lang-option-left">
          <span class="lang-flag">${{l.flag}}</span>
          <span class="lang-name">${{l.name}}</span>
        </div>
        <span class="lang-check">${{isSel ? '✓' : ''}}</span>
      `;
      btn.onclick = () => {{
        window.__galaxsee_i18n.setLanguage(l.code);
        overlay.remove();
        window.location.reload();
      }};
      list.appendChild(btn);
    }});

    card.appendChild(list);
    overlay.appendChild(card);
    document.body.appendChild(overlay);
  }};
}})();
"""
        code = i18n_engine_code + "\n" + code
        print("[2] Injected Full Multilingual (i18n) Engine with 7 languages & modal picker")

    # -------------------------------------------------------------
    # 3. Context Menu Translations
    # -------------------------------------------------------------
    # Update openPhotoContextMenu labels to use window.__galaxsee_i18n.t()
    target_menu_copy = "label: 'Copy Photo to Clipboard',"
    repl_menu_copy = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('copyClipboard') : 'Copy Photo to Clipboard'),"
    if target_menu_copy in code:
        code = code.replace(target_menu_copy, repl_menu_copy, 1)

    target_menu_fs = "label: 'Open / View Fullscreen',"
    repl_menu_fs = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('openFullscreen') : 'Open / View Fullscreen'),"
    if target_menu_fs in code:
        code = code.replace(target_menu_fs, repl_menu_fs, 1)

    target_menu_fav = "label: photo.isFavorite ? 'Remove from Favorites' : 'Add to Favorites',"
    repl_menu_fav = "label: photo.isFavorite ? (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('removeFavorite') : 'Remove from Favorites') : (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('addFavorite') : 'Add to Favorites'),"
    if target_menu_fav in code:
        code = code.replace(target_menu_fav, repl_menu_fav, 1)

    target_menu_svg = "label: 'Convert to SVG Vector',"
    repl_menu_svg = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('convertToSvg') : 'Convert to SVG Vector'),"
    if target_menu_svg in code:
        code = code.replace(target_menu_svg, repl_menu_svg, 1)

    target_menu_edit = "label: 'Edit Photo',"
    repl_menu_edit = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('editPhoto') : 'Edit Photo'),"
    if target_menu_edit in code:
        code = code.replace(target_menu_edit, repl_menu_edit, 1)

    target_menu_info = "label: 'Photo Info & EXIF',"
    repl_menu_info = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('photoInfo') : 'Photo Info & EXIF'),"
    if target_menu_info in code:
        code = code.replace(target_menu_info, repl_menu_info, 1)

    target_menu_app_wp = "label: 'Set as App Wallpaper',"
    repl_menu_app_wp = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('setAppWallpaper') : 'Set as App Wallpaper'),"
    if target_menu_app_wp in code:
        code = code.replace(target_menu_app_wp, repl_menu_app_wp, 1)

    target_menu_desk_wp = "label: 'Set photo as desktop wallpaper',"
    repl_menu_desk_wp = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('setDesktopWallpaper') : 'Set photo as desktop wallpaper'),"
    if target_menu_desk_wp in code:
        code = code.replace(target_menu_desk_wp, repl_menu_desk_wp, 1)

    target_menu_trash = "label: 'Move to Trash',"
    repl_menu_trash = "label: (window.__galaxsee_i18n ? window.__galaxsee_i18n.t('moveToTrash') : 'Move to Trash'),"
    if target_menu_trash in code:
        code = code.replace(target_menu_trash, repl_menu_trash, 1)

    print("[3] Wrapped Photo Context Menu labels in i18n translations")

    # -------------------------------------------------------------
    # 4. Multi-Tab State Isolation Sandbox
    # -------------------------------------------------------------
    # In App: Track active tab in window.__galaxsee_active_tab_id
    target_app_tab = 'd.find(W=>W.id===h)||d[0],w=g.viewMode,'
    repl_app_tab = 'd.find(W=>W.id===h)||d[0];if(typeof window<"u"){window.__galaxsee_active_tab_id=h;}const w=g.viewMode,'
    if target_app_tab in code:
        code = code.replace(target_app_tab, repl_app_tab, 1)
        print("[4a] Bound window.__galaxsee_active_tab_id to current tab ID")

    # In App: onCloseTab cleanup (ma)
    target_ma = 'ma=W=>{if(d.length<=1)return;const Ne=d.findIndex(tt=>tt.id===W),He=d.filter(tt=>tt.id!==W);'
    repl_ma = 'ma=W=>{if(d.length<=1)return;if(typeof window<"u"&&window.__galaxsee_tab_state){delete window.__galaxsee_tab_state[W];}const Ne=d.findIndex(tt=>tt.id===W),He=d.filter(tt=>tt.id!==W);'
    if target_ma in code:
        code = code.replace(target_ma, repl_ma, 1)
        print("[4b] Added per-tab state cleanup on tab close (prevents leaks for unlimited tabs)")

    # In ov: Grid scroll tracking & photo click scoped by tab ID
    target_ov_scroll = 'if(typeof window<"u"&&!window.__galaxsee_is_restoring_scroll){if($e.currentTarget.scrollTop>0)window.__galaxsee_last_grid_scroll=$e.currentTarget.scrollTop;}'
    repl_ov_scroll = (
        'if(typeof window<"u"&&!window.__galaxsee_is_restoring_scroll){'
        'const _tabId=window.__galaxsee_active_tab_id||"default_tab";'
        'if(!window.__galaxsee_tab_state)window.__galaxsee_tab_state={};'
        'if(!window.__galaxsee_tab_state[_tabId])window.__galaxsee_tab_state[_tabId]={};'
        'if($e.currentTarget.scrollTop>0)window.__galaxsee_tab_state[_tabId].scrollTop=$e.currentTarget.scrollTop;'
        '}'
    )
    if target_ov_scroll in code:
        code = code.replace(target_ov_scroll, repl_ov_scroll, 1)
        print("[4c] Scoped ov onScroll memory strictly to active tab ID")

    target_ov_limit = '[renderLimit,setRenderLimit]=M.useState(()=>{if(typeof window<"u"&&window.__galaxsee_last_viewed_photo_id&&Ue){const pIdx=Ue.findIndex(p=>p.id===window.__galaxsee_last_viewed_photo_id);if(pIdx>=60)return Math.min(100000,pIdx+40);}return 60;});'
    repl_ov_limit = '[renderLimit,setRenderLimit]=M.useState(()=>{if(typeof window<"u"&&Ue){const _tabId=window.__galaxsee_active_tab_id||"default_tab";const _pId=(window.__galaxsee_tab_state&&window.__galaxsee_tab_state[_tabId]&&window.__galaxsee_tab_state[_tabId].lastPhotoId)||window.__galaxsee_last_viewed_photo_id;if(_pId){const pIdx=Ue.findIndex(p=>p.id===_pId);if(pIdx>=60)return Math.min(100000,pIdx+40);}}return 60;});'
    if target_ov_limit in code:
        code = code.replace(target_ov_limit, repl_ov_limit, 1)
        print("[4l] Scoped ov initial renderLimit to active tab photo anchor")

    target_ov_click1 = 'if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=Re.id;if(R.current&&R.current.scrollTop>0)window.__galaxsee_last_grid_scroll=R.current.scrollTop;window.__galaxsee_is_restoring_scroll=true;}m(Re);'
    repl_ov_click1 = (
        'if(typeof window<"u"){'
        'const _tabId=window.__galaxsee_active_tab_id||"default_tab";'
        'if(!window.__galaxsee_tab_state)window.__galaxsee_tab_state={};'
        'if(!window.__galaxsee_tab_state[_tabId])window.__galaxsee_tab_state[_tabId]={};'
        'window.__galaxsee_tab_state[_tabId].lastPhotoId=Re.id;'
        'window.__galaxsee_last_viewed_photo_id=Re.id;'
        'if(R.current&&R.current.scrollTop>0)window.__galaxsee_tab_state[_tabId].scrollTop=R.current.scrollTop;'
        'window.__galaxsee_is_restoring_scroll=true;'
        '}m(Re);'
    )
    if target_ov_click1 in code:
        code = code.replace(target_ov_click1, repl_ov_click1, 1)
        print("[4d] Scoped ov single-click photo selection strictly to active tab ID")

    target_ov_click2 = 'onDoubleClick:$e=>{$e.stopPropagation();if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=Re.id;if(R.current&&R.current.scrollTop>0)window.__galaxsee_last_grid_scroll=R.current.scrollTop;window.__galaxsee_is_restoring_scroll=true;}m(Re);},'
    repl_ov_click2 = (
        'onDoubleClick:$e=>{$e.stopPropagation();if(typeof window<"u"){'
        'const _tabId=window.__galaxsee_active_tab_id||"default_tab";'
        'if(!window.__galaxsee_tab_state)window.__galaxsee_tab_state={};'
        'if(!window.__galaxsee_tab_state[_tabId])window.__galaxsee_tab_state[_tabId]={};'
        'window.__galaxsee_tab_state[_tabId].lastPhotoId=Re.id;'
        'window.__galaxsee_last_viewed_photo_id=Re.id;'
        'if(R.current&&R.current.scrollTop>0)window.__galaxsee_tab_state[_tabId].scrollTop=R.current.scrollTop;'
        'window.__galaxsee_is_restoring_scroll=true;'
        '}m(Re);},'
    )
    if target_ov_click2 in code:
        code = code.replace(target_ov_click2, repl_ov_click2, 1)
        print("[4m] Scoped ov double-click photo selection strictly to active tab ID")

    # In ov: Restoration hook reading strictly active tab state
    target_ov_targets = 'const targetScroll=typeof window<"u"?window.__galaxsee_last_grid_scroll:null;const targetId=typeof window<"u"?window.__galaxsee_last_viewed_photo_id:null;'
    repl_ov_targets = (
        'const _tabId=(typeof window<"u"&&window.__galaxsee_active_tab_id)||"default_tab";'
        'const _tabState=(typeof window<"u"&&window.__galaxsee_tab_state&&window.__galaxsee_tab_state[_tabId])||{};'
        'const targetScroll=_tabState.scrollTop||null;'
        'const targetId=_tabState.lastPhotoId||null;'
    )
    if target_ov_targets in code:
        code = code.replace(target_ov_targets, repl_ov_targets, 1)
        print("[4e] Scoped ov targetScroll and targetId strictly to active tab state")

    # In ov: doRestore smooth restoration
    target_ov_restore = 'const doRestore=()=>{const scroller=R.current;if(!scroller)return false;if(typeof targetScroll==="number"&&targetScroll>0&&scroller.scrollTop===0){scroller.scrollTop=targetScroll;}if(targetId&&nt.current&&nt.current.has(targetId)){const el=nt.current.get(targetId);if(el){const sr=scroller.getBoundingClientRect();const er=el.getBoundingClientRect();if(er.top<sr.top||er.bottom>sr.bottom){const diff=(er.top-sr.top)-(sr.height/2-er.height/2);scroller.scrollTop+=diff;}}}else if(typeof targetScroll==="number"&&targetScroll>0){scroller.scrollTop=targetScroll;}return true;};doRestore();const af=requestAnimationFrame(()=>{doRestore();const t1=setTimeout(()=>{doRestore();window.__galaxsee_is_restoring_scroll=false;},120);return()=>clearTimeout(t1);});'
    repl_ov_restore = (
        'const doRestore=(smooth=false)=>{const scroller=R.current;if(!scroller)return false;'
        'if(typeof targetScroll==="number"&&targetScroll>0&&scroller.scrollTop===0){scroller.scrollTop=targetScroll;}'
        'if(targetId&&nt.current&&nt.current.has(targetId)){'
        'const el=nt.current.get(targetId);'
        'if(el){'
        'const sr=scroller.getBoundingClientRect();const er=el.getBoundingClientRect();'
        'const diff=(er.top-sr.top)-(sr.height/2-er.height/2);'
        'if(Math.abs(diff)>16){'
        'if(smooth){scroller.scrollTo({top:Math.max(0,scroller.scrollTop+diff),behavior:"smooth"});}'
        'else{scroller.scrollTop+=diff;}'
        '}'
        '}'
        '}else if(typeof targetScroll==="number"&&targetScroll>0&&Math.abs(scroller.scrollTop-targetScroll)>16){'
        'if(smooth){scroller.scrollTo({top:targetScroll,behavior:"smooth"});}else{scroller.scrollTop=targetScroll;}'
        '}'
        'return true;};'
        'doRestore(false);'
        'const af=requestAnimationFrame(()=>{const t1=setTimeout(()=>{doRestore(true);const t2=setTimeout(()=>{window.__galaxsee_is_restoring_scroll=false;},250);},80);return()=>clearTimeout(t1);});'
    )
    if target_ov_restore in code:
        code = code.replace(target_ov_restore, repl_ov_restore, 1)
        print("[4f] Patched ov doRestore with instant scroll anchoring + smooth centering")

    target_ov_fade = 'className:`flex-1 overflow-y-auto px-4 md:px-8 py-6 relative select-none scrollbar-thin scrollbar-thumb-slate-700/50 transition-colors ${Y?"bg-blue-950/30 ring-4 ring-blue-500/40 ring-inset":""}`'
    repl_ov_fade = 'className:`flex-1 overflow-y-auto px-4 md:px-8 py-6 relative select-none scrollbar-thin scrollbar-thumb-slate-700/50 transition-colors animate-fade-in ${Y?"bg-blue-950/30 ring-4 ring-blue-500/40 ring-inset":""}`'
    if target_ov_fade in code:
        code = code.replace(target_ov_fade, repl_ov_fade, 1)
        print("[4g] Added animate-fade-in to grid scroller for smooth entrance")

    # In cv: smooth back transition & update tab lastPhotoId
    target_cv_state = 'cv=({photo:d,allPhotos:u,onBack:h,onGoFullScreen:m,onOpenInNewTab:g,onSelectPhoto:w,onToggleFavorite:y,onOpenEditor:k,onOpenInfo:_,onSetAsWallpaper:x,onDeletePhoto:T,theme:N="dark"})=>{const A=N==="light"||N==="light_galaxsee"||N==="blue_sky",[D,I]=M.useState(1),'
    repl_cv_state = (
        'cv=({photo:d,allPhotos:u,onBack:h,onGoFullScreen:m,onOpenInNewTab:g,onSelectPhoto:w,onToggleFavorite:y,onOpenEditor:k,onOpenInfo:_,onSetAsWallpaper:x,onDeletePhoto:T,theme:N="dark"})=>{\n'
        'if(typeof window<"u"){\n'
        '  const _tabId=window.__galaxsee_active_tab_id||"default_tab";\n'
        '  if(!window.__galaxsee_tab_state)window.__galaxsee_tab_state={};\n'
        '  if(!window.__galaxsee_tab_state[_tabId])window.__galaxsee_tab_state[_tabId]={};\n'
        '  window.__galaxsee_tab_state[_tabId].lastPhotoId=d.id;\n'
        '}\n'
        'const A=N==="light"||N==="light_galaxsee"||N==="blue_sky",[_exiting,_setExiting]=M.useState(!1),_smoothBack=()=>{_setExiting(!0);setTimeout(()=>h(),200);},[D,I]=M.useState(1),'
    )
    if target_cv_state in code:
        code = code.replace(target_cv_state, repl_cv_state, 1)
        print("[4h] Injected per-tab photo tracking and _smoothBack() into cv")

    # cv: Back to Grid button
    target_cv_back = 'a.jsxs("button",{title:"Back to Grid","aria-label":"Back to Grid",onClick:()=>{we.playKeypad(),h()},className:`galaxsee-back-btn flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${A?"bg-slate-200/70 hover:bg-slate-300/70 text-slate-700":"bg-white/10 hover:bg-white/20 text-slate-200"}`,children:[a.jsx(Xx,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"hidden sm:inline",children:"Back to Grid"})]})'
    repl_cv_back = 'a.jsxs("button",{title:(window.__galaxsee_i18n?window.__galaxsee_i18n.t("backToGrid"):"Back to Grid"),"aria-label":"Back to Grid",onClick:()=>{we.playKeypad(),_smoothBack()},className:`galaxsee-back-btn flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-lg text-xs font-bold transition-colors flex-shrink-0 ${A?"bg-slate-200/70 hover:bg-slate-300/70 text-slate-700":"bg-white/10 hover:bg-white/20 text-slate-200"}`,children:[a.jsx(Xx,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"hidden sm:inline",children:(window.__galaxsee_i18n?window.__galaxsee_i18n.t("backToGrid"):"Back to Grid")})]})'
    if target_cv_back in code:
        code = code.replace(target_cv_back, repl_cv_back, 1)
        print("[4i] Wired cv Back to Grid button to _smoothBack() with i18n label")

    # cv: Escape key
    target_cv_esc = 'oe.key==="Escape"?h():'
    repl_cv_esc = 'oe.key==="Escape"?_smoothBack():'
    if target_cv_esc in code:
        code = code.replace(target_cv_esc, repl_cv_esc, 1)
        print("[4j] Wired cv Escape key to _smoothBack()")

    # cv: Root div smooth exit transition
    idx_cv_def = code.find('cv=({photo:d')
    if idx_cv_def != -1:
        idx_cv_root = code.find('flex-1 flex flex-col overflow-hidden', idx_cv_def)
        if idx_cv_root != -1:
            start_cv_root = code.rfind('a.jsxs("div",{className:`', idx_cv_def, idx_cv_root)
            end_cv_root = code.find('text-slate-100"}`', idx_cv_root)
            if start_cv_root != -1 and end_cv_root != -1:
                end_cv_root += len('text-slate-100"}`')
                repl_cv_root = 'a.jsxs("div",{className:`flex-1 flex flex-col overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif] select-none transition-all duration-200 ease-out ${_exiting?"opacity-0 scale-[0.98] pointer-events-none":"opacity-100 scale-100"} ${A?"text-slate-800":"text-slate-100"}`'
                code = code[:start_cv_root] + repl_cv_root + code[end_cv_root:]
                print("[4k] Added smooth 200ms exit fade & scale transition to cv root container")

    target_cv_id_effect = 'P({x:0,y:0}),H(0);if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=d.id;}},[d.id]);'
    repl_cv_id_effect = (
        'P({x:0,y:0}),H(0);if(typeof window<"u"){'
        'const _tabId=window.__galaxsee_active_tab_id||"default_tab";'
        'if(!window.__galaxsee_tab_state)window.__galaxsee_tab_state={};'
        'if(!window.__galaxsee_tab_state[_tabId])window.__galaxsee_tab_state[_tabId]={};'
        'window.__galaxsee_tab_state[_tabId].lastPhotoId=d.id;'
        'window.__galaxsee_last_viewed_photo_id=d.id;'
        '}},[d.id]);'
    )
    if target_cv_id_effect in code:
        code = code.replace(target_cv_id_effect, repl_cv_id_effect, 1)
        print("[4n] Scoped cv photo change effect to active tab photo anchor")

    target_folder_click = 'onClick: () => { if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=V.id;window.__galaxsee_active_folder=T;} u(V); },'
    repl_folder_click = (
        'onClick: () => { if(typeof window<"u"){'
        'const _t=window.__galaxsee_active_tab_id||"default_tab";'
        'if(!window.__galaxsee_tab_state)window.__galaxsee_tab_state={};'
        'if(!window.__galaxsee_tab_state[_t])window.__galaxsee_tab_state[_t]={};'
        'window.__galaxsee_tab_state[_t].lastPhotoId=V.id;'
        'window.__galaxsee_last_viewed_photo_id=V.id;'
        'window.__galaxsee_active_folder=T;'
        '} u(V); },'
    )
    if target_folder_click in code:
        code = code.replace(target_folder_click, repl_folder_click, 1)
        print("[4o] Scoped Folder view photo click strictly to active tab photo anchor")

    # -------------------------------------------------------------
    # 5. rv Fullscreen 5s Fade & Tap-to-Wake
    # -------------------------------------------------------------
    target_J = 'const J=()=>{Ce(!0),Fe.current&&window.clearTimeout(Fe.current),Fe.current=window.setTimeout(()=>{I===1&&!ge&&Ce(!1)},3500)};'
    repl_J = 'const J=()=>{Ce(!0),Fe.current&&window.clearTimeout(Fe.current),Fe.current=window.setTimeout(()=>{!ge&&Ce(!1)},5000)};'
    if target_J in code:
        code = code.replace(target_J, repl_J, 1)
        print("[5a] Updated rv inactivity timer to 5000ms (5 seconds)")

    target_listeners = 'M.useEffect(()=>(window.addEventListener("mousemove",J),window.addEventListener("pointermove",J),window.addEventListener("touchstart",J),window.addEventListener("touchmove",J),J(),()=>{window.removeEventListener("mousemove",J),window.removeEventListener("pointermove",J),window.removeEventListener("touchstart",J),window.removeEventListener("touchmove",J),Fe.current&&window.clearTimeout(Fe.current)}),[I,ge]);'
    repl_listeners = 'M.useEffect(()=>(window.addEventListener("mousemove",J),window.addEventListener("pointermove",J),window.addEventListener("pointerdown",J),window.addEventListener("touchstart",J),window.addEventListener("touchmove",J),J(),()=>{window.removeEventListener("mousemove",J),window.removeEventListener("pointermove",J),window.removeEventListener("pointerdown",J),window.removeEventListener("touchstart",J),window.removeEventListener("touchmove",J),Fe.current&&window.clearTimeout(Fe.current)}),[ge]);'
    if target_listeners in code:
        code = code.replace(target_listeners, repl_listeners, 1)
        print("[5b] Attached pointerdown listener to rv window for instant wake on tap")

    target_la = 'if(Date.now()-qe.current.startTime<280){const $e=Date.now();$e-qe.current.lastTapTime<300&&Be(qe.current.startTouchPos.x,qe.current.startTouchPos.y);qe.current.lastTapTime=$e;}'
    repl_la = 'if(Date.now()-qe.current.startTime<280){const $e=Date.now();if($e-qe.current.lastTapTime<300){Be(qe.current.startTouchPos.x,qe.current.startTouchPos.y);}else{Ce(v=>!v);J();}qe.current.lastTapTime=$e;}'
    if target_la in code:
        code = code.replace(target_la, repl_la, 1)
        print("[5c] Added single-tap toggle/wake to rv touch handler (la)")

    target_rv_container = 'onDoubleClick:e=>{Be(e.clientX,e.clientY)},onContextMenu:e=>{e.preventDefault();e.stopPropagation();openPhotoContextMenu(e,d,{onOpen:()=>{},onToggleFavorite:g,onEdit:w,onInfo:y,onWallpaper:A,onDelete:k=>k&&k(d.id)})},className:"relative flex-1 w-full h-full flex items-center justify-center overflow-hidden cursor-grab active:cursor-grabbing touch-none select-none",children:['
    repl_rv_container = 'onClick:e=>{if(e.target===e.currentTarget||e.target.tagName==="IMG"||e.target.tagName==="VIDEO"){Ce(v=>!v);J();}},onDoubleClick:e=>{Be(e.clientX,e.clientY)},onContextMenu:e=>{e.preventDefault();e.stopPropagation();openPhotoContextMenu(e,d,{onOpen:()=>{},onToggleFavorite:g,onEdit:w,onInfo:y,onWallpaper:A,onDelete:k=>k&&k(d.id)})},className:"relative flex-1 w-full h-full flex items-center justify-center overflow-hidden cursor-grab active:cursor-grabbing touch-none select-none",children:['
    if target_rv_container in code:
        code = code.replace(target_rv_container, repl_rv_container, 1)
        print("[5d] Added onClick toggle/wake to rv main container")

    target_rv_hdr = 'a.jsxs("div",{className:`w-full z-30 px-6 py-4 flex items-center justify-between bg-gradient-to-b from-black/80 via-black/40 to-transparent transition-opacity duration-300 ${V?"opacity-100":"opacity-0 pointer-events-none"}`,children:['
    repl_rv_hdr = 'a.jsxs("div",{className:`w-full z-30 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between bg-gradient-to-b from-black/80 via-black/40 to-transparent transition-all duration-700 ease-in-out ${V?"opacity-100 translate-y-0":"opacity-0 -translate-y-4 pointer-events-none"}`,children:['
    if target_rv_hdr in code:
        code = code.replace(target_rv_hdr, repl_rv_hdr, 1)
        print("[5e] Updated rv header transition to 700ms ease-in-out with translateY")

    target_rv_left = 'className:`absolute left-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-200 ${V?"opacity-100 translate-x-0":"opacity-0 -translate-x-4 pointer-events-none"}`'
    repl_rv_left = 'className:`absolute left-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-700 ease-in-out ${V?"opacity-100 translate-x-0":"opacity-0 -translate-x-4 pointer-events-none"}`'
    if target_rv_left in code:
        code = code.replace(target_rv_left, repl_rv_left, 1)
        print("[5f] Updated rv left nav button transition to 700ms ease-in-out")

    target_rv_right = 'className:`absolute right-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-200 ${V?"opacity-100 translate-x-0":"opacity-0 translate-x-4 pointer-events-none"}`'
    repl_rv_right = 'className:`absolute right-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-700 ease-in-out ${V?"opacity-100 translate-x-0":"opacity-0 translate-x-4 pointer-events-none"}`'
    if target_rv_right in code:
        code = code.replace(target_rv_right, repl_rv_right, 1)
        print("[5g] Updated rv right nav button transition to 700ms ease-in-out")

    target_rv_burst = 'className:`z-30 mb-2 px-4 py-2 bg-black/60 backdrop-blur-xl rounded-2xl border border-white/10 flex items-center gap-2 self-center transition-opacity duration-300 ${V?"opacity-100":"opacity-0 pointer-events-none"}`'
    repl_rv_burst = 'className:`z-30 mb-2 px-4 py-2 bg-black/60 backdrop-blur-xl rounded-2xl border border-white/10 flex items-center gap-2 self-center transition-all duration-700 ease-in-out ${V?"opacity-100 translate-y-0":"opacity-0 translate-y-4 pointer-events-none"}`'
    if target_rv_burst in code:
        code = code.replace(target_rv_burst, repl_rv_burst, 1)
        print("[5h] Updated rv burst strip transition to 700ms ease-in-out")

    target_rv_bottom = 'className:`w-full z-30 px-4 md:px-8 py-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-center justify-between transition-opacity duration-300 ${V?"opacity-100":"opacity-0 pointer-events-none"}`'
    repl_rv_bottom = 'className:`w-full z-30 px-4 md:px-8 py-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-center justify-between transition-all duration-700 ease-in-out ${V?"opacity-100 translate-y-0":"opacity-0 translate-y-4 pointer-events-none"}`'
    if target_rv_bottom in code:
        code = code.replace(target_rv_bottom, repl_rv_bottom, 1)
        print("[5i] Updated rv bottom filmstrip bar transition to 700ms ease-in-out")

    # -------------------------------------------------------------
    # 6. Display Language Card in Settings (W1)
    # -------------------------------------------------------------
    target_settings_top = 'a.jsxs("div",{className:"max-w-4xl mx-auto space-y-8 pb-16",children:[a.jsxs("div",{className:"flex items-center justify-between",children:[a.jsxs("div",{className:"flex items-center gap-3",children:[a.jsx(ch,{className:`w-6 h-6 ${O?"text-slate-600":"text-slate-300"}`}),a.jsx("h1",{className:`text-2xl font-bold tracking-tight ${O?"text-slate-900":"text-white"}`,children:"Galaxsee Pro Settings"}),null]}),a.jsx("span",{className:"text-xs font-mono text-slate-400",children:"Studio Edition'
    repl_settings_top = (
        'a.jsxs("div",{className:"max-w-4xl mx-auto space-y-8 pb-16",children:['
        'a.jsxs("div",{className:"p-5 sm:p-6 rounded-2xl bg-slate-950/80 border-2 border-sky-500/40 shadow-xl shadow-sky-500/10 space-y-4",children:['
        'a.jsxs("div",{className:"flex items-center justify-between border-b border-white/10 pb-3",children:['
        'a.jsxs("div",{className:"flex items-center gap-2.5",children:[a.jsx("span",{className:"text-xl",children:"🌐"}),a.jsx("span",{className:"text-xs font-black uppercase tracking-widest text-sky-400 font-mono",children:(window.__galaxsee_i18n?window.__galaxsee_i18n.t("displayLanguage"):"DISPLAY LANGUAGE")})]}),'
        'a.jsx("button",{type:"button",onClick:()=>window.openGalaxseeLanguagePicker&&window.openGalaxseeLanguagePicker(),className:"text-xs font-bold text-sky-400 hover:text-sky-300 px-3 py-1.5 rounded-full bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 transition-all cursor-pointer",children:"Change Language ▾"})'
        ']}),'
        'a.jsx("div",{className:"grid grid-cols-1 sm:grid-cols-2 gap-2.5",children:(window.__galaxsee_i18n?window.__galaxsee_i18n.languages:[]).map(l=>{'
        'const isSel=window.__galaxsee_i18n&&window.__galaxsee_i18n.currentLanguage===l.code;'
        'return a.jsxs("button",{key:l.code,type:"button",onClick:()=>{window.__galaxsee_i18n&&window.__galaxsee_i18n.setLanguage(l.code);window.location.reload();},className:`lang-option-btn ${isSel?"selected":""}`,children:['
        'a.jsxs("div",{className:"lang-option-left",children:[a.jsx("span",{className:"lang-flag",children:l.flag}),a.jsx("span",{className:"lang-name",children:l.name})]}),'
        'a.jsx("span",{className:"lang-check",children:isSel?"✓":""})'
        ']});})})'
        ']}),'
        'a.jsxs("div",{className:"flex items-center justify-between",children:[a.jsxs("div",{className:"flex items-center gap-3",children:[a.jsx(ch,{className:`w-6 h-6 ${O?"text-slate-600":"text-slate-300"}`}),a.jsx("h1",{className:`text-2xl font-bold tracking-tight ${O?"text-slate-900":"text-white"}`,children:"Galaxsee Pro Settings"}),null]}),a.jsx("span",{className:"text-xs font-mono text-slate-400",children:"Studio Edition'
    )
    if target_settings_top in code:
        code = code.replace(target_settings_top, repl_settings_top, 1)
        print("[6] Added DISPLAY LANGUAGE card to Settings (W1) matching media_1791935491031.png")

    # -------------------------------------------------------------
    # 7. Add Language Pill / Selector to Top Bar (U1)
    # -------------------------------------------------------------
    target_top_settings = 'title:"Settings","data-tour":"settings-button"'
    repl_top_settings = 'title:"Settings","data-tour":"settings-button",onClick:W'
    # In U1, there is a settings button. We can add a language selector button right before or after it:
    target_u1_gear = 'a.jsx("button",{onClick:W,className:`p-2 rounded-lg text-slate-400 hover:text-white`'
    # Let us check how settings button is rendered in U1
    idx_u1_gear = code.find('title:"Settings","data-tour":"settings-button"')
    if idx_u1_gear != -1:
        btn_start = code.rfind('a.jsx("button",{', 0, idx_u1_gear)
        btn_end = code.find('})', idx_u1_gear) + 2
        lang_btn = (
            'a.jsx("button",{type:"button",onClick:()=>window.openGalaxseeLanguagePicker&&window.openGalaxseeLanguagePicker(),className:"p-1.5 sm:px-2.5 sm:py-1 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 hover:text-sky-300 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer",title:(window.__galaxsee_i18n?window.__galaxsee_i18n.t("displayLanguage"):"Display Language"),children:[a.jsx("span",{className:"text-sm",children:"🌐"}),a.jsx("span",{className:"hidden sm:inline uppercase font-mono text-[11px]",children:(window.__galaxsee_i18n?(window.__galaxsee_i18n.languages.find(l=>l.code===window.__galaxsee_i18n.currentLanguage)||{}).flag||"EN":"EN")})]}),'
        )
        code = code[:btn_start] + lang_btn + code[btn_start:]
        print("[7] Added Global Language Selector Pill to Top Bar (U1)")

    # -------------------------------------------------------------
    # Syntax Validation Before Write
    # -------------------------------------------------------------
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(code)
        tname = tf.name

    res = subprocess.run(["node", "-c", tname], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FATAL: Syntax validation failed for proposed patch to {js_file}!")
        print(res.stderr)
        os.remove(tname)
        sys.exit(1)
    else:
        print(f"SYNTAX VALIDATION PASSED (0 errors) for {js_file}!")
        os.remove(tname)

    # Write patched code
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(code)

    new_len = len(code)
    print(f"Wrote clean patch to {js_file}: {orig_len} -> {new_len} ({new_len - orig_len:+d} bytes)")

if __name__ == "__main__":
    css_targets = [
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-CMUT5y5_.css",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/android_build/assets/assets/index-CMUT5y5_.css",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-CMUT5y5_.css",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build/assets/assets/index-CMUT5y5_.css",
    ]
    for c in css_targets:
        patch_css(c)

    js_targets = [
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/android_build/assets/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build/assets/assets/index-DpfNch1h.js",
    ]
    for j in js_targets:
        patch_js(j)

    print("\nALL CSS AND JS TARGETS PATCHED AND VALIDATED WITH 0 ERRORS!")
