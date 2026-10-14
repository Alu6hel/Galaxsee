import sys
import subprocess

def patch_b1(code):
    orig_b1_start = """B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(!1),[H,E]=M.useState(!0),Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",K=d==="timeline"&&!k,X=d==="timeline"&&k;return a.jsxs(a.Fragment,{children:[!P&&a.jsx("div",{className:"fixed inset-0 z-20 md:hidden bg-black/30 backdrop-blur-[1px]",onClick:()=>ae(!0),onTouchStart:()=>ae(!0),"aria-hidden":"true"}),a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation","aria-label":"Main Navigation",id:"galaxsee-sidebar",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none transition-all duration-200 z-30 font-['Plus_Jakarta_Sans',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc]/90 text-slate-800":"border-r border-[#1e2638] bg-[#0c101a]/90 text-slate-200"} ${P?"w-14":"w-60"}`,children:"""

    new_b1_start = """B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(()=>typeof window!=="undefined"&&window.innerWidth<768?!0:!1),[H,E]=M.useState(!0),Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",K=d==="timeline"&&!k,X=d==="timeline"&&k;M.useEffect(()=>{const onToggle=()=>ae(v=>!v);const onClose=()=>ae(!0);window.addEventListener("galaxsee_toggle_sidebar",onToggle);window.addEventListener("galaxsee_close_sidebar",onClose);window.__galaxsee_toggle_sidebar=onToggle;window.__galaxsee_close_sidebar=onClose;const onOutside=(e)=>{if(typeof window!=="undefined"&&window.innerWidth<768&&!P){const aside=document.getElementById("galaxsee-sidebar");const toggleBtn=document.querySelector('[data-sidebar-toggle="true"]');if(aside&&!aside.contains(e.target)&&(!toggleBtn||!toggleBtn.contains(e.target))){ae(!0);}}};window.addEventListener("click",onOutside,{passive:!0});window.addEventListener("touchstart",onOutside,{passive:!0});return()=>{window.removeEventListener("galaxsee_toggle_sidebar",onToggle);window.removeEventListener("galaxsee_close_sidebar",onClose);window.removeEventListener("click",onOutside);window.removeEventListener("touchstart",onOutside);};},[P]);const qNav=(fn)=>{if(typeof window!=="undefined"&&window.innerWidth<768){ae(!0);}if(fn)fn();};return a.jsxs(a.Fragment,{children:[!P&&a.jsx("div",{className:"fixed inset-0 z-40 md:hidden bg-black/60 backdrop-blur-sm animate-fade-in",onClick:()=>ae(!0),onTouchStart:()=>ae(!0),"aria-hidden":"true"}),a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation","aria-label":"Main Navigation",id:"galaxsee-sidebar",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none transition-all duration-300 font-['Plus_Jakarta_Sans',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc] text-slate-800":"border-r border-[#1e2638] bg-[#0c101a] text-slate-200"} fixed md:static inset-y-0 left-0 z-50 md:z-30 h-full ${P?"-translate-x-full md:translate-x-0 md:w-14":"translate-x-0 md:w-60 shadow-2xl md:shadow-none"} w-64`,children:"""

    assert orig_b1_start in code, "orig_b1_start not found"
    code = code.replace(orig_b1_start, new_b1_start, 1)

    # Wrap B1 navigation onClick handlers
    replacements = [
        ('onClick:()=>{g?g():(m==null||m("all"),u("timeline"))}', 'onClick:()=>qNav(()=>{g?g():(m==null||m("all"),u("timeline"))})'),
        ('onClick:()=>{w?w():u("timeline")}', 'onClick:()=>qNav(()=>{w?w():u("timeline")})'),
        ('onClick:()=>{u("folders")}', 'onClick:()=>qNav(()=>u("folders"))'),
        ('onClick:()=>{m==null||m("onedrive"),u("timeline")}', 'onClick:()=>qNav(()=>{m==null||m("onedrive"),u("timeline")})'),
        ('onClick:()=>{m==null||m("google"),u("timeline")}', 'onClick:()=>qNav(()=>{m==null||m("google"),u("timeline")})'),
        ('onClick:()=>{I==null||I($),u("folders")}', 'onClick:()=>qNav(()=>{I==null||I($),u("folders")})'),
        ('onClick:()=>u("vault")', 'onClick:()=>qNav(()=>u("vault"))'),
        ('onClick:()=>u("duplicates")', 'onClick:()=>qNav(()=>u("duplicates"))'),
        ('onClick:()=>u("trash")', 'onClick:()=>qNav(()=>u("trash"))'),
        ('onClick:()=>u("albums")', 'onClick:()=>qNav(()=>u("albums"))'),
    ]

    for orig, rep in replacements:
        if orig in code:
            code = code.replace(orig, rep, 1)
            print(f"Patched B1 nav onClick: {orig[:30]}...")

    print("Patched B1 drawer and tap-to-hide listeners successfully")
    return code

