import sys
import os
import subprocess

def create_patched_b1(b1_code):
    # 1. Update state declaration and add qNav helper + window listeners
    orig_state = """B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(!1),[H,E]=M.useState(!0),Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",K=d==="timeline"&&!k,X=d==="timeline"&&k;return a.jsxs(a.Fragment,{children:[!P&&a.jsx("div",{className:"fixed inset-0 z-20 md:hidden bg-black/30 backdrop-blur-[1px]",onClick:()=>ae(!0),onTouchStart:()=>ae(!0),"aria-hidden":"true"}),a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation","aria-label":"Main Navigation",id:"galaxsee-sidebar",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none transition-all duration-200 z-30 font-['Plus_Jakarta_Sans',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc]/90 text-slate-800":"border-r border-[#1e2638] bg-[#0c101a]/90 text-slate-200"} ${P?"w-14":"w-60"}`,children:"""

    new_state = """B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(()=>typeof window!=="undefined"&&window.innerWidth<768?!0:!1),[H,E]=M.useState(!0),Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",K=d==="timeline"&&!k,X=d==="timeline"&&k;M.useEffect(()=>{const onToggle=()=>ae(v=>!v);const onClose=()=>ae(!0);window.addEventListener("galaxsee_toggle_sidebar",onToggle);window.addEventListener("galaxsee_close_sidebar",onClose);window.__galaxsee_toggle_sidebar=onToggle;window.__galaxsee_close_sidebar=onClose;const onOutside=(e)=>{if(typeof window!=="undefined"&&window.innerWidth<768&&!P){const aside=document.getElementById("galaxsee-sidebar");const toggleBtn=document.querySelector('[data-sidebar-toggle="true"]');if(aside&&!aside.contains(e.target)&&(!toggleBtn||!toggleBtn.contains(e.target))){ae(!0);}}};window.addEventListener("click",onOutside,{passive:!0});window.addEventListener("touchstart",onOutside,{passive:!0});return()=>{window.removeEventListener("galaxsee_toggle_sidebar",onToggle);window.removeEventListener("galaxsee_close_sidebar",onClose);window.removeEventListener("click",onOutside);window.removeEventListener("touchstart",onOutside);};},[P]);const qNav=(fn)=>{if(typeof window!=="undefined"&&window.innerWidth<768){ae(!0);}if(fn)fn();};return a.jsxs(a.Fragment,{children:[!P&&a.jsx("div",{className:"fixed inset-0 z-40 md:hidden bg-black/60 backdrop-blur-sm animate-fade-in",onClick:()=>ae(!0),onTouchStart:()=>ae(!0),"aria-hidden":"true"}),a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation","aria-label":"Main Navigation",id:"galaxsee-sidebar",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none transition-all duration-300 font-['Plus_Jakarta_Sans',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc] text-slate-800":"border-r border-[#1e2638] bg-[#0c101a] text-slate-200"} fixed md:static inset-y-0 left-0 z-50 md:z-30 h-full ${P?"-translate-x-full md:translate-x-0 md:w-14":"translate-x-0 md:w-60 shadow-2xl md:shadow-none"} w-64`,children:"""

    assert orig_state in b1_code, "orig_state not found in B1"
    b1_code = b1_code.replace(orig_state, new_state, 1)

    # 2. Wrap all menu item onClick handlers with qNav
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
        if orig in b1_code:
            b1_code = b1_code.replace(orig, rep)
            print(f"Patched B1 nav onClick: {orig[:30]}...")

    return b1_code

def patch_u1(code):
    # Add mobile hamburger toggle to U1 header
    orig_u1 = """children:[a.jsxs("div",{className:"flex items-center gap-2 shrink-0",style:{WebkitAppRegion:"drag"},children:[a.jsx("div",{style:{WebkitAppRegion:"no-drag"},"""
    
    new_u1 = """children:[a.jsxs("div",{className:"flex items-center gap-2 shrink-0",style:{WebkitAppRegion:"drag"},children:[a.jsx("button",{type:"button","data-sidebar-toggle":"true",onClick:()=>{window.dispatchEvent(new CustomEvent("galaxsee_toggle_sidebar"));try{we.playToggle();}catch{}},className:`p-1.5 -ml-1 mr-0.5 rounded-lg md:hidden flex items-center justify-center cursor-pointer transition-colors ${D?"hover:bg-slate-200 text-slate-700":"hover:bg-white/10 text-slate-300"}`,title:"Toggle Navigation Menu","aria-label":"Toggle Navigation Menu",children:a.jsx(yb,{className:"w-5 h-5"})}),a.jsx("div",{style:{WebkitAppRegion:"no-drag"},"""

    assert orig_u1 in code, "orig_u1 not found"
    code = code.replace(orig_u1, new_u1, 1)

    # Hide Cull button on small mobile screens (<640px)
    orig_cull = """children:[y&&a.jsxs("button",{onClick:y,className:`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-extrabold rounded-xl transition-all cursor-pointer border whitespace-nowrap shadow-sm"""
    new_cull = """children:[y&&a.jsxs("button",{onClick:y,className:`hidden sm:flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-extrabold rounded-xl transition-all cursor-pointer border whitespace-nowrap shadow-sm"""
    if orig_cull in code:
        code = code.replace(orig_cull, new_cull, 1)
        print("Patched Cull button to hidden sm:flex")

    return code

