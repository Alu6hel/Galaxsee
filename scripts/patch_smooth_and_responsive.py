#!/usr/bin/env python3
import sys
import os
import subprocess

def patch_bundle(file_path):
    print(f"\n=======================================================")
    print(f"PATCHING: {file_path}")
    print(f"=======================================================")
    
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} does not exist, skipping.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)

    # -------------------------------------------------------------
    # 1. Tv: Remove Duplicate "Photo Location & Storage" Cards
    # -------------------------------------------------------------
    card_sig = 'a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5",'
    starts = []
    p = 0
    while True:
        idx = code.find(card_sig, p)
        if idx == -1:
            break
        starts.append(idx)
        p = idx + len(card_sig)

    if len(starts) == 4:
        next_sec = 'a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2",'
        idx_next = code.find(next_sec, starts[1])
        if idx_next != -1:
            code = code[:starts[1]] + code[idx_next:]
            print("[1] Successfully removed 3 duplicate Photo Location & Storage cards in Tv (now exactly 1)")
        else:
            print("[1] Warning: next_sec not found for Tv card dedup")
    elif len(starts) == 1:
        print("[1] Note: Tv cards already deduplicated (exactly 1 present)")
    else:
        print(f"[1] Note: Unexpected number of Tv cards ({len(starts)})")

    # -------------------------------------------------------------
    # 2. rv: Fullscreen 5-Second Inactivity Timer & Smooth Fade
    # -------------------------------------------------------------
    # Update inactivity timeout to 5000ms
    target_J = 'const J=()=>{Ce(!0),Fe.current&&window.clearTimeout(Fe.current),Fe.current=window.setTimeout(()=>{I===1&&!ge&&Ce(!1)},3500)};'
    repl_J = 'const J=()=>{Ce(!0),Fe.current&&window.clearTimeout(Fe.current),Fe.current=window.setTimeout(()=>{!ge&&Ce(!1)},5000)};'
    if target_J in code:
        code = code.replace(target_J, repl_J, 1)
        print("[2a] Updated rv inactivity timer to 5000ms (5 seconds)")
    else:
        print("[2a] Note: target_J not found or already patched")

    # Inactivity event listeners (including pointerdown for touch/tap)
    target_listeners = 'M.useEffect(()=>(window.addEventListener("mousemove",J),window.addEventListener("pointermove",J),window.addEventListener("touchstart",J),window.addEventListener("touchmove",J),J(),()=>{window.removeEventListener("mousemove",J),window.removeEventListener("pointermove",J),window.removeEventListener("touchstart",J),window.removeEventListener("touchmove",J),Fe.current&&window.clearTimeout(Fe.current)}),[I,ge]);'
    repl_listeners = 'M.useEffect(()=>(window.addEventListener("mousemove",J),window.addEventListener("pointermove",J),window.addEventListener("pointerdown",J),window.addEventListener("touchstart",J),window.addEventListener("touchmove",J),J(),()=>{window.removeEventListener("mousemove",J),window.removeEventListener("pointermove",J),window.removeEventListener("pointerdown",J),window.removeEventListener("touchstart",J),window.removeEventListener("touchmove",J),Fe.current&&window.clearTimeout(Fe.current)}),[ge]);'
    if target_listeners in code:
        code = code.replace(target_listeners, repl_listeners, 1)
        print("[2b] Attached pointerdown listener to rv window for instant wake on tap")
    else:
        print("[2b] Note: target_listeners not found or already patched")

    # Single tap in la handler to wake up / toggle menu
    target_la = 'if(Date.now()-qe.current.startTime<280){const $e=Date.now();$e-qe.current.lastTapTime<300&&Be(qe.current.startTouchPos.x,qe.current.startTouchPos.y);qe.current.lastTapTime=$e;}'
    repl_la = 'if(Date.now()-qe.current.startTime<280){const $e=Date.now();if($e-qe.current.lastTapTime<300){Be(qe.current.startTouchPos.x,qe.current.startTouchPos.y);}else{Ce(v=>!v);J();}qe.current.lastTapTime=$e;}'
    if target_la in code:
        code = code.replace(target_la, repl_la, 1)
        print("[2c] Added single-tap toggle/wake to rv touch handler (la)")
    else:
        print("[2c] Note: target_la not found or already patched")

    # Tap on photo container in rv to toggle/wake controls
    target_rv_container = 'onDoubleClick:e=>{Be(e.clientX,e.clientY)},onContextMenu:e=>{e.preventDefault();e.stopPropagation();openPhotoContextMenu(e,d,{onOpen:()=>{},onToggleFavorite:g,onEdit:w,onInfo:y,onWallpaper:A,onDelete:k=>k&&k(d.id)})},className:"relative flex-1 w-full h-full flex items-center justify-center overflow-hidden cursor-grab active:cursor-grabbing touch-none select-none",children:['
    repl_rv_container = 'onClick:e=>{if(e.target===e.currentTarget||e.target.tagName==="IMG"||e.target.tagName==="VIDEO"){Ce(v=>!v);J();}},onDoubleClick:e=>{Be(e.clientX,e.clientY)},onContextMenu:e=>{e.preventDefault();e.stopPropagation();openPhotoContextMenu(e,d,{onOpen:()=>{},onToggleFavorite:g,onEdit:w,onInfo:y,onWallpaper:A,onDelete:k=>k&&k(d.id)})},className:"relative flex-1 w-full h-full flex items-center justify-center overflow-hidden cursor-grab active:cursor-grabbing touch-none select-none",children:['
    if target_rv_container in code:
        code = code.replace(target_rv_container, repl_rv_container, 1)
        print("[2d] Added onClick toggle/wake to rv main container")
    else:
        print("[2d] Note: target_rv_container not found or already patched")

    # Smooth 700ms transitions for rv controls
    target_rv_hdr = 'a.jsxs("div",{className:`w-full z-30 px-6 py-4 flex items-center justify-between bg-gradient-to-b from-black/80 via-black/40 to-transparent transition-opacity duration-300 ${V?"opacity-100":"opacity-0 pointer-events-none"}`,children:['
    repl_rv_hdr = 'a.jsxs("div",{className:`w-full z-30 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between bg-gradient-to-b from-black/80 via-black/40 to-transparent transition-all duration-700 ease-in-out ${V?"opacity-100 translate-y-0":"opacity-0 -translate-y-4 pointer-events-none"}`,children:['
    if target_rv_hdr in code:
        code = code.replace(target_rv_hdr, repl_rv_hdr, 1)
        print("[2e] Updated rv header transition to 700ms ease-in-out with translateY")
    else:
        print("[2e] Note: target_rv_hdr not found or already patched")

    target_rv_left = 'className:`absolute left-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-200 ${V?"opacity-100 translate-x-0":"opacity-0 -translate-x-4 pointer-events-none"}`'
    repl_rv_left = 'className:`absolute left-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-700 ease-in-out ${V?"opacity-100 translate-x-0":"opacity-0 -translate-x-4 pointer-events-none"}`'
    if target_rv_left in code:
        code = code.replace(target_rv_left, repl_rv_left, 1)
        print("[2f] Updated rv left nav button transition to 700ms ease-in-out")
    else:
        print("[2f] Note: target_rv_left not found or already patched")

    target_rv_right = 'className:`absolute right-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-200 ${V?"opacity-100 translate-x-0":"opacity-0 translate-x-4 pointer-events-none"}`'
    repl_rv_right = 'className:`absolute right-4 z-30 p-3.5 rounded-full bg-black/50 hover:bg-black/90 hover:scale-110 active:scale-95 text-white/90 hover:text-white backdrop-blur-md border border-white/20 shadow-2xl transition-all duration-700 ease-in-out ${V?"opacity-100 translate-x-0":"opacity-0 translate-x-4 pointer-events-none"}`'
    if target_rv_right in code:
        code = code.replace(target_rv_right, repl_rv_right, 1)
        print("[2g] Updated rv right nav button transition to 700ms ease-in-out")
    else:
        print("[2g] Note: target_rv_right not found or already patched")

    target_rv_burst = 'className:`z-30 mb-2 px-4 py-2 bg-black/60 backdrop-blur-xl rounded-2xl border border-white/10 flex items-center gap-2 self-center transition-opacity duration-300 ${V?"opacity-100":"opacity-0 pointer-events-none"}`'
    repl_rv_burst = 'className:`z-30 mb-2 px-4 py-2 bg-black/60 backdrop-blur-xl rounded-2xl border border-white/10 flex items-center gap-2 self-center transition-all duration-700 ease-in-out ${V?"opacity-100 translate-y-0":"opacity-0 translate-y-4 pointer-events-none"}`'
    if target_rv_burst in code:
        code = code.replace(target_rv_burst, repl_rv_burst, 1)
        print("[2h] Updated rv burst strip transition to 700ms ease-in-out")
    else:
        print("[2h] Note: target_rv_burst not found or already patched")

    target_rv_bottom = 'className:`w-full z-30 px-4 md:px-8 py-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-center justify-between transition-opacity duration-300 ${V?"opacity-100":"opacity-0 pointer-events-none"}`'
    repl_rv_bottom = 'className:`w-full z-30 px-4 md:px-8 py-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-center justify-between transition-all duration-700 ease-in-out ${V?"opacity-100 translate-y-0":"opacity-0 translate-y-4 pointer-events-none"}`'
    if target_rv_bottom in code:
        code = code.replace(target_rv_bottom, repl_rv_bottom, 1)
        print("[2i] Updated rv bottom filmstrip bar transition to 700ms ease-in-out")
    else:
        print("[2i] Note: target_rv_bottom not found or already patched")

    # -------------------------------------------------------------
    # 3. Responsive Portrait Toolbars & Elimination of Overcrowding
    # -------------------------------------------------------------
    # rv top toolbar buttons
    idx_rv_fs = code.find('title:"Toggle Fullscreen"')
    if idx_rv_fs != -1:
        start_rv = code.rfind("rv=({", 0, idx_rv_fs)
        start_rv_tb = code.find('a.jsxs("div",{className:"flex items-center gap-2",children:[', start_rv)
        end_marker_rv = ']}),a.jsxs("div",{onMouseDown:xt'
        end_rv_tb = code.find(end_marker_rv, idx_rv_fs)
        if start_rv_tb != -1 and end_rv_tb != -1:
            repl_rv_tb = (
                'a.jsxs("div",{className:"flex items-center gap-1.5 sm:gap-2 flex-shrink-0",children:['
                'a.jsx("button",{onClick:()=>{Y(ye=>!ye),we.playKeypad()},className:`p-2.5 rounded-full backdrop-blur-md transition-all hidden md:flex ${z?"bg-emerald-500 text-black shadow-lg shadow-emerald-500/40":"bg-white/10 hover:bg-white/20 text-white"}`,title:"Toggle Focus Peaking (P)",children:a.jsx(Im,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>{le(ye=>!ye),we.playKeypad()},className:`p-2.5 rounded-full backdrop-blur-md transition-all hidden md:flex ${ee?"bg-amber-500 text-black shadow-lg shadow-amber-500/40":"bg-white/10 hover:bg-white/20 text-white"}`,title:"Toggle Exposure Zebras (Z)",children:a.jsx(Gm,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>De(ye=>!ye),className:`p-2.5 rounded-full backdrop-blur-md transition-all hidden sm:flex ${me?"bg-amber-400 text-black shadow-lg shadow-amber-400/40":"bg-white/10 hover:bg-white/20 text-white"}`,title:"Max Brightness Outdoor Mode",children:a.jsx(p1,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>je(ye=>!ye),className:`p-2.5 rounded-full backdrop-blur-md transition-all hidden sm:flex ${O?"bg-cyan-500 text-black shadow-lg shadow-cyan-500/40":"bg-white/10 hover:bg-white/20 text-white"}`,title:"Ultra HDR Wide Gamut Boost",children:a.jsx(Fa,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>x==null?void 0:x([d]),className:"p-2.5 rounded-full bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 backdrop-blur-md transition-all hidden md:flex",title:"Export as PDF Document",children:a.jsx(en,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>T==null?void 0:T([d]),className:"p-2.5 rounded-full bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 backdrop-blur-md transition-all hidden md:flex",title:"Convert Format & SVG Vector Tracing",children:a.jsx(ui,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>{we.playFavorite(!d.isFavorite),g(d.id)},className:`p-2.5 rounded-full backdrop-blur-md transition-all ${d.isFavorite?"bg-rose-500 text-white shadow-lg shadow-rose-500/30":"bg-white/10 hover:bg-white/20 text-white"}`,title:"Favorite (F)",children:a.jsx(hi,{className:`w-4 h-4 ${d.isFavorite?"fill-current":""}`})}),'
                'a.jsx("button",{onClick:()=>{we.playKeypad();copyPhotoToClipboard(d)},className:"p-2.5 rounded-full bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 hover:text-blue-200 border border-blue-500/30 backdrop-blur-md transition-all cursor-pointer hidden sm:flex",title:"Copy Photo to Clipboard (Ctrl+C)",children:a.jsx("svg",{className:"w-4 h-4",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor",strokeWidth:2,children:a.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",d:"M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"})})}),'
                'a.jsx("button",{onClick:()=>w(d),className:"p-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all",title:"Edit Photo (E)",children:a.jsx(Pc,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>_==null?void 0:_(d),className:"p-2.5 rounded-full bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 hover:text-emerald-200 border border-emerald-500/30 backdrop-blur-md transition-all hidden md:flex",title:"Resize & Compress Image",children:a.jsx(rr,{className:"w-4 h-4"})}),'
                '(d.isVideo||d.isLivePhoto)&&a.jsx("button",{onClick:()=>N==null?void 0:N(d),className:"p-2.5 rounded-full bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 hover:text-purple-200 border border-purple-500/30 backdrop-blur-md transition-all hidden md:flex",title:"Acoustic Mastering in Audio Studio",children:a.jsx(Fm,{className:"w-4 h-4"})}),'
                'A&&!d.isVideo&&a.jsx("button",{onClick:()=>{we.playFavorite(!0),A(d.url)},className:"p-2.5 rounded-full bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 hover:text-indigo-200 border border-indigo-500/30 backdrop-blur-md transition-all hidden lg:flex",title:"Set as App Background Wallpaper",children:a.jsx(kn,{className:"w-4 h-4"})}),'
                'k&&a.jsx("button",{onClick:()=>{we.playDelete(),k(d.id),h()},className:"p-2.5 rounded-full bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 hover:text-rose-200 border border-rose-500/30 backdrop-blur-md transition-all",title:"Move to Trash (Delete)",children:a.jsx(ka,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>y(d),className:"p-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all",title:"Info & EXIF (I)",children:a.jsx(nh,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:e=>{e.stopPropagation();openPhotoContextMenu(e,d,{onOpen:()=>{},onToggleFavorite:g,onEdit:w,onInfo:y,onWallpaper:A?()=>A(d.url):null,onDelete:()=>k&&k(d.id)})},className:"p-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all md:hidden",title:"More Options",children:a.jsx("svg",{className:"w-4 h-4",fill:"currentColor",viewBox:"0 0 20 20",children:a.jsx("path",{d:"M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"})})}),'
                'a.jsx("button",{onClick:Re,className:"p-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-all hidden sm:flex",title:"Toggle Fullscreen",children:se?a.jsx(oh,{className:"w-4 h-4"}):a.jsx(lh,{className:"w-4 h-4"})})'
                ']})'
            )
            code = code[:start_rv_tb] + repl_rv_tb + code[end_rv_tb:]
            print("[3a] Made rv top toolbar responsive with portrait-friendly collapsing and More Options (...) menu")
        else:
            print("[3a] Warning: Could not find rv toolbar bounds")
    else:
        print("[3a] Note: rv toolbar not found or already patched")

    # Title truncation & back button flex-shrink in rv header
    target_rv_left_title = 'a.jsxs("div",{className:"flex items-center gap-3",children:[a.jsx("button",{onClick:h,className:"p-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-colors",children:a.jsx(Xt,{className:"w-5 h-5"})}),a.jsxs("div",{className:"min-w-0 flex-1",children:[a.jsx("h2",{className:"text-sm font-bold text-white tracking-tight truncate max-w-[170px] xs:max-w-[260px] sm:max-w-md"'
    repl_rv_left_title = 'a.jsxs("div",{className:"flex items-center gap-2 sm:gap-3 min-w-0 mr-2",children:[a.jsx("button",{onClick:h,className:"p-2.5 rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-md transition-colors flex-shrink-0",children:a.jsx(Xt,{className:"w-5 h-5"})}),a.jsxs("div",{className:"min-w-0 flex-1",children:[a.jsx("h2",{className:"text-sm font-bold text-white tracking-tight truncate max-w-[110px] xs:max-w-[180px] sm:max-w-md"'
    if target_rv_left_title in code:
        code = code.replace(target_rv_left_title, repl_rv_left_title, 1)
        print("[3b] Added flex-shrink-0 to rv back button and mr-2 to title container")
    else:
        print("[3b] Note: target_rv_left_title not found or already patched")

    # cv: Exit state and smoothBack helper
    target_cv_state = 'cv=({photo:d,allPhotos:u,onBack:h,onGoFullScreen:m,onOpenInNewTab:g,onSelectPhoto:w,onToggleFavorite:y,onOpenEditor:k,onOpenInfo:_,onSetAsWallpaper:x,onDeletePhoto:T,theme:N="dark"})=>{const A=N==="light"||N==="light_galaxsee"||N==="blue_sky",[D,I]=M.useState(1),'
    repl_cv_state = 'cv=({photo:d,allPhotos:u,onBack:h,onGoFullScreen:m,onOpenInNewTab:g,onSelectPhoto:w,onToggleFavorite:y,onOpenEditor:k,onOpenInfo:_,onSetAsWallpaper:x,onDeletePhoto:T,theme:N="dark"})=>{const A=N==="light"||N==="light_galaxsee"||N==="blue_sky",[_exiting,_setExiting]=M.useState(!1),_smoothBack=()=>{_setExiting(!0);setTimeout(()=>h(),200);},[D,I]=M.useState(1),'
    if target_cv_state in code:
        code = code.replace(target_cv_state, repl_cv_state, 1)
        print("[3c] Injected _exiting state and _smoothBack() into cv")
    else:
        print("[3c] Note: target_cv_state not found or already patched")

    # cv: Back to Grid button
    target_cv_back = 'a.jsxs("button",{title:"Back to Grid","aria-label":"Back to Grid",onClick:()=>{we.playKeypad(),h()},className:`galaxsee-back-btn flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${A?"bg-slate-200/70 hover:bg-slate-300/70 text-slate-700":"bg-white/10 hover:bg-white/20 text-slate-200"}`,children:[a.jsx(Xx,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"hidden sm:inline",children:"Back to Grid"})]})'
    repl_cv_back = 'a.jsxs("button",{title:"Back to Grid","aria-label":"Back to Grid",onClick:()=>{we.playKeypad(),_smoothBack()},className:`galaxsee-back-btn flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-lg text-xs font-bold transition-colors flex-shrink-0 ${A?"bg-slate-200/70 hover:bg-slate-300/70 text-slate-700":"bg-white/10 hover:bg-white/20 text-slate-200"}`,children:[a.jsx(Xx,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"hidden sm:inline",children:"Back to Grid"})]})'
    if target_cv_back in code:
        code = code.replace(target_cv_back, repl_cv_back, 1)
        print("[3d] Wired cv Back to Grid button to _smoothBack()")
    else:
        print("[3d] Note: target_cv_back not found or already patched")

    # cv: Escape key
    target_cv_esc = 'oe.key==="Escape"?h():'
    repl_cv_esc = 'oe.key==="Escape"?_smoothBack():'
    if target_cv_esc in code:
        code = code.replace(target_cv_esc, repl_cv_esc, 1)
        print("[3e] Wired cv Escape key to _smoothBack()")
    else:
        print("[3e] Note: target_cv_esc not found or already patched")

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
                print("[3f] Added smooth 200ms exit fade & scale transition to cv root container")
            else:
                print("[3f] Warning: Could not locate bounds for cv root container")
    else:
        print("[3f] Warning: cv definition not found")

    # cv header left container spacing & title truncation
    target_cv_left = 'a.jsxs("div",{className:"flex items-center gap-3 min-w-0",children:['
    repl_cv_left = 'a.jsxs("div",{className:"flex items-center gap-2 sm:gap-3 min-w-0 mr-2",children:['
    if target_cv_left in code:
        code = code.replace(target_cv_left, repl_cv_left, 1)
        print("[3g-1] Added mr-2 to cv title container")
    else:
        print("[3g-1] Note: target_cv_left not found or already patched")

    target_cv_title = 'a.jsx("h2",{className:"text-xs font-bold truncate max-w-[170px] xs:max-w-[260px] sm:max-w-md",title:d.title'
    repl_cv_title = 'a.jsx("h2",{className:"text-xs font-bold truncate max-w-[110px] xs:max-w-[180px] sm:max-w-md",title:d.title'
    if target_cv_title in code:
        code = code.replace(target_cv_title, repl_cv_title, 1)
        print("[3g-2] Updated cv title max-width for compact portrait screens")
    else:
        print("[3g-2] Note: target_cv_title not found or already patched")

    # cv: Responsive toolbar buttons
    idx_cv_fs = code.find('title:"Fullscreen (F)"')
    if idx_cv_fs != -1:
        start_cv_tb = code.rfind('a.jsxs("div",{className:"flex items-center gap-1 sm:gap-2",children:[', 0, idx_cv_fs)
        end_marker_cv = ']}),a.jsxs("div",{onMouseDown:he'
        end_cv_tb = code.find(end_marker_cv, idx_cv_fs)
        if start_cv_tb != -1 and end_cv_tb != -1:
            repl_cv_tb = (
                'a.jsxs("div",{className:"flex items-center gap-1 sm:gap-2 flex-shrink-0",children:['
                'a.jsx("button",{onClick:()=>{me(B=>!B),we.playKeypad()},className:`p-2 rounded-lg text-xs font-bold transition-all hidden md:flex ${$?"bg-emerald-500 text-black shadow-md shadow-emerald-500/30":A?"hover:bg-slate-200 text-slate-600":"hover:bg-white/10 text-slate-300"}`,title:"Focus Peaking (P)",children:a.jsx(Im,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>{O(B=>!B),we.playKeypad()},className:`p-2 rounded-lg text-xs font-bold transition-all hidden md:flex ${De?"bg-amber-500 text-black shadow-md shadow-amber-500/30":A?"hover:bg-slate-200 text-slate-600":"hover:bg-white/10 text-slate-300"}`,title:"Exposure Zebras (Z)",children:a.jsx(Gm,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>{we.playFavorite(!d.isFavorite),y(d.id)},className:`p-2 rounded-lg text-xs font-bold transition-colors ${d.isFavorite?"text-rose-500":A?"hover:bg-slate-200 text-slate-600":"hover:bg-white/10 text-slate-300"}`,title:"Toggle Favorite",children:a.jsx(hi,{className:`w-4 h-4 ${d.isFavorite?"fill-current":""}`})}),'
                'a.jsx("button",{onClick:()=>{we.playKeypad();copyPhotoToClipboard(d)},className:`p-2 rounded-lg text-xs font-bold transition-colors hidden sm:flex ${A?"hover:bg-blue-100 text-blue-600":"hover:bg-blue-500/20 text-blue-400"}`,title:"Copy Photo to Clipboard (Ctrl+C)",children:a.jsx("svg",{className:"w-4 h-4",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor",strokeWidth:2,children:a.jsx("path",{strokeLinecap:"round",strokeLinejoin:"round",d:"M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"})})}),'
                'a.jsxs("button",{onClick:()=>{we.playKeypad(),g(d)},className:`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors hidden md:flex ${A?"bg-slate-200/60 hover:bg-slate-300/60 text-slate-700":"bg-white/10 hover:bg-white/20 text-slate-200"}`,title:"Open in New Tab",children:[a.jsx($u,{className:"w-3.5 h-3.5 text-blue-400"}),a.jsx("span",{className:"hidden md:inline",children:"Open in Tab"})]}),'
                'a.jsxs("button",{onClick:()=>k(d),className:`flex items-center gap-1 p-2 sm:px-2.5 sm:py-1.5 rounded-lg text-xs font-semibold transition-colors ${A?"bg-slate-200/60 hover:bg-slate-300/60 text-slate-700":"bg-white/10 hover:bg-white/20 text-slate-200"}`,title:"Edit Photo",children:[a.jsx(Pc,{className:"w-3.5 h-3.5 text-cyan-400"}),a.jsx("span",{className:"hidden md:inline",children:"Edit"})]}),'
                'x&&!d.isVideo&&a.jsxs("button",{onClick:()=>{we.playFavorite(!0),x(d.url)},className:`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors hidden lg:flex ${A?"bg-indigo-100 hover:bg-indigo-200 text-indigo-800":"bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300"}`,title:"Set as App Background Wallpaper",children:[a.jsx(kn,{className:"w-3.5 h-3.5 text-indigo-400"}),a.jsx("span",{className:"hidden lg:inline",children:"Set Wallpaper"})]}),'
                'T&&a.jsx("button",{onClick:()=>{we.playDelete(),T(d.id),_smoothBack()},className:`p-2 rounded-lg text-xs font-bold transition-colors ${A?"hover:bg-rose-100 text-rose-600":"hover:bg-rose-600/20 text-rose-400"}`,title:"Move to Trash (30-day retention)",children:a.jsx(ka,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:()=>_(d),className:`p-2 rounded-lg text-xs font-bold transition-colors ${A?"hover:bg-slate-200 text-slate-600":"hover:bg-white/10 text-slate-300"}`,title:"Info & EXIF",children:a.jsx(nh,{className:"w-4 h-4"})}),'
                'a.jsx("button",{onClick:e=>{e.stopPropagation();openPhotoContextMenu(e,d,{onOpen:()=>m(d),onToggleFavorite:()=>y(d.id),onEdit:()=>k(d),onInfo:()=>_(d),onWallpaper:x?()=>x(d.url):null,onDelete:()=>T&&T(d.id)})},className:`p-2 rounded-lg text-xs font-bold transition-colors md:hidden ${A?"hover:bg-slate-200 text-slate-600":"hover:bg-white/10 text-slate-300"}`,title:"More Options",children:a.jsx("svg",{className:"w-4 h-4",fill:"currentColor",viewBox:"0 0 20 20",children:a.jsx("path",{d:"M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"})})}),'
                'a.jsxs("button",{onClick:()=>{we.playKeypad(),m(d)},className:"flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-md shadow-blue-600/30 transition-all",title:"Fullscreen (F)",children:[a.jsx(lh,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"hidden sm:inline",children:"Full Screen"})]})'
                ']})'
            )
            code = code[:start_cv_tb] + repl_cv_tb + code[end_cv_tb:]
            print("[3h] Made cv top toolbar responsive with portrait-friendly collapsing and More Options (...) menu")
        else:
            print("[3h] Warning: Could not find cv toolbar bounds")
    else:
        print("[3h] Note: cv toolbar not found or already patched")

    # -------------------------------------------------------------
    # 4. ov: Smooth Scroll Restoration & Grid Fade-In
    # -------------------------------------------------------------
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
        print("[4a] Patched ov doRestore with instant layout scrollTop followed by smooth centering (zero jerkiness)")
    else:
        print("[4a] Note: target_ov_restore not found or already patched")

    target_ov_scroller_class = 'className:`flex-1 overflow-y-auto px-4 md:px-8 py-6 relative select-none scrollbar-thin scrollbar-thumb-slate-700/50 transition-colors ${Y?"bg-blue-950/30 ring-4 ring-blue-500/40 ring-inset":""}`'
    repl_ov_scroller_class = 'className:`flex-1 overflow-y-auto px-4 md:px-8 py-6 relative select-none scrollbar-thin scrollbar-thumb-slate-700/50 transition-colors animate-fade-in ${Y?"bg-blue-950/30 ring-4 ring-blue-500/40 ring-inset":""}`'
    if target_ov_scroller_class in code:
        code = code.replace(target_ov_scroller_class, repl_ov_scroller_class, 1)
        print("[4b] Added animate-fade-in to ov scroller container for smooth grid entrance")
    else:
        print("[4b] Note: target_ov_scroller_class not found or already patched")

    # Write patched file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    new_len = len(code)
    print(f"Finished patching: {orig_len} -> {new_len} ({new_len - orig_len:+d} bytes)")

    # Verify node syntax
    res = subprocess.run(["node", "-c", file_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FATAL: Syntax validation failed for {file_path}:")
        print(res.stderr)
        sys.exit(1)
    else:
        print(f"VERIFICATION SUCCESS: 0 syntax errors in {file_path}!")

if __name__ == "__main__":
    targets = [
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/android_build/assets/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build/assets/assets/index-DpfNch1h.js",
    ]
    if len(sys.argv) > 1:
        targets = sys.argv[1:]

    for t in targets:
        patch_bundle(t)
    print("\nALL TARGETS PATCHED AND VERIFIED CLEANLY!")