def patch_u1(code):
    orig_u1_logo = """children:[a.jsxs("div",{className:"flex items-center gap-2 shrink-0",style:{WebkitAppRegion:"drag"},children:[a.jsx("div",{style:{WebkitAppRegion:"no-drag"},"""
    new_u1_logo = """children:[a.jsxs("div",{className:"flex items-center gap-2 shrink-0",style:{WebkitAppRegion:"drag"},children:[a.jsx("button",{type:"button","data-sidebar-toggle":"true",onClick:()=>{window.dispatchEvent(new CustomEvent("galaxsee_toggle_sidebar"));try{we.playToggle();}catch{}},className:`p-1.5 -ml-1 mr-0.5 rounded-lg md:hidden flex items-center justify-center cursor-pointer transition-colors ${D?"hover:bg-slate-200 text-slate-700":"hover:bg-white/10 text-slate-300"}`,title:"Toggle Navigation Menu","aria-label":"Toggle Navigation Menu",children:a.jsx(yb,{className:"w-5 h-5"})}),a.jsx("div",{style:{WebkitAppRegion:"no-drag"},"""

    assert orig_u1_logo in code, "orig_u1_logo not found"
    code = code.replace(orig_u1_logo, new_u1_logo, 1)
    print("Added mobile hamburger toggle to U1 header")

    # Cull button responsive styling
    orig_cull = """children:[y&&a.jsxs("button",{onClick:y,className:`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-extrabold rounded-xl transition-all cursor-pointer border whitespace-nowrap shadow-sm"""
    new_cull = """children:[y&&a.jsxs("button",{onClick:y,className:`hidden sm:flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-extrabold rounded-xl transition-all cursor-pointer border whitespace-nowrap shadow-sm"""
    if orig_cull in code:
        code = code.replace(orig_cull, new_cull, 1)
        print("Set Cull Studio header button to hidden sm:flex")

    return code

def patch_ov(code):
    # 1. Add progressive batching state to ov
    orig_ov_state = "[te,ke]=M.useState(!1),[Te,Fe]=M.useState(null),[qe,st]=M.useState(null),nt=M.useRef(new Map);"
    new_ov_state = "[te,ke]=M.useState(!1),[Te,Fe]=M.useState(null),[qe,st]=M.useState(null),nt=M.useRef(new Map),[renderLimit,setRenderLimit]=M.useState(60);M.useEffect(()=>{setRenderLimit(60);},[d,ue,B]);M.useEffect(()=>{const hScroll=(e)=>{const el=e.target;if(el&&el.scrollHeight&&el.scrollTop+el.clientHeight>=el.scrollHeight-700){setRenderLimit(prev=>prev<10000?prev+60:prev);}};const scroller=document.querySelector('main > div.overflow-y-auto')||window;scroller.addEventListener('scroll',hScroll,{passive:!0});return()=>scroller.removeEventListener('scroll',hScroll);},[]);"

    assert orig_ov_state in code, "orig_ov_state not found in ov"
    code = code.replace(orig_ov_state, new_ov_state, 1)
    print("Added renderLimit state and auto-scroll listener to ov")

    # 2. Slice photos rendering to renderLimit
    orig_photos_map = "a.jsx(\"div\",{className:`grid gap-2 sm:gap-3 ${Wt()}`,children:Be.photos.map(Re=>{"
    new_photos_map = "a.jsx(\"div\",{className:`grid gap-2 sm:gap-3 ${Wt()}`,children:Be.photos.slice(0,renderLimit).map(Re=>{"
    assert orig_photos_map in code, "orig_photos_map not found"
    code = code.replace(orig_photos_map, new_photos_map, 1)
    print("Sliced Be.photos.map to renderLimit")

    # 3. Add load more / show all controls after We.map
    target_wemap_end = "title:\"Info & EXIF\",children:a.jsx(nh,{className:\"w-3.5 h-3.5\"})})]})]})]},Re.id)})})]},Be.dateKey))"
    assert target_wemap_end in code, "target_wemap_end not found"

    controls_jsx = target_wemap_end + """,a.jsxs("div",{className:"py-6 w-full flex flex-col items-center justify-center gap-2 select-none text-slate-400 font-mono text-xs",children:[renderLimit<3200&&a.jsx("button",{type:"button",onClick:()=>setRenderLimit(prev=>prev+60),className:"px-4 py-2 rounded-xl bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 font-bold border border-blue-500/30 transition-all cursor-pointer shadow-sm active:scale-95",children:"Load More Photos (60+)"}),renderLimit<3200&&a.jsx("button",{type:"button",onClick:()=>setRenderLimit(100000),className:"text-[11px] text-slate-500 hover:text-slate-300 underline cursor-pointer",children:"Show All Photos in Library"})]})"""

    code = code.replace(target_wemap_end, controls_jsx, 1)
    print("Appended progressive batching load controls after We.map")
    return code

def patch_file(filepath):
    print(f"\n=======================================================")
    print(f"PATCHING: {filepath}")
    print(f"=======================================================")
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)
    code = patch_b1(code)
    code = patch_u1(code)
    code = patch_ov(code)

    print(f"Code size: {orig_len} -> {len(code)} (+{len(code)-orig_len} bytes)")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    # Test syntax with node -c
    res = subprocess.run(["node", "-c", filepath], capture_output=True, text=True)
    if res.returncode != 0:
        print("ERROR: Syntax validation failed:")
        print(res.stderr)
        sys.exit(1)
    else:
        print("VALIDATION SUCCESS: 0 syntax errors!")

if __name__ == "__main__":
    patch_file("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js")
    patch_file("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js")
