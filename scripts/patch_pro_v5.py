#!/usr/bin/env python3
import sys

with open("test_full_qv.js", "r", encoding="utf-8") as f:
    qv_content = f.read().strip()
if qv_content.startswith("const res = "):
    qv_content = "return " + qv_content[len("const res = "):]
if qv_content.endswith(";"):
    qv_content = qv_content[:-1]
qv_snippet = qv_content

helpers = """
  const flatFolderList=M.useMemo(()=>{
    const list=[];
    const walk=(items)=>{
      for(const it of items){
        if(it.photoCount>0&&!it.isDrive){
          const cover=he.find(p=>{
            if(it.isGoogle)return p.cloudSource==="google";
            if(it.isOneDrive)return p.cloudSource==="onedrive";
            if(it.isUsb)return(p.localPath||"").toLowerCase().includes(it.path.replace("Drive/","").toLowerCase());
            const info=ge(p,U);
            if(it.path==="This PC/Pictures")return info.root==="pictures";
            return info.folderPath===it.path;
          });
          list.push({
            id:it.id,
            name:it.name,
            path:it.path,
            photoCount:it.photoCount,
            coverUrl:cover?(cover.thumbnailUrl||cover.url):null,
            isGoogle:it.isGoogle,
            isOneDrive:it.isOneDrive,
            isUsb:it.isUsb,
            isCustom:it.isCustom
          });
        }
        if(it.children&&Array.isArray(it.children))walk(it.children);
      }
    };
    walk(R);
    return list;
  },[R,he,U]);
  const sortedPhotos=M.useMemo(()=>{
    let list=F;
    if(folderSearch&&folderSearch.trim()){
      const q=folderSearch.trim().toLowerCase();
      list=list.filter(p=>(p.title||"").toLowerCase().includes(q)||(p.folder||"").toLowerCase().includes(q)||(p.tags&&p.tags.some(t=>t.toLowerCase().includes(q))));
    }
    return [...list].sort((a,b)=>{
      if(folderSortBy==="date-asc")return new Date(a.date||0)-new Date(b.date||0);
      if(folderSortBy==="name-asc")return(a.title||"").localeCompare(b.title||"");
      if(folderSortBy==="name-desc")return(b.title||"").localeCompare(a.title||"");
      if(folderSortBy==="size-desc")return(b.fileSize||0)-(a.fileSize||0);
      if(folderSortBy==="size-asc")return(a.fileSize||0)-(b.fileSize||0);
      return new Date(b.date||0)-new Date(a.date||0);
    });
  },[F,folderSearch,folderSortBy]);
"""

