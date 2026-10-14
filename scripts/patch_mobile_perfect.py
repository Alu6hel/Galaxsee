import sys
import os
import subprocess

CSS_RULES = """
/* Galaxsee Mobile Responsive Navigation & Drawer */
@media (max-width: 767px) {
  #galaxsee-sidebar {
    position: fixed !important;
    top: 0 !important;
    bottom: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    width: 270px !important;
    max-width: 80vw !important;
    z-index: 50 !important;
    transform: translateX(-100%) !important;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: none !important;
    display: flex !important;
  }
  #galaxsee-sidebar.mobile-open {
    transform: translateX(0) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85) !important;
  }
  #galaxsee-sidebar .truncate {
    display: inline !important;
  }
  main {
    width: 100% !important;
    max-width: 100vw !important;
  }
}

@media (min-width: 768px) {
  #galaxsee-sidebar {
    position: static !important;
    transform: none !important;
    transition: width 0.2s ease !important;
  }
}

.galaxsee-backdrop {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background-color: rgba(0, 0, 0, 0.65) !important;
  backdrop-filter: blur(4px) !important;
  -webkit-backdrop-filter: blur(4px) !important;
  z-index: 45 !important;
}
@media (min-width: 768px) {
  .galaxsee-backdrop {
    display: none !important;
  }
}
"""

def patch_css_files(repo_path):
    print(f"\n[CSS] Patching CSS in {repo_path}...")
    # 1. Patch index.html files
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file == "index.html":
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if "/* Galaxsee Mobile Responsive Navigation & Drawer */" not in content:
                    content = content.replace("</style>", CSS_RULES + "\n    </style>")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Patched <style> in {filepath}")

            elif file.endswith(".css") and "index-" in file:
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if "/* Galaxsee Mobile Responsive Navigation & Drawer */" not in content:
                    content = content + "\n" + CSS_RULES
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Appended CSS rules to {filepath}")

def patch_js_bundle(js_path):
    print(f"\n[JS] Patching bundle {js_path}...")
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Find B1 start
    pos_b1 = code.find("B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_=")
    assert pos_b1 != -1, "B1 start not found"

    # Find aside tag inside B1
    pos_aside = code.find("id:\"galaxsee-sidebar\"", pos_b1)
    assert pos_aside != -1, "id:galaxsee-sidebar not found"

    # Extract the block from pos_b1 to pos_aside + 400
    sub = code[pos_b1:pos_aside+400]

    # Target the return and aside declaration
    # We want to replace from pos_b1 up to the start of children of aside
    pos_children = code.find("children:[", pos_aside)
    assert pos_children != -1, "children:[ in aside not found"
    
    orig_b1_header = code[pos_b1:pos_children+10]

    new_b1_header = """B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[mobileOpen,setMobileOpen]=M.useState(!1),[P,ae]=M.useState(!1),[H,E]=M.useState(!0),Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",K=d==="timeline"&&!k,X=d==="timeline"&&k;M.useEffect(()=>{const onToggle=()=>setMobileOpen(v=>!v);const onClose=()=>setMobileOpen(!1);window.addEventListener("galaxsee_toggle_sidebar",onToggle);window.addEventListener("galaxsee_close_sidebar",onClose);window.__galaxsee_toggle_sidebar=onToggle;window.__galaxsee_close_sidebar=onClose;const onOutside=(e)=>{if(typeof window!=="undefined"&&window.innerWidth<768&&mobileOpen){const aside=document.getElementById("galaxsee-sidebar");const toggleBtn=document.querySelector('[data-sidebar-toggle="true"]');if(aside&&!aside.contains(e.target)&&(!toggleBtn||!toggleBtn.contains(e.target))){setMobileOpen(!1);}}};window.addEventListener("click",onOutside,{passive:!0});window.addEventListener("touchstart",onOutside,{passive:!0});return()=>{window.removeEventListener("galaxsee_toggle_sidebar",onToggle);window.removeEventListener("galaxsee_close_sidebar",onClose);window.removeEventListener("click",onOutside);window.removeEventListener("touchstart",onOutside);};},[mobileOpen]);const qNav=(fn)=>{setMobileOpen(!1);if(fn)fn();};return a.jsxs(a.Fragment,{children:[mobileOpen&&a.jsx("div",{className:"galaxsee-backdrop",onClick:()=>setMobileOpen(!1),onTouchStart:()=>setMobileOpen(!1),"aria-hidden":"true"}),a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation","aria-label":"Main Navigation",id:"galaxsee-sidebar",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none font-['Plus_Jakarta_Sans',sans-serif] ${Z?"border-r border-slate-200 bg-[#f8fafc] text-slate-800":"border-r border-[#1e2638] bg-[#0c101a] text-slate-200"} ${mobileOpen?"mobile-open ":""}${P?"w-14":"w-60"}`,children:"""

    code = code[:pos_b1] + new_b1_header + code[pos_children+10:]
    print("Replaced B1 header with mobileOpen state and galaxsee-backdrop")

    # Update top toggle button inside aside so on mobile it closes drawer
    orig_toggle_btn = 'onClick:()=>ae(!P),className:`w-10 h-10 rounded-lg flex items-center justify-center transition-colors mb-2'
    new_toggle_btn = 'onClick:()=>{typeof window!=="undefined"&&window.innerWidth<768?setMobileOpen(!1):ae(!P)},className:`w-10 h-10 rounded-lg flex items-center justify-center transition-colors mb-2'
    if orig_toggle_btn in code:
        code = code.replace(orig_toggle_btn, new_toggle_btn, 1)
        print("Updated toggle button in aside to close mobile drawer")

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Validate syntax with node -c
    res = subprocess.run(["node", "-c", js_path], capture_output=True, text=True)
    if res.returncode != 0:
        print("ERROR: Syntax validation failed on", js_path)
        print(res.stderr)
        sys.exit(1)
    else:
        print("SUCCESS: 0 syntax errors on", js_path)

if __name__ == "__main__":
    patch_css_files("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee")
    patch_css_files("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard")
    patch_js_bundle("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js")
    patch_js_bundle("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js")
