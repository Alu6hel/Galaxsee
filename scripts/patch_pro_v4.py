#!/usr/bin/env python3
import re
import sys

def patch_index_js():
    file_path = "web_app_dist/assets/index-DpfNch1h.js"
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    print(f"Original file length: {len(code)}")

    # -------------------------------------------------------------
    # 1. Deduplicate Photo Location & Storage in File Info Modal (Tv)
    # -------------------------------------------------------------
    m1 = code.find("Photo Location & Storage")
    m2 = code.find("Photo Location & Storage", m1 + 1)
    m3 = code.find("Photo Location & Storage", m2 + 1)
    m4 = code.find("Photo Location & Storage", m3 + 1)
    after = code.find("Color Histogram", m4)

    if m1 != -1 and m2 != -1 and m4 != -1 and after != -1:
        c2 = code.rfind('a.jsxs("div",{className:"p-3.5 rounded-2xl', 0, m2)
        c_end = code.rfind('a.jsxs("div",{className:"p-3.5 rounded-2xl', 0, after)
        if c2 != -1 and c_end != -1 and c_end > c2:
            code = code[:c2] + code[c_end:]
            print(f"[1/7] Deduplicated Photo Location & Storage (removed duplicate cards, new count: {code.count('Photo Location & Storage')})")
        else:
            print("[1/7] Warning: Could not locate card boundaries for deduplication")
    else:
        print("[1/7] Warning: Photo Location duplicates not found")

    # -------------------------------------------------------------
    # 2. Sound Effects Mute Toggle in Audio Synth (Xi) and Settings (W1)
    # -------------------------------------------------------------
    target_xi = 'let Il=null;function Xi(){try{if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}'
    replacement_xi = 'let Il=null;function Xi(){try{if(typeof localStorage!=="undefined"&&localStorage.getItem("galaxsee_sound_muted")==="true")return null;if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}'
    if target_xi in code:
        code = code.replace(target_xi, replacement_xi, 1)
        print("[2/7 a] Updated Xi() to respect localStorage sound mute")
    else:
        print("[2/7 a] Warning: target_xi not found")

    # In Settings (W1), add sound toggle state and setting card
    target_w1_state = 'const[tutAuto,setTutAuto]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_tutorial_autostart")==="true"}catch{return!1}});'
    repl_w1_state = target_w1_state + '\n  const[soundMuted,setSoundMuted]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_sound_muted")==="true"}catch{return!1}});'
    if target_w1_state in code:
        code = code.replace(target_w1_state, repl_w1_state, 1)
        print("[2/7 b] Added soundMuted state to W1 Settings")
    else:
        print("[2/7 b] Warning: target_w1_state not found")

    sound_card_jsx = '''a.jsxs("div",{className:`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${O?"bg-white border-slate-200 shadow-sm":"bg-[#1a2233] border-[#29354d]"}`,children:[a.jsxs("div",{className:"flex items-start gap-3.5",children:[a.jsx("div",{className:"w-5 h-5 flex items-center justify-center text-lg mt-0.5",children:soundMuted?"🔇":"🔊"}),a.jsxs("div",{children:[a.jsx("div",{className:`text-xs font-semibold ${O?"text-slate-900":"text-white"}`,children:"Sound Effects & Audio Feedback"}),a.jsx("div",{className:`text-[11px] ${O?"text-slate-500":"text-slate-400"}`,children:"Synthesized camera shutter clicks, keypad clicks, and audio tones throughout the app."})]})]}),a.jsx("button",{type:"button",onClick:()=>{const n=!soundMuted;setSoundMuted(n);try{if(n)localStorage.setItem("galaxsee_sound_muted","true");else localStorage.removeItem("galaxsee_sound_muted");}catch(e){}if(!n)we.playToggle();},className:`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${soundMuted?O?"bg-slate-100 hover:bg-slate-200 text-slate-700":"bg-slate-800 hover:bg-slate-700 text-slate-300":"bg-blue-600 hover:bg-blue-500 text-white shadow-md"}`,children:soundMuted?"Sound Muted (Silent)":"Sound Effects Active"})]}),'''
    
    target_w1_card = 'a.jsx("h2",{className:`text-xs font-bold ${O?"text-slate-500":"text-slate-400"}`,children:"Personalization & Themes"}),'
    if target_w1_card in code:
        code = code.replace(target_w1_card, sound_card_jsx + target_w1_card, 1)
        print("[2/7 c] Added Sound Effects card to Settings UI")
    else:
        print("[2/7 c] Warning: target_w1_card not found")

    # -------------------------------------------------------------
    # 3. SVG Vector Conversion in Pro Tools (Kv and Xv)
    # -------------------------------------------------------------
    svg_conversion_logic = '''x.drawImage(g,0,0,y,k);
if(u.targetFormat==="image/svg+xml"){
  try{
    const pngDataUrl=_.toDataURL("image/png");
    const traceCanvas=document.createElement("canvas");
    const traceW=Math.min(320,y);
    const traceH=Math.max(1,Math.round(k*(traceW/y)));
    traceCanvas.width=traceW;
    traceCanvas.height=traceH;
    const tctx=traceCanvas.getContext("2d");
    tctx.drawImage(g,0,0,traceW,traceH);
    const imgData=tctx.getImageData(0,0,traceW,traceH);
    const pixels=imgData.data;
    const scaleX=y/traceW;
    const scaleY=k/traceH;
    const colorBuckets={};
    for(let py=0;py<traceH;py++){
      let curColor=null;
      let startX=0;
      for(let px=0;px<traceW;px++){
        const i=(py*traceW+px)*4;
        const r=Math.round(pixels[i]/32)*32;
        const g=Math.round(pixels[i+1]/32)*32;
        const b=Math.round(pixels[i+2]/32)*32;
        const a=pixels[i+3];
        const hex=a<32?"transparent":`rgb(${r},${g},${b})`;
        if(hex!==curColor){
          if(curColor&&curColor!=="transparent"){
            if(!colorBuckets[curColor])colorBuckets[curColor]=[];
            const rx=Math.round(startX*scaleX);
            const ry=Math.round(py*scaleY);
            const rw=Math.max(1,Math.round((px-startX)*scaleX));
            const rh=Math.max(1,Math.round(scaleY));
            colorBuckets[curColor].push(`M${rx},${ry}h${rw}v${rh}h-${rw}Z`);
          }
          curColor=hex;
          startX=px;
        }
      }
      if(curColor&&curColor!=="transparent"){
        if(!colorBuckets[curColor])colorBuckets[curColor]=[];
        const rx=Math.round(startX*scaleX);
        const ry=Math.round(py*scaleY);
        const rw=Math.max(1,Math.round((traceW-startX)*scaleX));
        const rh=Math.max(1,Math.round(scaleY));
        colorBuckets[curColor].push(`M${rx},${ry}h${rw}v${rh}h-${rw}Z`);
      }
    }
    let vectorPaths="";
    for(const col in colorBuckets){
      if(colorBuckets[col].length>0){
        vectorPaths+=`<path fill="${col}" d="${colorBuckets[col].join(" ")}"/>\\n`;
      }
    }
    const svgXml=`<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${y} ${k}" width="${y}" height="${k}">
  <title>${d.title||"Photo"} - Galaxsee Pro SVG Vector</title>
  <desc>Converted via Galaxsee Pro Raster-to-Vector &amp; High-Res Embedding Engine</desc>
  <g id="vector-tracing-layer" opacity="0.95">
    ${vectorPaths}
  </g>
  <image id="embedded-raster-layer" x="0" y="0" width="${y}" height="${k}" xlink:href="${pngDataUrl}" preserveAspectRatio="none"/>
</svg>`;
    const svgBlob=new Blob([svgXml],{type:"image/svg+xml;charset=utf-8"});
    const svgUrl=URL.createObjectURL(svgBlob);
    const fname=`${(d.title||"vector").replace(/\\.[^/.]+$/,"")}_vector.svg`;
    const savedPct=Math.max(0,Math.round(((d.fileSize||svgBlob.size)-svgBlob.size)/Math.max(1,d.fileSize||svgBlob.size)*100));
    h({photoId:d.id,originalSize:d.fileSize||svgBlob.size,newSize:svgBlob.size,savedPercentage:savedPct,blob:svgBlob,dataUrl:svgUrl,filename:fname});
    return;
  }catch(svgErr){
    console.error("SVG Conversion Error:",svgErr);
  }
}
_.toBlob(T=>{'''

    target_kv_draw = 'x.drawImage(g,0,0,y,k),_.toBlob(T=>{'
    if target_kv_draw in code:
        code = code.replace(target_kv_draw, svg_conversion_logic, 1)
        print("[3/7 a] Injected SVG raster-to-vector tracing and embedding in Kv")
    else:
        print("[3/7 a] Warning: target_kv_draw not found")

    target_formats = '{id:"image/bmp",label:"BMP",desc:"Uncompressed Windows Bitmap"}'
    repl_formats = '{id:"image/bmp",label:"BMP",desc:"Uncompressed Windows Bitmap"},{id:"image/svg+xml",label:"SVG Vector",desc:"XML Scalable Vector Graphic"}'
    if target_formats in code:
        code = code.replace(target_formats, repl_formats, 1)
        print("[3/7 b] Added SVG Vector option in Xv target formats")
    else:
        print("[3/7 b] Warning: target_formats not found")

    # -------------------------------------------------------------
    # 4. Outside Tap / Click Dismissal for Pro Tools Menu (xy)
    # -------------------------------------------------------------
    target_pro_menu_state = 'const [showProMenu, setShowProMenu] = M.useState(false);'
    repl_pro_menu_state = target_pro_menu_state + '''
  M.useEffect(() => {
    if (!showProMenu) return;
    const dismiss = () => setShowProMenu(false);
    const timer = setTimeout(() => {
      window.addEventListener("mousedown", dismiss);
      window.addEventListener("touchstart", dismiss);
    }, 10);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("mousedown", dismiss);
      window.removeEventListener("touchstart", dismiss);
    };
  }, [showProMenu]);'''
    if target_pro_menu_state in code:
        code = code.replace(target_pro_menu_state, repl_pro_menu_state, 1)
        print("[4/7 a] Added outside click/tap dismissal for Pro Tools menu in Cull Studio")
    else:
        print("[4/7 a] Warning: target_pro_menu_state not found")

    # -------------------------------------------------------------
    # 5. Header Import Menu (U1) Outside Tap Dismissal & Mobile Optimization
    # -------------------------------------------------------------
    target_import_state = 'const[T,N]=Ju.useState(!1),'
    repl_import_state = target_import_state + '''
  M.useEffect(() => {
    if (!T) return;
    const dismiss = () => N(false);
    const timer = setTimeout(() => {
      window.addEventListener("mousedown", dismiss);
      window.addEventListener("touchstart", dismiss);
    }, 10);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("mousedown", dismiss);
      window.removeEventListener("touchstart", dismiss);
    };
  }, [T]),'''
    if target_import_state in code:
        code = code.replace(target_import_state, repl_import_state, 1)
        print("[5/7 a] Added outside click/tap dismissal for Import Menu in U1")
    else:
        print("[5/7 a] Warning: target_import_state not found")

    # Hide Cull Studio on mobile in header (hidden sm:flex)
    target_cull_btn = 'className:`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-extrabold rounded-xl transition-all cursor-pointer border whitespace-nowrap shrink-0'
    repl_cull_btn = 'className:`hidden sm:flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-extrabold rounded-xl transition-all cursor-pointer border whitespace-nowrap shrink-0'
    if target_cull_btn in code:
        code = code.replace(target_cull_btn, repl_cull_btn, 1)
        print("[5/7 b] Responsive header: hid duplicate Cull Studio on narrow screens (hidden sm:flex)")
    else:
        print("[5/7 b] Warning: target_cull_btn not found")

    # Add mobile hamburger toggle button in U1 header
    target_u1_logo = 'children:[a.jsx("div",{style:{WebkitAppRegion:"no-drag"},className:`w-7 h-7 rounded-lg'
    repl_u1_logo = '''children:[a.jsx("button",{type:"button",onClick:()=>{window.dispatchEvent(new CustomEvent("galaxsee_toggle_sidebar"));we.playToggle();},className:`p-1.5 -ml-1 mr-0.5 rounded-lg md:hidden flex items-center justify-center cursor-pointer transition-colors ${D?"hover:bg-slate-200 text-slate-700":"hover:bg-white/10 text-slate-300"}`,title:"Toggle Menu",children:a.jsx(yb,{className:"w-4 h-4"})}),a.jsx("div",{style:{WebkitAppRegion:"no-drag"},className:`w-7 h-7 rounded-lg'''
    if target_u1_logo in code:
        code = code.replace(target_u1_logo, repl_u1_logo, 1)
        print("[5/7 c] Added mobile drawer hamburger button in U1 header")
    else:
        print("[5/7 c] Warning: target_u1_logo not found")

    # -------------------------------------------------------------
    # 6. Sidebar (B1) Mobile Off-Canvas Drawer with Backdrop & Auto-Close
    # -------------------------------------------------------------
    target_b1_start = 'B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(!1),[H,E]=M.useState(!0),'
    repl_b1_start = 'B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(!1),[H,E]=M.useState(!0),[mobileOpen,setMobileOpen]=M.useState(!1);M.useEffect(()=>{const toggle=()=>setMobileOpen(v=>!v);const close=()=>setMobileOpen(!1);window.addEventListener("galaxsee_toggle_sidebar",toggle);window.addEventListener("galaxsee_close_sidebar",close);return()=>{window.removeEventListener("galaxsee_toggle_sidebar",toggle);window.removeEventListener("galaxsee_close_sidebar",close);};},[]);'
    if target_b1_start in code:
        code = code.replace(target_b1_start, repl_b1_start, 1)
        print("[6/7 a] Added mobile drawer state & event listeners to B1")
    else:
        print("[6/7 a] Warning: target_b1_start not found")

    # Replace aside classes and add backdrop in B1
    target_b1_aside = 'return a.jsxs("aside",{"data-tour":"sidebar-nav",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none transition-all duration-200 z-30 font-[\'Plus_Jakarta_Sans\',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc]/90 text-slate-800":"border-r border-[#1e2638] bg-[#0c101a]/90 text-slate-200"} ${P?"w-14":"w-60"}`'
    repl_b1_aside = 'return a.jsxs(a.Fragment,{children:[mobileOpen&&a.jsx("div",{onClick:()=>{setMobileOpen(!1);we.playToggle();},className:"fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden animate-fade-in"}),a.jsxs("aside",{"data-tour":"sidebar-nav",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none transition-all duration-300 z-50 font-[\'Plus_Jakarta_Sans\',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc] text-slate-800":"border-r border-[#1e2638] bg-[#0c101a] text-slate-200"} fixed md:static inset-y-0 left-0 ${mobileOpen?"translate-x-0 shadow-2xl":"-translate-x-full md:translate-x-0"} ${P?"md:w-14":"md:w-60"} w-64`'
    
    if target_b1_aside in code:
        code = code.replace(target_b1_aside, repl_b1_aside, 1)
        # Also need to close Fragment at end of B1
        # In B1: ends before `let Il=null;`
        target_b1_end = ']}]})};let Il=null;'
        repl_b1_end = ']}]}),]};let Il=null;'
        if target_b1_end in code:
            code = code.replace(target_b1_end, repl_b1_end, 1)
            print("[6/7 b] Converted B1 to mobile off-canvas drawer with backdrop")
        else:
            print("[6/7 b] Warning: target_b1_end not found")
    else:
        print("[6/7 b] Warning: target_b1_aside not found")

    # In B1, make tab clicks auto-close mobile drawer
    code = code.replace('onClick:()=>{g?g():(m==null||m("all"),u("timeline"))}', 'onClick:()=>{setMobileOpen(!1);g?g():(m==null||m("all"),u("timeline"))}', 1)
    code = code.replace('onClick:()=>{w?w():u("timeline")}', 'onClick:()=>{setMobileOpen(!1);w?w():u("timeline")}', 1)
    code = code.replace('onClick:y,className:`w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs font-semibold transition-colors cursor-pointer ${Z?"text-blue-700 hover:bg-blue-50":"text-blue-300 hover:bg-blue-950/30"}`', 'onClick:()=>{setMobileOpen(!1);y&&y();},className:`w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs font-semibold transition-colors cursor-pointer ${Z?"text-blue-700 hover:bg-blue-50":"text-blue-300 hover:bg-blue-950/30"}`', 1)
    code = code.replace('onClick:()=>{u("folders");}', 'onClick:()=>{setMobileOpen(!1);u("folders");}', 2)
    code = code.replace('onClick:()=>u("vault")', 'onClick:()=>{setMobileOpen(!1);u("vault")}', 1)
    code = code.replace('onClick:()=>u("duplicates")', 'onClick:()=>{setMobileOpen(!1);u("duplicates")}', 1)
    code = code.replace('onClick:()=>u("trash")', 'onClick:()=>{setMobileOpen(!1);u("trash")}', 1)
    code = code.replace('onClick:()=>u("albums")', 'onClick:()=>{setMobileOpen(!1);u("albums")}', 1)
    print("[6/7 c] Wired B1 menu actions to auto-dismiss mobile drawer on tap")

    # -------------------------------------------------------------
    # 7. Folder Explorer (Qv) Sorting Menu & Photo Sorting
    # -------------------------------------------------------------
    # Add outside click dismissal for showSortMenu in Qv
    target_qv_state = 'const [showSortMenu,setShowSortMenu]=M.useState(false);'
    repl_qv_state = target_qv_state + '''
  M.useEffect(() => {
    if (!showSortMenu) return;
    const dismiss = () => setShowSortMenu(false);
    const timer = setTimeout(() => {
      window.addEventListener("mousedown", dismiss);
      window.addEventListener("touchstart", dismiss);
    }, 10);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("mousedown", dismiss);
      window.removeEventListener("touchstart", dismiss);
    };
  }, [showSortMenu]);'''
    if target_qv_state in code:
        code = code.replace(target_qv_state, repl_qv_state, 1)
        print("[7/7 a] Added outside click/tap dismissal for Folder sort menu")
    else:
        print("[7/7 a] Warning: target_qv_state not found")

    # In Qv, sort photos inside activeFolder
    target_active_folder = '''  const activeFolder=M.useMemo(()=>{
    if(!selectedFolder)return null;
    return folderBuckets.find(f=>f.name.toLowerCase()===selectedFolder.toLowerCase())||null;
  },[selectedFolder,folderBuckets]);'''
    repl_active_folder = '''  const activeFolder=M.useMemo(()=>{
    if(!selectedFolder)return null;
    return folderBuckets.find(f=>f.name.toLowerCase()===selectedFolder.toLowerCase())||null;
  },[selectedFolder,folderBuckets]);

  const sortedFolderPhotos=M.useMemo(()=>{
    if(!activeFolder||!activeFolder.photos)return[];
    const list=[...activeFolder.photos];
    switch(folderSort){
      case"name_asc":return list.sort((a,b)=>(a.title||"").localeCompare(b.title||""));
      case"name_desc":return list.sort((a,b)=>(b.title||"").localeCompare(a.title||""));
      case"size":return list.sort((a,b)=>(b.fileSize||0)-(a.fileSize||0));
      case"modified":return list.sort((a,b)=>new Date(a.date||0).getTime()-new Date(b.date||0).getTime());
      case"recent":default:return list.sort((a,b)=>new Date(b.date||0).getTime()-new Date(a.date||0).getTime());
    }
  },[activeFolder,folderSort]);'''
    if target_active_folder in code:
        code = code.replace(target_active_folder, repl_active_folder, 1)
        code = code.replace('activeFolder.photos.map(p=>a.jsxs("div",{', 'sortedFolderPhotos.map(p=>a.jsxs("div",{', 1)
        print("[7/7 b] Added photo sorting (Date, Name, Size) inside selected folder in Qv")
    else:
        print("[7/7 b] Warning: target_active_folder not found")

    # In Qv, show sort menu even when selectedFolder is open
    code = code.replace('!selectedFolder&&a.jsxs("div",{\n            className:"flex items-center gap-2.5",', 'a.jsxs("div",{\n            className:"flex items-center gap-2.5",', 1)
    # And hide folder search input when selectedFolder is open
    code = code.replace('className:`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs transition-all ${isLight?"bg-white border-slate-300 focus-within:border-blue-500":"bg-slate-900/90 border-slate-700/80 focus-within:border-blue-500"}`,', '!selectedFolder&&a.jsxs("div",{className:`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs transition-all ${isLight?"bg-white border-slate-300 focus-within:border-blue-500":"bg-slate-900/90 border-slate-700/80 focus-within:border-blue-500"}`,', 1)
    print("[7/7 c] Kept Sort Menu visible inside selected folder in Qv")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"Patched file written to {file_path}. New length: {len(code)}")

if __name__ == "__main__":
    patch_index_js()
