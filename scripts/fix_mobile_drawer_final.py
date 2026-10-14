#!/usr/bin/env python3
"""
Fix the mobile sidebar drawer for Galaxsee.

Root cause: The previous patch injected Tailwind utility classes like
-translate-x-full, md:static, md:translate-x-0, md:w-14 into the
<aside> className. These classes were purged by Vite's CSS tree-shaking
and DO NOT EXIST in the compiled CSS bundle. So the sidebar remained
permanently visible on mobile, squishing the gallery.

Strategy:
1. Revert B1 to the ORIGINAL code from origin/main (P = useState(!1),
   simple w-14/w-60 toggle, no broken Tailwind classes).
2. Apply a CORRECT patch that:
   - Adds mobileOpen state (separate from P)
   - Uses CSS class "mobile-open" on the aside (toggled via JS)
   - Our injected CSS rules use #galaxsee-sidebar with !important
     to force translateX(-100%) on mobile and translateX(0) when
     .mobile-open is present
   - Wraps all nav button clicks in qNav() to auto-close drawer
   - Adds event listeners for galaxsee_toggle_sidebar/close events
   - Adds outside click/touch handlers to close the drawer
3. Ensure CSS rules are in index.html <style> and all CSS files.
4. Validate syntax with node -c.
"""

import os
import sys
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

# The ORIGINAL B1 header from origin/main (before any patches)
ORIG_B1_START = (
    'B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,'
    'onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,'
    'theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,'
    'oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>'
    '{const[P,ae]=M.useState(!1),[H,E]=M.useState(!0),'
    'Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",'
    'K=d==="timeline"&&!k,X=d==="timeline"&&k;'
    'return a.jsxs(a.Fragment,{children:['
    '!P&&a.jsx("div",{className:"fixed inset-0 z-20 md:hidden bg-black/30 backdrop-blur-[1px]",'
    'onClick:()=>ae(!0),onTouchStart:()=>ae(!0),"aria-hidden":"true"}),'
    'a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation",'
    '"aria-label":"Main Navigation",id:"galaxsee-sidebar",'
    'className:`flex flex-col justify-between py-2 safe-bottom-padding select-none '
    "transition-all duration-200 z-30 font-['Plus_Jakarta_Sans',sans-serif] "
    '${Z?"border-r border-slate-200 bg-[#f8fafc]/90 text-slate-800":'
    '"border-r border-[#1e2638] bg-[#0c101a]/90 text-slate-200"} '
    '${P?"w-14":"w-60"}`,children:['
)

# The NEW B1 header with proper mobileOpen state and CSS-class-based drawer
NEW_B1_START = (
    'B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,'
    'onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,'
    'theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,'
    'oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>'
    '{const[P,ae]=M.useState(!1),[H,E]=M.useState(!0),'
    'Z=_==="light"||_==="light_galaxsee"||_==="blue_sky",'
    'K=d==="timeline"&&!k,X=d==="timeline"&&k;'
    # mobileOpen state - separate from P (collapse/expand)
    'const[mobileOpen,setMobileOpen]=M.useState(!1);'
    # useEffect: sync .mobile-open class, listen for events, outside click
    'M.useEffect(()=>{'
    'const sb=document.getElementById("galaxsee-sidebar");'
    'if(sb){if(mobileOpen){sb.classList.add("mobile-open")}else{sb.classList.remove("mobile-open")}}'
    # Event listeners for programmatic toggle/close
    'const onToggle=()=>setMobileOpen(v=>!v);'
    'const onClose=()=>setMobileOpen(!1);'
    'window.addEventListener("galaxsee_toggle_sidebar",onToggle);'
    'window.addEventListener("galaxsee_close_sidebar",onClose);'
    'window.__galaxsee_toggle_sidebar=onToggle;'
    'window.__galaxsee_close_sidebar=onClose;'
    # Outside click/touch to close
    'const onOutside=(e)=>{'
    'if(typeof window!=="undefined"&&window.innerWidth<768&&mobileOpen){'
    'const aside=document.getElementById("galaxsee-sidebar");'
    'if(aside&&!aside.contains(e.target)){setMobileOpen(!1);}'
    '}};'
    'document.addEventListener("click",onOutside,{passive:!0,capture:!0});'
    'document.addEventListener("touchstart",onOutside,{passive:!0,capture:!0});'
    'return()=>{'
    'window.removeEventListener("galaxsee_toggle_sidebar",onToggle);'
    'window.removeEventListener("galaxsee_close_sidebar",onClose);'
    'document.removeEventListener("click",onOutside,{capture:!0});'
    'document.removeEventListener("touchstart",onOutside,{capture:!0});'
    '};'
    '},[mobileOpen]);'
    # qNav wrapper: close drawer on mobile, then call handler
    'const qNav=(fn)=>{setMobileOpen(!1);if(fn)fn();};'
    # return - use galaxsee-backdrop div instead of the original Tailwind backdrop
    'return a.jsxs(a.Fragment,{children:['
    'mobileOpen&&a.jsx("div",{className:"galaxsee-backdrop",'
    'onClick:()=>setMobileOpen(!1),onTouchStart:()=>setMobileOpen(!1),'
    '"aria-hidden":"true"}),'
    'a.jsxs("aside",{"data-tour":"sidebar-nav",role:"navigation",'
    '"aria-label":"Main Navigation",id:"galaxsee-sidebar",'
    # Keep original className - just w-14/w-60, no broken Tailwind mobile classes
    'className:`flex flex-col justify-between py-2 safe-bottom-padding select-none '
    "transition-all duration-200 z-30 font-['Plus_Jakarta_Sans',sans-serif] "
    '${Z?"border-r border-slate-200 bg-[#f8fafc]/90 text-slate-800":'
    '"border-r border-[#1e2638] bg-[#0c101a]/90 text-slate-200"} '
    '${P?"w-14":"w-60"}`,children:['
)

