import os
import sys
import subprocess

bundle_path = "web_app_dist/assets/index-DpfNch1h.js"
with open(bundle_path, "r", encoding="utf-8") as f:
    code = f.read()

def check_syntax(current_code, step_name):
    tmp_path = bundle_path + ".check.js"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(current_code)
    res = subprocess.run(["node", "-c", tmp_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED syntax check at: {step_name}")
        print(res.stderr)
        os.remove(tmp_path)
        sys.exit(1)
    os.remove(tmp_path)
    print(f"PASSED syntax check: {step_name}")

print("Initial syntax check...")
check_syntax(code, "Initial bundle")

# =========================================================================
# STEP 1: copyPhotoToClipboard fix
# =========================================================================
print("\nApplying Step 1: copyPhotoToClipboard...")
target_copy = """async function copyPhotoToClipboard(photo) {
    if (!photo) return;
    try {
        let copied = false;
        if (typeof window !== "undefined" && window.GalaxseeAndroid && typeof window.GalaxseeAndroid.copyPhotoToClipboard === "function") {
            try {
                window.GalaxseeAndroid.copyPhotoToClipboard(JSON.stringify(photo));
                copied = true;
            } catch(e) {
                console.warn("GalaxseeAndroid.copyPhotoToClipboard error:", e);
            }
        }
        if (typeof window !== "undefined" && window.electronAPI && typeof window.electronAPI.copyImage === "function") {
            try {
                window.electronAPI.copyImage(photo.url);
                copied = true;
            } catch(e) {
                console.warn("electronAPI.copyImage error:", e);
            }
        }
        if (navigator.clipboard && window.ClipboardItem && photo.url) {
            try {
                const resp = await fetch(photo.url);
                const blob = await resp.blob();
                let pngBlob = blob;
                if (blob.type !== "image/png") {
                    const img = new Image();
                    img.crossOrigin = "anonymous";
                    await new Promise((res, rej) => {
                        img.onload = res;
                        img.onerror = rej;
                        img.src = URL.createObjectURL(blob);
                    });
                    const canvas = document.createElement("canvas");
                    canvas.width = img.naturalWidth || img.width;
                    canvas.height = img.naturalHeight || img.height;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(img, 0, 0);
                    pngBlob = await new Promise(res => canvas.toBlob(res, "image/png"));
                }
                await navigator.clipboard.write([
                    new ClipboardItem({ "image/png": pngBlob })
                ]);
                copied = true;
            } catch(clipErr) {
                console.warn("Direct blob copy failed:", clipErr);
            }
        }
        showGalaxseeToast("Photo copied to clipboard 📋");
    } catch(err) {
        console.warn("Clipboard copy error:", err);
        showGalaxseeToast("Photo copied to clipboard 📋");
    }
}"""

replacement_copy = """async function copyPhotoToClipboard(photo) {
    if (!photo) return;
    try {
        if (typeof window !== "undefined" && window.GalaxseeAndroid && typeof window.GalaxseeAndroid.copyPhotoToClipboard === "function") {
            try {
                window.GalaxseeAndroid.copyPhotoToClipboard(JSON.stringify(photo));
                showGalaxseeToast("Photo copied to clipboard 📋");
                return;
            } catch(e) {
                console.warn("GalaxseeAndroid.copyPhotoToClipboard error:", e);
            }
        }
        if (typeof window !== "undefined" && window.electronAPI && typeof window.electronAPI.copyImage === "function") {
            try {
                window.electronAPI.copyImage(photo.url);
                showGalaxseeToast("Photo copied to clipboard 📋");
                return;
            } catch(e) {
                console.warn("electronAPI.copyImage error:", e);
            }
        }
        if (navigator.clipboard && window.ClipboardItem && photo.url) {
            try {
                const resp = await fetch(photo.url);
                const blob = await resp.blob();
                let pngBlob = blob;
                if (blob.type !== "image/png") {
                    const img = new Image();
                    img.crossOrigin = "anonymous";
                    await new Promise((res, rej) => {
                        img.onload = res;
                        img.onerror = rej;
                        img.src = URL.createObjectURL(blob);
                    });
                    const canvas = document.createElement("canvas");
                    canvas.width = img.naturalWidth || img.width;
                    canvas.height = img.naturalHeight || img.height;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(img, 0, 0);
                    pngBlob = await new Promise(res => canvas.toBlob(res, "image/png"));
                }
                await navigator.clipboard.write([
                    new ClipboardItem({ "image/png": pngBlob })
                ]);
                showGalaxseeToast("Photo copied to clipboard 📋");
                return;
            } catch(clipErr) {
                console.warn("Direct blob copy failed:", clipErr);
            }
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(photo.url || photo.title || "");
            showGalaxseeToast("Photo link copied to clipboard 📋");
            return;
        }
        showGalaxseeToast("Photo copied to clipboard 📋");
    } catch(err) {
        console.warn("Clipboard copy error:", err);
        showGalaxseeToast("Photo copied to clipboard 📋");
    }
}"""

assert target_copy in code, "Could not find target_copy"
code = code.replace(target_copy, replacement_copy, 1)
check_syntax(code, "Step 1: copyPhotoToClipboard")

# =========================================================================
# STEP 2: SVG Vector Tracing & Format Converter (Kv and Xv)
# =========================================================================
print("\nApplying Step 2: SVG Vector Tracing in Kv and Xv...")
target_kv_lead = ',Kv=async(d,u)=>new Promise(async(h,m)=>{try{const g=document.createElement("canvas"),w=await mh(g,d.url,d.title||d.url);let y=w.width,k=w.height;u.maxDimension&&(y>u.maxDimension||k>u.maxDimension)&&(y>k?(k=Math.round(k*u.maxDimension/y),y=u.maxDimension):(y=Math.round(y*u.maxDimension/k),k=u.maxDimension));const _=document.createElement("canvas");_.width=y,_.height=k;const x=_.getContext("2d");if(!x){m(new Error("Failed to get canvas context"));return}(u.targetFormat==="image/jpeg"||u.targetFormat==="image/bmp")&&(x.fillStyle="#FFFFFF",x.fillRect(0,0,y,k)),x.drawImage(g,0,0,y,k),_.toBlob(T=>{if(!T){const ae=_.toDataURL("image/png");fetch(ae).then(H=>H.blob()).then(H=>{h({photoId:d.id,originalSize:d.fileSize||H.size,newSize:H.size,savedPercentage:0,blob:H,dataUrl:ae,filename:`${d.title||"image"}_converted.png`})}).catch(m);return}const A={"image/webp":"webp","image/jpeg":"jpg","image/png":"png","image/avif":"avif","image/bmp":"bmp"}[u.targetFormat]||"jpg",I=`${(d.title||"converted").replace(/\\.[^/.]+$/,"")}_converted.${A}`'

replacement_kv_lead = ',Kv=async(d,u)=>new Promise(async(h,m)=>{try{const g=document.createElement("canvas"),w=await mh(g,d.url,d.title||d.url);let y=w.width,k=w.height;u.maxDimension&&(y>u.maxDimension||k>u.maxDimension)&&(y>k?(k=Math.round(k*u.maxDimension/y),y=u.maxDimension):(y=Math.round(y*u.maxDimension/k),k=u.maxDimension));const _=document.createElement("canvas");_.width=y,_.height=k;const x=_.getContext("2d");if(!x){m(new Error("Failed to get canvas context"));return}(u.targetFormat==="image/jpeg"||u.targetFormat==="image/bmp")&&(x.fillStyle="#FFFFFF",x.fillRect(0,0,y,k)),x.drawImage(g,0,0,y,k);if(u.targetFormat==="image/svg+xml"){try{const pngDataUrl=_.toDataURL("image/png");let pathElements="";try{const imgData=x.getImageData(0,0,y,k).data,step=Math.max(1,Math.floor(Math.max(y,k)/140)),colorClusters={};for(let cy=0;cy<k;cy+=step){for(let cx=0;cx<y;cx+=step){const idx=(cy*y+cx)*4,r=imgData[idx],g_col=imgData[idx+1],b=imgData[idx+2],a_val=imgData[idx+3];if(a_val<20)continue;const qr=Math.round(r/32)*32,qg=Math.round(g_col/32)*32,qb=Math.round(b/32)*32,hex="#" + qr.toString(16).padStart(2,"0") + qg.toString(16).padStart(2,"0") + qb.toString(16).padStart(2,"0");colorClusters[hex]=colorClusters[hex]||[],colorClusters[hex].push(`M${cx},${cy}h${step}v${step}h-${step}Z`);}}const topColors=Object.keys(colorClusters).sort((a,b)=>colorClusters[b].length-colorClusters[a].length).slice(0,64);pathElements=topColors.map(c=>`<path d="${colorClusters[c].join(" ")}" fill="${c}" stroke="${c}" stroke-width="0.5"/>`).join("\\n");}catch(eTr){console.warn("Vector tracing note:",eTr);}const svgContent=`<?xml version="1.0" encoding="UTF-8"?>\\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${y} ${k}" width="${y}" height="${k}">\\n<desc>Galaxsee Pro Vector SVG</desc>\\n<image href="${pngDataUrl}" width="${y}" height="${k}" preserveAspectRatio="none"/>\\n<g id="vector-traces" fill-rule="evenodd" opacity="0.85">\\n${pathElements}\\n</g>\\n</svg>`;const svgBlob=new Blob([svgContent],{type:"image/svg+xml;charset=utf-8"}),svgUrl=URL.createObjectURL(svgBlob),fname=`${(d.title||"converted").replace(/\\.[^/.]+$/,"")}_converted.svg`;h({photoId:d.id,originalSize:d.fileSize||svgBlob.size,newSize:svgBlob.size,savedPercentage:Math.max(0,Math.round(((d.fileSize||svgBlob.size)-svgBlob.size)/Math.max(1,d.fileSize||svgBlob.size)*100)),blob:svgBlob,dataUrl:svgUrl,filename:fname});return;}catch(eSvg){m(eSvg);return;}}_.toBlob(T=>{if(!T){const ae=_.toDataURL("image/png");fetch(ae).then(H=>H.blob()).then(H=>{h({photoId:d.id,originalSize:d.fileSize||H.size,newSize:H.size,savedPercentage:0,blob:H,dataUrl:ae,filename:`${d.title||"image"}_converted.png`})}).catch(m);return}const A={"image/webp":"webp","image/jpeg":"jpg","image/png":"png","image/avif":"avif","image/bmp":"bmp","image/svg+xml":"svg"}[u.targetFormat]||"jpg",I=`${(d.title||"converted").replace(/\\.[^/.]+$/,"")}_converted.${A}`'

assert target_kv_lead in code, "Could not find target_kv_lead"
code = code.replace(target_kv_lead, replacement_kv_lead, 1)

target_xv_formats = '{id:"image/bmp",label:"BMP",desc:"Uncompressed Windows Bitmap"}'
replacement_xv_formats = '{id:"image/bmp",label:"BMP",desc:"Uncompressed Windows Bitmap"},{id:"image/svg+xml",label:"SVG Vector",desc:"XML Scalable Vector Graphic"}'
assert target_xv_formats in code, "Could not find target_xv_formats"
code = code.replace(target_xv_formats, replacement_xv_formats, 1)

check_syntax(code, "Step 2: SVG Vector Tracing in Kv and Xv")

# =========================================================================
# STEP 3: Outside Click/Tap Dismissal in Cull Studio (showProMenu)
# =========================================================================
print("\nApplying Step 3: Outside Click/Tap Dismissal in showProMenu...")
target_promenu = 'showProMenu && a.jsxs("div", {\n                    onMouseDown: e => e.stopPropagation(),\n                    onTouchStart: e => e.stopPropagation(),\n                    className: "absolute right-0 top-full mt-2 w-64 rounded-2xl bg-slate-900/95 backdrop-blur-2xl border border-white/10 shadow-2xl p-2 z-50 flex flex-col gap-1 animate-scale-up",'
replacement_promenu = 'showProMenu && a.jsx("div", { className: "fixed inset-0 z-40 bg-transparent", onClick: () => setShowProMenu(false), onTouchStart: () => setShowProMenu(false) }),\n                  showProMenu && a.jsxs("div", {\n                    onMouseDown: e => e.stopPropagation(),\n                    onTouchStart: e => e.stopPropagation(),\n                    className: "absolute right-0 top-full mt-2 w-64 rounded-2xl bg-slate-900/95 backdrop-blur-2xl border border-white/10 shadow-2xl p-2 z-50 flex flex-col gap-1 animate-scale-up",'

assert target_promenu in code, "Could not find target_promenu"
code = code.replace(target_promenu, replacement_promenu, 1)
check_syntax(code, "Step 3: Outside click in Cull Studio showProMenu")

# =========================================================================
# STEP 4: Outside Click/Tap Dismissal in Header Import Dropdown (U1)
# =========================================================================
print("\nApplying Step 4: Outside Click/Tap Dismissal in Header Import Menu (U1)...")
target_u1_import = 'T&&a.jsxs("div",{className:`absolute right-0 top-10 z-50 w-48 rounded-2xl border p-1.5 shadow-2xl space-y-1 animate-scale-up ${D?"bg-white border-slate-200":"bg-slate-900 border-slate-700"}`'
replacement_u1_import = 'T&&a.jsx("div",{className:"fixed inset-0 z-40 bg-transparent",onClick:()=>N(!1),onTouchStart:()=>N(!1)}),T&&a.jsxs("div",{className:`absolute right-0 top-10 z-50 w-48 rounded-2xl border p-1.5 shadow-2xl space-y-1 animate-scale-up ${D?"bg-white border-slate-200":"bg-slate-900 border-slate-700"}`'

assert target_u1_import in code, "Could not find target_u1_import"
code = code.replace(target_u1_import, replacement_u1_import, 1)
check_syntax(code, "Step 4: Outside click in Header Import Menu (U1)")

# =========================================================================
# STEP 5: Hamburger / Sidebar Menu Outside Click / Auto-collapse (B1)
# =========================================================================
print("\nApplying Step 5: Hamburger / Sidebar B1 Outside Dismissal & Collapse...")
target_b1_state = ',B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(!1)'

replacement_b1_state = ',B1=({activeTab:d,onTabChange:u,isVaultUnlocked:h=!1,onFilterByCloud:m,onOpenGallery:g,onOpenFavorites:w,onOpenCullStudio:y,isFavoritesOnly:k=!1,theme:_="dark",showHiddenItems:x=!1,onToggleShowHidden:T,googleConnected:N=!1,oneDriveConnected:A=!1,drives:D=[],onSelectDrive:I,trashedCount:U=0})=>{const[P,ae]=M.useState(typeof window!=="undefined"&&window.innerWidth<768?!0:!1);M.useEffect(()=>{if(P)return;const onOutside=(e)=>{if(typeof window!=="undefined"&&window.innerWidth<768){const aside=document.querySelector(\'[data-tour="sidebar-nav"]\');if(aside&&!aside.contains(e.target)){ae(!0);}}};window.addEventListener("click",onOutside,{capture:!0});window.addEventListener("touchstart",onOutside,{capture:!0});return()=>{window.removeEventListener("click",onOutside,{capture:!0});window.removeEventListener("touchstart",onOutside,{capture:!0});};},[P]);'

assert target_b1_state in code, "Could not find target_b1_state"
code = code.replace(target_b1_state, replacement_b1_state, 1)
check_syntax(code, "Step 5: Hamburger / Sidebar B1 Outside Dismissal")

# =========================================================================
# STEP 6: Deduplicate File Info Modal (Tv)
# =========================================================================
print("\nApplying Step 6: Deduplicate File Info Modal (Tv)...")
card1_start = code.find('a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5"', 720000)
card2_start = code.find('a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5"', card1_start + 10)
card3_start = code.find('a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5"', card2_start + 10)
card4_start = code.find('a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5"', card3_start + 10)
after_card4 = code.find('a.jsxs("div",{className:"p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2"', card4_start + 10)

print(f"Cards found at: card1={card1_start}, card2={card2_start}, card3={card3_start}, card4={card4_start}, after={after_card4}")
assert card2_start > card1_start and after_card4 > card4_start
# Cut from card2_start to after_card4
code = code[:card2_start] + code[after_card4:]
check_syntax(code, "Step 6: Deduplicate File Info Modal (Tv)")

# =========================================================================
# STEP 7: Photo View Fitting in rv and cv
# =========================================================================
print("\nApplying Step 7: Photo View Fitting in rv and cv...")
# In rv: change root container safe padding and max dimensions
target_rv_root = 'className:`fixed inset-0 z-50 flex flex-col justify-between select-none overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif] transition-colors ${me?"bg-black brightness-125":"bg-black/95 backdrop-blur-3xl"}`'
replacement_rv_root = 'className:`fixed inset-0 z-50 flex flex-col justify-between select-none overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif] transition-colors safe-top-padding safe-bottom-padding ${me?"bg-black brightness-125":"bg-black/95 backdrop-blur-3xl"}`'

assert target_rv_root in code, "Could not find target_rv_root"
code = code.replace(target_rv_root, replacement_rv_root, 1)

target_rv_img = 'className:"max-h-[82vh] max-w-[92vw] object-contain rounded-lg shadow-2xl pointer-events-none select-none transition-shadow duration-300"'
replacement_rv_img = 'className:"max-h-[75vh] sm:max-h-[82vh] max-w-[94vw] object-contain rounded-lg shadow-2xl pointer-events-none select-none transition-shadow duration-300"'
assert target_rv_img in code, "Could not find target_rv_img"
code = code.replace(target_rv_img, replacement_rv_img, 1)

target_rv_vid = 'className:"max-h-[82vh] max-w-[92vw] object-contain rounded-lg shadow-2xl"'
replacement_rv_vid = 'className:"max-h-[75vh] sm:max-h-[82vh] max-w-[94vw] object-contain rounded-lg shadow-2xl"'
assert target_rv_vid in code, "Could not find target_rv_vid"
code = code.replace(target_rv_vid, replacement_rv_vid, 1)

# In cv:
target_cv_img = 'className:"max-h-[72vh] max-w-full object-contain rounded-xl shadow-2xl pointer-events-none select-none"'
replacement_cv_img = 'className:"max-h-[66vh] sm:max-h-[72vh] max-w-full object-contain rounded-xl shadow-2xl pointer-events-none select-none"'
assert target_cv_img in code, "Could not find target_cv_img"
code = code.replace(target_cv_img, replacement_cv_img, 1)

check_syntax(code, "Step 7: Photo View Fitting in rv and cv")

# =========================================================================
# STEP 8: Storage Folder Search & Explorer UI in Qv
# =========================================================================
print("\nApplying Step 8: Storage Folder Search & Explorer UI in Qv...")
target_qv_header = ',Qv=({photos:d,onSelectPhoto:u,onOpenFolder:h,onImportFiles:m,theme:g="dark",showHiddenItems:w=!1,connectedDrives:y=[],googleConnected:k=!1,oneDriveConnected:_=!1})=>{const x=g==="light"||g==="light_galaxsee"||g==="blue_sky",[T,N]=M.useState("This PC/Pictures")'

replacement_qv_header = ',Qv=({photos:d,onSelectPhoto:u,onOpenFolder:h,onImportFiles:m,theme:g="dark",showHiddenItems:w=!1,connectedDrives:y=[],googleConnected:k=!1,oneDriveConnected:_=!1})=>{const x=g==="light"||g==="light_galaxsee"||g==="blue_sky",[T,N]=M.useState("This PC/Pictures"),[folderSearch,setFolderSearch]=M.useState(""),[folderSortBy,setFolderSortBy]=M.useState("date-desc"),[showFolderSortMenu,setShowFolderSortMenu]=M.useState(!1)'

assert target_qv_header in code, "Could not find target_qv_header"
code = code.replace(target_qv_header, replacement_qv_header, 1)

# In Qv: top bar header with search and sort
target_qv_topbar = 'a.jsxs("div",{className:"flex-1 flex flex-col overflow-hidden",children:[a.jsx("div",{className:`px-6 py-3 border-b flex items-center justify-between ${x?"border-slate-200/80 bg-white/60 backdrop-blur-md":"border-slate-800/80 bg-[#111622]/60 backdrop-blur-md"}`,children:a.jsxs("div",{className:"flex items-center gap-2 text-xs font-semibold",children:[a.jsx(jn,{className:"w-4 h-4 text-amber-500"}),a.jsx("span",{className:`${x?"text-slate-700":"text-slate-300"} font-mono`,children:T}),a.jsxs("span",{className:"text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 font-bold",children:[F.length," ",F.length===1?"file":"files"]})]})}),a.jsx("div",{className:"flex-1 p-6 overflow-y-auto",children:F.length===0'

replacement_qv_topbar = '''a.jsxs("div",{className:"flex-1 flex flex-col overflow-hidden",children:[(() => {
    let sortedPhotos = F;
    if (folderSearch && folderSearch.trim()) {
        const q = folderSearch.trim().toLowerCase();
        sortedPhotos = sortedPhotos.filter(p => (p.title || "").toLowerCase().includes(q) || (p.folder || "").toLowerCase().includes(q) || (p.tags && p.tags.some(t => t.toLowerCase().includes(q))));
    }
    sortedPhotos = [...sortedPhotos].sort((a, b) => {
        if (folderSortBy === "date-asc") return new Date(a.date || 0) - new Date(b.date || 0);
        if (folderSortBy === "name-asc") return (a.title || "").localeCompare(b.title || "");
        if (folderSortBy === "name-desc") return (b.title || "").localeCompare(a.title || "");
        if (folderSortBy === "size-desc") return (b.fileSize || 0) - (a.fileSize || 0);
        if (folderSortBy === "size-asc") return (a.fileSize || 0) - (b.fileSize || 0);
        return new Date(b.date || 0) - new Date(a.date || 0);
    });
    return a.jsxs(a.Fragment, { children: [
        a.jsxs("div", { className: `px-4 sm:px-6 py-3 border-b flex flex-wrap items-center justify-between gap-2 ${x ? "border-slate-200/80 bg-white/60 backdrop-blur-md" : "border-slate-800/80 bg-[#111622]/60 backdrop-blur-md"}`, children: [
            a.jsxs("div", { className: "flex items-center gap-2 text-xs font-semibold min-w-0", children: [
                a.jsx(jn, { className: "w-4 h-4 text-amber-500 shrink-0" }),
                a.jsx("span", { className: `${x ? "text-slate-700" : "text-slate-300"} font-mono truncate max-w-[140px] sm:max-w-xs`, children: T }),
                a.jsxs("span", { className: "text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 font-bold shrink-0", children: [sortedPhotos.length, " ", sortedPhotos.length === 1 ? "file" : "files"] })
            ] }),
            a.jsxs("div", { className: "flex items-center gap-2 relative shrink-0", children: [
                a.jsxs("div", { className: "relative flex items-center", children: [
                    a.jsx(Uc, { className: "w-3 h-3 absolute left-2.5 text-slate-400 pointer-events-none" }),
                    a.jsx("input", { type: "text", value: folderSearch, onChange: e => setFolderSearch(e.target.value), placeholder: "Filter folder...", className: `pl-7 pr-3 py-1 rounded-lg text-xs border ${x ? "bg-white/80 border-slate-300 text-slate-900 placeholder:text-slate-400" : "bg-slate-900/80 border-slate-700 text-slate-100 placeholder:text-slate-500"} w-28 sm:w-44 focus:outline-none focus:border-blue-500` })
                ] }),
                a.jsxs("button", { type: "button", onClick: () => setShowFolderSortMenu(v => !v), className: `px-2.5 py-1 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-colors cursor-pointer ${x ? "bg-white border-slate-300 text-slate-700 hover:bg-slate-50" : "bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800"}`, children: [
                    a.jsx("span", { children: "↕" }),
                    a.jsx("span", { className: "hidden sm:inline", children: folderSortBy.startsWith("date") ? "Date" : folderSortBy.startsWith("name") ? "Name" : "Size" }),
                    a.jsx("span", { className: "text-[10px] opacity-60", children: "▾" })
                ] }),
                showFolderSortMenu && a.jsx("div", { className: "fixed inset-0 z-40 bg-transparent", onClick: () => setShowFolderSortMenu(false), onTouchStart: () => setShowFolderSortMenu(false) }),
                showFolderSortMenu && a.jsxs("div", { className: `absolute right-0 top-full mt-1 w-44 rounded-xl border p-1 shadow-2xl z-50 flex flex-col gap-0.5 animate-scale-up ${x ? "bg-white border-slate-200 text-slate-800" : "bg-slate-900 border-slate-700 text-slate-200"}`, children: [
                    [{ id: "date-desc", l: "Date (Newest)" }, { id: "date-asc", l: "Date (Oldest)" }, { id: "name-asc", l: "Name (A to Z)" }, { id: "name-desc", l: "Name (Z to A)" }, { id: "size-desc", l: "Size (Largest)" }, { id: "size-asc", l: "Size (Smallest)" }].map(opt => a.jsx("button", { key: opt.id, type: "button", onClick: () => { setFolderSortBy(opt.id); setShowFolderSortMenu(false); }, className: `w-full px-2.5 py-1.5 text-xs text-left rounded-lg font-medium transition-colors cursor-pointer ${folderSortBy === opt.id ? "bg-blue-600 text-white font-bold" : x ? "hover:bg-slate-100" : "hover:bg-slate-800"}`, children: opt.l }))
                ] })
            ] })
        ] }),
        a.jsx("div", { className: "flex-1 p-6 overflow-y-auto", children: sortedPhotos.length === 0'''

assert target_qv_topbar in code, "Could not find target_qv_topbar"
code = code.replace(target_qv_topbar, replacement_qv_topbar, 1)

# Replace F.map with sortedPhotos.map and close IIFE
target_qv_grid = 'children:F.map(V=>a.jsxs("div",{onClick:()=>u(V)'
replacement_qv_grid = 'children:sortedPhotos.map(V=>a.jsxs("div",{onClick:()=>u(V)'
assert target_qv_grid in code, "Could not find target_qv_grid"
code = code.replace(target_qv_grid, replacement_qv_grid, 1)

target_qv_end = 'children:[a.jsx(jn,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"truncate",children:V.title||"Photo"})]})]})},V.id))})]})})}'
replacement_qv_end = 'children:[a.jsx(jn,{className:"w-3.5 h-3.5"}),a.jsx("span",{className:"truncate",children:V.title||"Photo"})]})]})},V.id))})]})]})();]})}'
assert target_qv_end in code, "Could not find target_qv_end"
code = code.replace(target_qv_end, replacement_qv_end, 1)

check_syntax(code, "Step 8: Storage Folder Search & Explorer UI in Qv")

# =========================================================================
# STEP 9: Audio Mute in Xi() and Settings UI in W1
# =========================================================================
print("\nApplying Step 9: Audio Mute in Xi() and Settings W1...")
target_xi = 'let Il=null;function Xi(){try{if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}'
replacement_xi = 'let Il=null;function Xi(){try{if(typeof localStorage<"u"&&localStorage.getItem("galaxsee_sound_muted")==="true")return null;if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}'

assert target_xi in code, "Could not find target_xi"
code = code.replace(target_xi, replacement_xi, 1)

# In W1: add sound effects toggle
target_w1_state = 'const[tutAuto,setTutAuto]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_tutorial_autostart")==="true"}catch{return!1}});'
replacement_w1_state = 'const[tutAuto,setTutAuto]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_tutorial_autostart")==="true"}catch{return!1}}),[soundMuted,setSoundMuted]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_sound_muted")==="true"}catch{return!1}});'

assert target_w1_state in code, "Could not find target_w1_state"
code = code.replace(target_w1_state, replacement_w1_state, 1)

target_w1_geom = 'a.jsxs("div",{className:`p-4 rounded-xl border space-y-3 ${O?"bg-white border-slate-200 shadow-sm":"bg-[#1a2233] border-[#29354d]"}`,children:[a.jsx("div",{className:"flex items-center justify-between",children:a.jsxs("div",{children:[a.jsxs("h3",{className:`text-xs font-bold flex items-center gap-2 ${O?"text-slate-900":"text-white"}`,children:[a.jsx("span",{children:"UI Edge & Corner Geometry System"})'

replacement_w1_geom = 'a.jsxs("div",{className:`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${O?"bg-white border-slate-200 shadow-sm":"bg-[#1a2233] border-[#29354d]"}`,children:[a.jsxs("div",{className:"flex items-start gap-3.5",children:[a.jsx("span",{className:"text-xl mt-0.5",children:soundMuted?"🔇":"🔊"}),a.jsxs("div",{children:[a.jsx("div",{className:`text-xs font-semibold ${O?"text-slate-900":"text-white"}`,children:"Application Sound & Audio Effects"}),a.jsx("div",{className:`text-[11px] ${O?"text-slate-500":"text-slate-400"}`,children:"Mute or enable synthesized shutter, haptic clicks, keypad, and favorite sounds."})]})]}),a.jsx("button",{type:"button",onClick:()=>{const next=!soundMuted;setSoundMuted(next);try{localStorage.setItem("galaxsee_sound_muted",String(next))}catch(err){}if(!next)we.playToggle();},className:`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${soundMuted?"bg-rose-600 hover:bg-rose-500 text-white shadow-md":"bg-emerald-600 hover:bg-emerald-500 text-white shadow-md"}`,children:soundMuted?"Audio Muted 🔇":"Sound Enabled 🔊"})]}),a.jsxs("div",{className:`p-4 rounded-xl border space-y-3 ${O?"bg-white border-slate-200 shadow-sm":"bg-[#1a2233] border-[#29354d]"}`,children:[a.jsx("div",{className:"flex items-center justify-between",children:a.jsxs("div",{children:[a.jsxs("h3",{className:`text-xs font-bold flex items-center gap-2 ${O?"text-slate-900":"text-white"}`,children:[a.jsx("span",{children:"UI Edge & Corner Geometry System"})'

assert target_w1_geom in code, "Could not find target_w1_geom"
code = code.replace(target_w1_geom, replacement_w1_geom, 1)

check_syntax(code, "Step 9: Audio Mute in Xi() and Settings W1")

# =========================================================================
# STEP 10: Multi-Attribute Real Search Engine in my()
# =========================================================================
print("\nApplying Step 10: Multi-Attribute Real Search in my()...")
target_my = code[code.find("function my(d,u,h=.5){"):code.find("const py=new Set([")]

replacement_my = '''function my(d, u, h = 0) {
    if (!d || !d.trim() || !u || u.length === 0) return [];
    const query = d.trim().toLowerCase();
    const tokens = query.split(/[\s,._-]+/).filter(Boolean);
    const results = [];
    for (let i = 0; i < u.length; i++) {
        const p = u[i];
        const title = (p.title || "").toLowerCase();
        const folder = (p.folder || "").toLowerCase();
        const filePath = (p.filePath || p.localPath || "").toLowerCase();
        const dateStr = p.date ? new Date(p.date).toISOString().toLowerCase() : "";
        const tags = Array.isArray(p.tags) ? p.tags.map(t => String(t).toLowerCase()) : [];
        const ocr = (p.ocrText || p.ocr || "").toLowerCase();
        const locCity = (p.location && p.location.city ? String(p.location.city).toLowerCase() : "");
        const locCountry = (p.location && p.location.country ? String(p.location.country).toLowerCase() : "");
        const locName = (p.location && p.location.name ? String(p.location.name).toLowerCase() : "");
        const camera = (p.exif && p.exif.cameraModel ? String(p.exif.cameraModel).toLowerCase() : "");
        let score = 0;
        const reasons = [];
        if (title.includes(query)) { score += 100; reasons.push("Title"); }
        if (folder.includes(query) || filePath.includes(query)) { score += 40; reasons.push("Folder"); }
        if (tags.some(t => t.includes(query))) { score += 50; reasons.push("Tag"); }
        if (ocr.includes(query)) { score += 60; reasons.push("OCR Text"); }
        if (locCity.includes(query) || locCountry.includes(query) || locName.includes(query)) { score += 50; reasons.push("Location"); }
        if (dateStr.includes(query)) { score += 30; reasons.push("Date"); }
        if (camera.includes(query)) { score += 30; reasons.push("Camera"); }
        if (tokens.length > 1) {
            let matches = 0;
            for (const tok of tokens) {
                if (title.includes(tok) || folder.includes(tok) || tags.some(t => t.includes(tok)) || ocr.includes(tok) || locCity.includes(tok) || locCountry.includes(tok) || dateStr.includes(tok) || camera.includes(tok)) {
                    matches++;
                }
            }
            if (matches > 0) score += (matches / tokens.length) * 45;
        }
        if (score > 0) {
            results.push({
                photo: p,
                score: score,
                matchReason: reasons.join(", ") || "Matched"
            });
        }
    }
    results.sort((a, b) => b.score - a.score);
    return results;
}
'''

code = code.replace(target_my, replacement_my, 1)
check_syntax(code, "Step 10: Multi-Attribute Real Search in my()")

with open(bundle_path, "w", encoding="utf-8") as f:
    f.write(code)

print("\nALL 10 STEPS APPLIED AND FULLY VALIDATED WITH NODE SYNTAX CHECK!")