def patch_file(file_path):
    global qv_snippet, helpers
    print(f"Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    orig_len = len(code)

    # 1. Search placeholder: Remove "AI Vector Search..." and replace with clean placeholder + aria-label
    search_old = 'placeholder:"AI Vector Search (e.g. \'sunset beach\', \'red car\') or file names..."'
    search_new = 'placeholder:"Search photos, folders, tags, dates, cameras...","aria-label":"Search photos, folders, tags, dates, and cameras"'
    if search_old in code:
        code = code.replace(search_old, search_new, 1)
        print("[1] Replaced AI Vector Search placeholder with clean search and aria-label")
    else:
        print("[1] WARNING: AI Vector Search placeholder not found")

    # 2. Add "cull" to tab switcher ta in gy
    ta_old = 'W==="settings"&&(Ne="Settings",He="settings");u(tt=>tt.map('
    ta_new = 'W==="settings"?(Ne="Settings",He="settings"):W==="cull"&&(Ne="Cull Studio",He="cull");u(tt=>tt.map('
    if ta_old in code:
        code = code.replace(ta_old, ta_new, 1)
        print("[2] Added cull viewMode to ta tab switcher")
    else:
        print("[2] WARNING: ta_old not found")

    # 3. Add "cull" icon mapping in Q1
    q1_old = 'switch(_||x){case"folders":case"folder":'
    q1_new = 'switch(_||x){case"cull":case"cull_studio":return a.jsx(Fa,{className:"w-3.5 h-3.5 text-indigo-400"});case"folders":case"folder":'
    if q1_old in code:
        code = code.replace(q1_old, q1_new, 1)
        print("[3] Added cull icon mapping to Q1 tab bar")
    else:
        print("[3] WARNING: q1_old not found")

    # 4. Update Cull Studio triggers in gy (Header, Sidebar, Timeline) to open as tab
    hdr_cull_old = 'onOpenCullStudio:()=>{se(ga.length>0?ga:he),B(!0)}'
    hdr_cull_new = 'onOpenCullStudio:()=>{se(ga.length>0?ga:he);ta("cull");}'
    if hdr_cull_old in code:
        code = code.replace(hdr_cull_old, hdr_cull_new, 1)
        print("[4 a] Header Cull Studio button now opens cull tab")
    else:
        print("[4 a] WARNING: hdr_cull_old not found")

    side_cull_old = 'onOpenCullStudio:()=>{se(he),B(!0)}'
    side_cull_new = 'onOpenCullStudio:()=>{se(ga.length>0?ga:he);ta("cull");}'
    if side_cull_old in code:
        code = code.replace(side_cull_old, side_cull_new, 1)
        print("[4 b] Sidebar Cull Studio button now opens cull tab")
    else:
        print("[4 b] WARNING: side_cull_old not found")

    time_cull_old = 'onOpenCullStudio:W=>{se(W&&W.length>0?W:ga),B(!0)}'
    time_cull_new = 'onOpenCullStudio:W=>{se(W&&W.length>0?W:ga);ta("cull");}'
    if time_cull_old in code:
        code = code.replace(time_cull_old, time_cull_new, 1)
        print("[4 c] Timeline Cull Studio button now opens cull tab")
    else:
        print("[4 c] WARNING: time_cull_old not found")

    # 5. Render xy inside <main> when w === "cull"
    main_cull_old = 'w==="folders"&&a.jsx(Qv,'
    main_cull_new = 'w==="cull"&&a.jsx(xy,{photos:oe.length>0?oe:(ga.length>0?ga:he),isOpen:!0,asTab:!0,onClose:()=>ta("timeline"),onImportPhotos:W=>{R(Ne=>{const He=new Set(Ne.map(dt=>dt.id));return[...W.filter(dt=>!He.has(dt.id)),...Ne]}),se(Ne=>[...W,...Ne])},onApplyCullResults:({keeps:W,rejects:Ne,ratings:He})=>{R(tt=>tt.map(dt=>{const kt=W.includes(dt.id),Ts=Ne.includes(dt.id),pi=He[dt.id];return{...dt,isFavorite:kt?!0:Ts?!1:dt.isFavorite,rating:pi!==void 0?pi:dt.rating}}))},onDeleteRejects:W=>{zt(W)},theme:y}),w==="folders"&&a.jsx(Qv,'
    if main_cull_old in code:
        code = code.replace(main_cull_old, main_cull_new, 1)
        print("[5] Rendered xy inside <main> when w === 'cull'")
    else:
        print("[5] WARNING: main_cull_old not found")

    # Neutralize the old overlay le && a.jsx(xy, ...) outside <main>
    le_cull_old = 'le&&a.jsx(xy,'
    le_cull_new = '!1&&a.jsx(xy,'
    if le_cull_old in code:
        code = code.replace(le_cull_old, le_cull_new, 1)
        print("[5 b] Neutralized fullscreen modal overlay le && a.jsx(xy,)")
    else:
        print("[5 b] WARNING: le_cull_old not found")

    # 6. Add asTab prop & responsive layout to xy component
    xy_sig_old = 'xy = ({ photos: d, isOpen: u, onClose: h, onApplyCullResults: m, onDeleteRejects: g, onImportPhotos: w, theme: y = "dark" }) => {'
    xy_sig_new = 'xy = ({ photos: d, isOpen: u, onClose: h, onApplyCullResults: m, onDeleteRejects: g, onImportPhotos: w, theme: y = "dark", asTab = !1 }) => {'
    if xy_sig_old in code:
        code = code.replace(xy_sig_old, xy_sig_new, 1)
        print("[6 a] Added asTab prop to xy component signature")
    else:
        print("[6 a] WARNING: xy_sig_old not found")

    xy_ret_old = 'className: "fixed inset-0 z-50 bg-[#070a12] text-slate-100 flex flex-col select-none overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif] animate-fade-in",'
    xy_ret_new = 'className: (asTab ? "flex-1 w-full h-full relative" : "fixed inset-0 z-50") + " bg-[#070a12] text-slate-100 flex flex-col select-none overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif] animate-fade-in",'
    if xy_ret_old in code:
        code = code.replace(xy_ret_old, xy_ret_new, 1)
        print("[6 b] Made xy outer container respect asTab")
    else:
        print("[6 b] WARNING: xy_ret_old not found")

    # 7. Dropdown menu fixes:
    # 7a: xy header overflow-hidden -> overflow-visible relative z-30
    xy_hdr_old = 'className: "h-14 px-2.5 sm:px-6 border-b border-white/[0.08] bg-[#0c111d]/90 backdrop-blur-xl flex items-center justify-between z-30 overflow-hidden flex-nowrap flex-shrink-0",'
    xy_hdr_new = 'className: "h-14 px-2 sm:px-4 border-b border-white/[0.08] bg-[#0c111d]/90 backdrop-blur-xl flex items-center justify-between z-30 overflow-visible relative flex-nowrap flex-shrink-0",'
    if xy_hdr_old in code:
        code = code.replace(xy_hdr_old, xy_hdr_new, 1)
        print("[7 a] Fixed Cull Studio header overflow-hidden to overflow-visible")
    else:
        print("[7 a] WARNING: xy_hdr_old not found")

    # 7b: Cull Studio Pro Tools dropdown z-index to z-[100]
    xy_pro_menu_old = 'className: "absolute right-0 top-full mt-2 w-64 rounded-2xl bg-slate-900/95 backdrop-blur-2xl border border-white/10 shadow-2xl p-2 z-50 flex flex-col gap-1 animate-scale-up",'
    xy_pro_menu_new = 'className: "absolute right-0 top-full mt-2 w-64 rounded-2xl bg-slate-900/95 backdrop-blur-2xl border border-white/10 shadow-2xl p-2 z-[100] flex flex-col gap-1 animate-scale-up",'
    if xy_pro_menu_old in code:
        code = code.replace(xy_pro_menu_old, xy_pro_menu_new, 1)
        print("[7 b] Increased Cull Studio Pro Tools menu to z-[100]")
    else:
        print("[7 b] WARNING: xy_pro_menu_old not found")

    # 7c: Gallery Sort dropdown & container in ov
    ov_tb_old = 'a.jsxs("div",{className:"mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80",'
    ov_tb_new = 'a.jsxs("div",{className:"mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80 relative z-30",'
    if ov_tb_old in code:
        code = code.replace(ov_tb_old, ov_tb_new, 1)
        print("[7 c] Added relative z-30 to Gallery toolbar container")
    else:
        print("[7 c] WARNING: ov_tb_old not found")

    ov_sort_old = 'se&&a.jsxs("div",{className:`absolute right-0 top-full mt-1.5 w-72 rounded-2xl p-2 z-50 border shadow-2xl backdrop-blur-xl animate-scale-up space-y-2 text-xs select-none'
    ov_sort_new = 'se&&a.jsx("div",{className:"fixed inset-0 z-40 bg-transparent",onClick:()=>_e(!1),onTouchStart:()=>_e(!1)}),se&&a.jsxs("div",{className:`absolute right-0 top-full mt-1.5 w-72 rounded-2xl p-2 z-[100] border shadow-2xl backdrop-blur-xl animate-scale-up space-y-2 text-xs select-none'
    if ov_sort_old in code:
        code = code.replace(ov_sort_old, ov_sort_new, 1)
        print("[7 d] Added backdrop dismisser & z-[100] to Gallery sort dropdown")
    else:
        print("[7 d] WARNING: ov_sort_old not found")

    # 7d: Editor Save dropdown & header in cv
    ed_hdr_old = 'a.jsxs("div",{className:"h-14 px-3 sm:px-5 border-b border-slate-800 flex items-center justify-between bg-[#111726]/90 backdrop-blur-md overflow-x-auto gap-2",'
    ed_hdr_new = 'a.jsxs("div",{className:"h-14 px-3 sm:px-5 border-b border-slate-800 flex items-center justify-between bg-[#111726]/90 backdrop-blur-md overflow-visible relative z-30 gap-2",'
    if ed_hdr_old in code:
        code = code.replace(ed_hdr_old, ed_hdr_new, 1)
        print("[7 e] Fixed Editor header overflow to overflow-visible relative z-30")
    else:
        print("[7 e] WARNING: ed_hdr_old not found")

    ed_save_old = 'he&&a.jsxs("div",{className:"absolute right-0 top-12 z-50 w-52 rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl p-1.5 space-y-1 animate-scale-up",'
    ed_save_new = 'he&&a.jsx("div",{className:"fixed inset-0 z-40 bg-transparent",onClick:()=>R(!1),onTouchStart:()=>R(!1)}),he&&a.jsxs("div",{className:"absolute right-0 top-12 z-[100] w-52 rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl p-1.5 space-y-1 animate-scale-up",'
    if ed_save_old in code:
        code = code.replace(ed_save_old, ed_save_new, 1)
        print("[7 f] Added backdrop dismisser & z-[100] to Editor save dropdown")
    else:
        print("[7 f] WARNING: ed_save_old not found")

    # 8. Qv Folder Grid:
    idx_qv = code.find("Qv=({photos:")
    idx_jv = code.find("Jv=({isOpen:", idx_qv)
    idx_ret = code.find('return a.jsxs("div",{className:`flex-1 flex overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif]', idx_qv)

    if idx_qv != -1 and idx_jv != -1 and idx_ret != -1:
        qv_head = code[idx_qv:idx_ret]
        qv_head = qv_head.replace('[T,N]=M.useState("This PC/Pictures"),', '[T,N]=M.useState(null),[folderSearch,setFolderSearch]=M.useState(""),[folderSortBy,setFolderSortBy]=M.useState("date-desc"),[showFolderSortMenu,setShowFolderSortMenu]=M.useState(!1),')

        qv_eff_old = 'M.useEffect(()=>{const V=[],Ce=j=>{for(const v of j)v.photoCount>0&&V.push(v.path),v.children&&Ce(v.children)};if(Ce(R),V.length>0&&!V.includes(T)){const j=V.find(v=>v==="This PC/Pictures")||V[0];N(j)}},[R,T]);'
        qv_eff_new = 'M.useEffect(()=>{if(T){const V=[],Ce=j=>{for(const v of j)v.photoCount>0&&V.push(v.path),v.children&&Ce(v.children)};Ce(R);if(V.length>0&&!V.includes(T)){N(null);}}},[R,T]);'
        qv_head = qv_head.replace(qv_eff_old, qv_eff_new)

        code = code[:idx_qv] + qv_head + helpers + qv_snippet + code[idx_jv - 2:]
        print("[8] Successfully upgraded Qv with responsive Folder Grid & Full-Width photo view")
    else:
        print("[8] WARNING: Could not find Qv bounds for replacement")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Done patching {file_path}. New length: {len(code)} (delta: {len(code) - orig_len})")

if __name__ == "__main__":
    patch_file("web_app_dist/assets/index-DpfNch1h.js")
    patch_file("android_build/assets/assets/index-DpfNch1h.js")