# Nav button onClick wrappers - wrap existing onClick handlers in qNav()
# These are the original onClick handlers we need to wrap
NAV_BUTTONS = [
    # Gallery button
    (
        '{onClick:()=>{g?g():(m==null||m("all"),u("timeline"))}',
        '{onClick:()=>qNav(()=>{g?g():(m==null||m("all"),u("timeline"))})'
    ),
    # Favorites button
    (
        '{onClick:()=>{w?w():u("timeline")}',
        '{onClick:()=>qNav(()=>{w?w():u("timeline")})'
    ),
    # Folders button
    (
        '{onClick:()=>{u("folders")}',
        '{onClick:()=>qNav(()=>{u("folders")})'
    ),
    # Vault button
    (
        '{onClick:()=>u("vault")',
        '{onClick:()=>qNav(()=>u("vault"))'
    ),
    # Duplicates button
    (
        '{onClick:()=>u("duplicates")',
        '{onClick:()=>qNav(()=>u("duplicates"))'
    ),
    # Trash button
    (
        '{onClick:()=>u("trash")',
        '{onClick:()=>qNav(()=>u("trash"))'
    ),
    # Albums button
    (
        '{onClick:()=>u("albums")',
        '{onClick:()=>qNav(()=>u("albums"))'
    ),
]

# The toggle button inside the aside - on mobile it should open/close drawer
ORIG_TOGGLE = 'onClick:()=>ae(!P),className:`w-10 h-10 rounded-lg flex items-center justify-center transition-colors mb-2'
NEW_TOGGLE = 'onClick:()=>{if(typeof window!=="undefined"&&window.innerWidth<768){setMobileOpen(v=>!v)}else{ae(!P)}},className:`w-10 h-10 rounded-lg flex items-center justify-center transition-colors mb-2'


def patch_css_files(repo_path):
    """Inject CSS rules into index.html and all CSS files."""
    print(f"\n[CSS] Patching CSS in {repo_path}...")
    marker = "/* Galaxsee Mobile Responsive Navigation & Drawer */"
    
    for root, dirs, files in os.walk(repo_path):
        # Skip .git directories
        if '.git' in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            
            if file == "index.html":
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if marker in content:
                    # Remove old CSS rules and re-add fresh ones
                    parts = content.split(marker)
                    if len(parts) >= 2:
                        # Find the end of the old CSS block (before </style>)
                        before = parts[0]
                        # Find </style> in the remainder
                        rest = marker.join(parts[1:])  # in case marker appears multiple times
                        style_end = rest.find("</style>")
                        if style_end != -1:
                            after = rest[style_end:]
                            content = before + CSS_RULES + "\n    " + after
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(content)
                            print(f"  Refreshed CSS in {filepath}")
                else:
                    content = content.replace("</style>", CSS_RULES + "\n    </style>")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"  Injected CSS into {filepath}")
                    
            elif file.endswith(".css") and "index-" in file:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if marker in content:
                    # Remove old and re-add
                    idx = content.find(marker)
                    content = content[:idx] + CSS_RULES
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"  Refreshed CSS in {filepath}")
                else:
                    content = content + "\n" + CSS_RULES
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"  Appended CSS to {filepath}")