def patch_ov(code):
    # Add progressive batch windowing state to ov
    orig_ov_state = "[te,ke]=M.useState(!1),[Te,Fe]=M.useState(null),[qe,st]=M.useState(null),nt=M.useRef(new Map);"
    new_ov_state = "[te,ke]=M.useState(!1),[Te,Fe]=M.useState(null),[qe,st]=M.useState(null),nt=M.useRef(new Map),[renderLimit,setRenderLimit]=M.useState(100);M.useEffect(()=>{setRenderLimit(100);},[d,ue,B]);"

    assert orig_ov_state in code, "orig_ov_state not found"
    code = code.replace(orig_ov_state, new_ov_state, 1)
    print("Added renderLimit state to ov")

    # Replace We.map in ov with progressive batching + IntersectionObserver sentinel
    # We locate We.map(Be=>a.jsxs("div",{className:"mb-8 last:mb-20 date-group-container",
    target_start = """We.map(Be=>a.jsxs("div",{className:"mb-8 last:mb-20 date-group-container","""
    assert target_start in code, "target_start not found in ov"

    # Replace Be.photos.map with visiblePhotos.map inside date-group-container
    orig_photos_map = """a.jsx("div",{className:`grid gap-2 sm:gap-3 ${Wt()}`,children:Be.photos.map(Re=>{"""
    new_photos_map = """a.jsx("div",{className:`grid gap-2 sm:gap-3 ${Wt()}`,children:visiblePhotos.map(Re=>{"""
    
    assert orig_photos_map in code, "orig_photos_map not found"

    # Find the full We.map(...) expression in code
    p_start = code.find(target_start)
    # Parse to matching closing )
    depth = 1
    in_str = None
    escape = False
    i = p_start + 6 # right after We.map(
    while i < len(code) and depth > 0:
        ch = code[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif in_str:
            if ch == in_str:
                in_str = None
        else:
            if ch in ("\"", "'", "`"):
                in_str = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        i += 1
    p_end = i
    orig_wemap = code[p_start:p_end]

    # Create optimized wemap
    # Inside orig_wemap, replace target_start with:
    # (() => { let renderedCount = 0; return We.map(Be => { if (renderedCount >= renderLimit) return null; const startCount = renderedCount; renderedCount += Be.photos.length; const visiblePhotos = Be.photos.slice(0, Math.max(0, renderLimit - startCount)); if (visiblePhotos.length === 0) return null; return a.jsxs("div", { className: "mb-8 last:mb-20 date-group-container",
    
    opt_wemap_body = orig_wemap.replace(orig_photos_map, new_photos_map, 1)
    
    prefix = """(()=>{let renderedCount=0;return We.map(Be=>{if(renderedCount>=renderLimit)return null;const startCount=renderedCount;renderedCount+=Be.photos.length;const visiblePhotos=Be.photos.slice(0,Math.max(0,renderLimit-startCount));if(visiblePhotos.length===0)return null;return a.jsxs("div",{className:"mb-8 last:mb-20 date-group-container","""

    opt_wemap_body = opt_wemap_body.replace(target_start, prefix, 1)

    # Append sentinel right after the self-invoking function:
    sentinel_jsx = """,renderLimit<Ue.length&&a.jsxs("div",{ref:el=>{if(el&&typeof IntersectionObserver!=="undefined"){const obs=new IntersectionObserver(entries=>{if(entries[0]&&entries[0].isIntersecting){setRenderLimit(prev=>Math.min(Ue.length,prev+100));}},{rootMargin:"600px"});obs.observe(el);}},className:"py-6 w-full flex flex-col items-center justify-center gap-2 text-slate-400 font-mono text-xs select-none",children:[a.jsx("div",{className:"w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"}),a.jsxs("span",{children:["Loaded ",Math.min(renderLimit,Ue.length)," of ",Ue.length," photos"]}),a.jsx("button",{type:"button",onClick:()=>setRenderLimit(Ue.length),className:"px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold transition-all shadow cursor-pointer",children:"Load All Photos"})]})"""

    new_wemap = opt_wemap_body + ")()" + sentinel_jsx

    code = code[:p_start] + new_wemap + code[p_end:]
    print("Replaced We.map with progressive batching and infinite scroll sentinel")
    return code

def patch_file(filepath):
    print(f"\n[PATCHING] {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)
    code = create_patched_b1(code)
    code = patch_u1(code)
    code = patch_ov(code)

    print(f"Original len: {orig_len} -> New len: {len(code)}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    # Test syntax with node -c
    res = subprocess.run(["node", "-c", filepath], capture_output=True, text=True)
    if res.returncode != 0:
        print("SYNTAX ERROR IN PATCHED FILE:")
        print(res.stderr)
        sys.exit(1)
    else:
        print("SYNTAX CHECK PASSED: 0 errors!")

if __name__ == "__main__":
    patch_file("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js")
    patch_file("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js")