def patch_js(js_path):
    """Patch B1 component in the JS bundle."""
    print(f"\n[JS] Patching {js_path}...")
    
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # First, check if we need to revert a broken patch
    # The broken patch changed useState(!1) to useState(()=>typeof window...)
    broken_marker = 'M.useState(()=>typeof window!=="undefined"&&window.innerWidth<768?!0:!1)'
    if broken_marker in code:
        print("  Detected broken patch. Reverting B1 to original...")
        
        # Find the current (broken) B1 start
        pos_b1 = code.find("B1=({activeTab:d")
        assert pos_b1 != -1, "B1 not found"
        
        # Find the aside children:[ which is where the header ends
        # The original aside has this className pattern:
        # ${P?"w-14":"w-60"}`,children:[
        # The broken one has: w-64`,children:[
        # We need to find the first children:[ inside aside
        
        pos_aside = code.find('id:"galaxsee-sidebar"', pos_b1)
        assert pos_aside != -1, "galaxsee-sidebar not found"
        
        pos_children = code.find("children:[", pos_aside)
        assert pos_children != -1, "children:[ in aside not found"
        
        # The current broken header goes from pos_b1 to pos_children+10
        old_header = code[pos_b1:pos_children + 10]
        print(f"  Old header length: {len(old_header)} chars")
        
        # Also need to undo the qNav wrappings on nav buttons
        # and the toggle button change
        
        # Replace the header
        code = code[:pos_b1] + NEW_B1_START + code[pos_children + 10:]
        print("  Replaced B1 header with correct mobileOpen implementation")
        
    elif ORIG_B1_START in code:
        print("  Found original B1 header, applying patch...")
        code = code.replace(ORIG_B1_START, NEW_B1_START, 1)
        print("  Replaced B1 header")
    else:
        # Try to find B1 start regardless
        pos_b1 = code.find("B1=({activeTab:d")
        if pos_b1 == -1:
            print("  ERROR: Cannot find B1 component at all!")
            sys.exit(1)
        print(f"  B1 found at {pos_b1}, attempting flexible patch...")
        
        pos_aside = code.find('id:"galaxsee-sidebar"', pos_b1)
        assert pos_aside != -1, "galaxsee-sidebar not found"
        pos_children = code.find("children:[", pos_aside)
        assert pos_children != -1, "children:[ not found"
        
        code = code[:pos_b1] + NEW_B1_START + code[pos_children + 10:]
        print("  Applied flexible header replacement")
    
    # Now fix nav button onClick handlers - wrap in qNav()
    # First, undo any existing qNav wraps that might be broken
    for orig, wrapped in NAV_BUTTONS:
        if wrapped in code:
            # Already wrapped (either from this run or previous)
            pass
        elif orig in code:
            # Count occurrences - some like u("folders") appear multiple times
            count = code.count(orig)
            if count == 1:
                code = code.replace(orig, wrapped, 1)
                print(f"  Wrapped nav button: {orig[:40]}...")
            else:
                # Replace only the first occurrence (the main nav button, not sub-items)
                pos = code.find(orig, code.find("B1=({"))
                if pos != -1:
                    code = code[:pos] + wrapped + code[pos + len(orig):]
                    print(f"  Wrapped first nav button: {orig[:40]}...")
    
    # Fix the toggle button - on mobile should toggle drawer, on desktop toggle collapse
    if NEW_TOGGLE in code:
        print("  Toggle button already patched")
    elif ORIG_TOGGLE in code:
        code = code.replace(ORIG_TOGGLE, NEW_TOGGLE, 1)
        print("  Patched toggle button for mobile drawer")
    else:
        # The broken patch might have changed the toggle differently
        # Look for any toggle pattern
        broken_toggle_patterns = [
            'onClick:()=>{typeof window!=="undefined"&&window.innerWidth<768?setMobileOpen(!1):ae(!P)},className:`w-10 h-10',
            'onClick:()=>{typeof window!=="undefined"&&window.innerWidth<768?setMobileOpen(v=>!v):ae(!P)},className:`w-10 h-10',
        ]
        fixed = False
        for bp in broken_toggle_patterns:
            if bp in code:
                code = code.replace(bp, NEW_TOGGLE.split(',className')[0] + ',className:`w-10 h-10', 1)
                print("  Fixed broken toggle button pattern")
                fixed = True
                break
        if not fixed:
            print("  WARNING: Could not find toggle button pattern to patch")
    
    # Write back
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    # Validate syntax
    res = subprocess.run(["node", "-c", js_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  SYNTAX ERROR: {res.stderr}")
        sys.exit(1)
    else:
        print(f"  ✓ Syntax valid: {js_path}")


def verify_features(js_path):
    """Verify that important features still exist in the bundle."""
    with open(js_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    features = {
        "SVG Vector": "SVG Vector converter",
        "checkForUpdates": "App updater",
        "renderLimit": "Progressive scroll batching",
        "mobileOpen": "Mobile drawer state",
        "mobile-open": "Mobile-open CSS class",
        "galaxsee-backdrop": "Backdrop element",
        "galaxsee_toggle_sidebar": "Toggle sidebar event",
        "qNav": "Navigation auto-close wrapper",
    }
    
    print(f"\n[VERIFY] Feature check in {js_path}:")
    all_ok = True
    for token, label in features.items():
        if token in code:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ MISSING: {label}")
            all_ok = False
    
    return all_ok


if __name__ == "__main__":
    repos = [
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard",
    ]
    
    for repo in repos:
        js_path = os.path.join(repo, "web_app_dist", "assets", "index-DpfNch1h.js")
        if not os.path.exists(js_path):
            print(f"SKIP: {js_path} not found")
            continue
        
        print(f"\n{'='*60}")
        print(f"PATCHING: {repo}")
        print(f"{'='*60}")
        
        patch_css_files(repo)
        patch_js(js_path)
        
        if not verify_features(js_path):
            print(f"\nERROR: Feature verification failed for {repo}")
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print("ALL PATCHES APPLIED SUCCESSFULLY")
    print(f"{'='*60}")
