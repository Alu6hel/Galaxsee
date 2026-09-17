#!/usr/bin/env python3
import sys

with open("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/test_full_qv.js", "r", encoding="utf-8") as f:
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
    print(f"Patching {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    orig_len = len(code)

    # 1. Search placeholder: Remove "AI Vector Search..." and replace with clean placeholder + aria-label
    search_old = 'placeholder:"AI Vector Search (e.g. \'sunset beach\', \'red car\') or file names..."'
    search_new = 'placeholder:"Search photos, folders, tags, dates, cameras...","aria-label":"Search photos, folders, tags, dates, and cameras"'
    if search_old in code:
        code = code.replace(search_old, search_new, 1)
        print("[1] Cleaned search placeholder (removed AI lettering) and added aria-label")
    else:
        print("[1] WARNING: search_old not found")

    # 2. Deduplicate Photo Location & Storage in File Info Modal (Tv)
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
            print(f"[2] Deduplicated Photo Location & Storage (count now: {code.count('Photo Location & Storage')})")
    else:
        print("[2] WARNING: Photo Location duplicates not found")

    # 3. Sound Effects Mute Toggle in Audio Synth (Xi) and Settings (W1)
    target_xi = 'let Il=null;function Xi(){try{if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}'
    replacement_xi = 'let Il=null;function Xi(){try{if(typeof localStorage!=="undefined"&&localStorage.getItem("galaxsee_sound_muted")==="true")return null;if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}'
    if target_xi in code:
        code = code.replace(target_xi, replacement_xi, 1)
        print("[3 a] Updated Xi() to respect sound mute")
    else:
        print("[3 a] WARNING: target_xi not found")

    target_w1_state = 'const[tutAuto,setTutAuto]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_tutorial_autostart")==="true"}catch{return!1}});'
    repl_w1_state = target_w1_state + '\n  const[soundMuted,setSoundMuted]=Ju.useState(()=>{try{return localStorage.getItem("galaxsee_sound_muted")==="true"}catch{return!1}});'
    if target_w1_state in code:
        code = code.replace(target_w1_state, repl_w1_state, 1)
        print("[3 b] Added soundMuted state to Settings W1")
    else:
        print("[3 b] WARNING: target_w1_state not found")

    target_w1_card = 'a.jsxs("div",{className:`p-5 rounded-2xl border transition-all ${T?"bg-white/80 border-slate-200/80 shadow-sm":"bg-slate-900/60 border-slate-800/80 shadow-lg"}`,children:[a.jsxs("div",{className:"flex items-center justify-between mb-3",children:[a.jsxs("div",{className:"flex items-center gap-3",children:[a.jsx("div",{className:"p-2.5 rounded-xl bg-blue-500/10 text-blue-400"'
    sound_card = '''a.jsxs("div",{className:`p-5 rounded-2xl border transition-all ${T?"bg-white/80 border-slate-200/80 shadow-sm":"bg-slate-900/60 border-slate-800/80 shadow-lg"}`,children:[a.jsxs("div",{className:"flex items-center justify-between",children:[a.jsxs("div",{className:"flex items-center gap-3",children:[a.jsx("div",{className:"p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400",children:a.jsx("span",{className:"text-base",children:"🔊"})}),a.jsxs("div",{children:[a.jsx("h3",{className:`text-sm font-bold ${T?"text-slate-800":"text-slate-200"}`,children:"UI Sound Effects"}),a.jsx("p",{className:"text-xs text-slate-500",children:"Audio feedback on photo interactions and clicks"})]})]}),a.jsx("button",{type:"button","aria-label":"Toggle sound effects",onClick:()=>{const next=!soundMuted;setSoundMuted(next);try{localStorage.setItem("galaxsee_sound_muted",String(next))}catch{}},className:`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${!soundMuted?"bg-blue-600":"bg-slate-700"}`,children:a.jsx("span",{className:`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${!soundMuted?"translate-x-5":"translate-x-0"}`})})]})]}),'''
    if target_w1_card in code:
        code = code.replace(target_w1_card, sound_card + target_w1_card, 1)
        print("[3 c] Added Sound Effects toggle card to Settings UI")
    else:
        print("[3 c] WARNING: target_w1_card not found")

    # 4. Dropdown menu fixes:
    # Gallery Sort dropdown & container in ov
    ov_tb_old = 'a.jsxs("div",{className:"mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80",'
    ov_tb_new = 'a.jsxs("div",{className:"mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80 relative z-30",'
    if ov_tb_old in code:
        code = code.replace(ov_tb_old, ov_tb_new, 1)
        print("[4 a] Added relative z-30 to Gallery toolbar container")
    else:
        print("[4 a] WARNING: ov_tb_old not found")

    ov_sort_old = 'se&&a.jsxs("div",{className:`absolute right-0 top-full mt-1.5 w-72 rounded-2xl p-2 z-50 border shadow-2xl backdrop-blur-xl animate-scale-up space-y-2 text-xs select-none'
    ov_sort_new = 'se&&a.jsx("div",{className:"fixed inset-0 z-40 bg-transparent",onClick:()=>_e(!1),onTouchStart:()=>_e(!1)}),se&&a.jsxs("div",{className:`absolute right-0 top-full mt-1.5 w-72 rounded-2xl p-2 z-[100] border shadow-2xl backdrop-blur-xl animate-scale-up space-y-2 text-xs select-none'
    if ov_sort_old in code:
        code = code.replace(ov_sort_old, ov_sort_new, 1)
        print("[4 b] Added backdrop dismisser & z-[100] to Gallery sort dropdown")
    else:
        print("[4 b] WARNING: ov_sort_old not found")

    # Editor Save dropdown & header
    ed_hdr_old = 'a.jsxs("div",{className:"h-14 px-3 sm:px-5 border-b border-slate-800 flex items-center justify-between bg-[#111726]/90 backdrop-blur-md overflow-x-auto gap-2",'
    ed_hdr_new = 'a.jsxs("div",{className:"h-14 px-3 sm:px-5 border-b border-slate-800 flex items-center justify-between bg-[#111726]/90 backdrop-blur-md overflow-visible relative z-30 gap-2",'
    if ed_hdr_old in code:
        code = code.replace(ed_hdr_old, ed_hdr_new, 1)
        print("[4 c] Fixed Editor header overflow to overflow-visible relative z-30")
    else:
        print("[4 c] WARNING: ed_hdr_old not found")

    ed_save_old = 'he&&a.jsxs("div",{className:"absolute right-0 top-12 z-50 w-52 rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl p-1.5 space-y-1 animate-scale-up",'
    ed_save_new = 'he&&a.jsx("div",{className:"fixed inset-0 z-40 bg-transparent",onClick:()=>R(!1),onTouchStart:()=>R(!1)}),he&&a.jsxs("div",{className:"absolute right-0 top-12 z-[100] w-52 rounded-2xl bg-slate-900 border border-slate-700 shadow-2xl p-1.5 space-y-1 animate-scale-up",'
    if ed_save_old in code:
        code = code.replace(ed_save_old, ed_save_new, 1)
        print("[4 d] Added backdrop dismisser & z-[100] to Editor save dropdown")
    else:
        print("[4 d] WARNING: ed_save_old not found")

    # 5. Qv Folder Grid: Replace sidebar squishing with responsive Folder Grid + Full-Width folder view
    idx_qv = code.find("Qv=({photos:")
    idx_jv = code.find("Jv=({isOpen:", idx_qv)
    idx_ret = code.find('return a.jsxs("div",{className:`flex-1 flex overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif]', idx_qv)

    if idx_qv != -1 and idx_jv != -1 and idx_ret != -1:
        qv_head = code[idx_qv:idx_ret]
        qv_head = qv_head.replace('[T,N]=M.useState("This PC/Pictures"),', '[T,N]=M.useState(null),[folderSearch,setFolderSearch]=M.useState(""),[folderSortBy,setFolderSortBy]=M.useState("date-desc"),[showFolderSortMenu,setShowFolderSortMenu]=M.useState(!1),')

        qv_eff_old = 'M.useEffect(()=>{const V=[],Ce=j=>{for(const v of j)v.photoCount>0&&V.push(v.path),v.children&&Ce(v.children)};if(Ce(R),V.length>0&&!V.includes(T)){const j=V.find(v=>v==="This PC/Pictures")||V[0];N(j)}},[R,T]);'
        qv_eff_new = 'M.useEffect(()=>{if(T){const V=[],Ce=j=>{for(const v of j)v.photoCount>0&&V.push(v.path),v.children&&Ce(v.children)};Ce(R);if(V.length>0&&!V.includes(T)){N(null);}}},[R,T]);'
        qv_head = qv_head.replace(qv_eff_old, qv_eff_new)

        # F null guard
        f_target = "F=M.useMemo(()=>he.filter(V=>{"
        f_repl = "F=M.useMemo(()=>!T?[]:he.filter(V=>{"
        qv_head = qv_head.replace(f_target, f_repl)

        code = code[:idx_qv] + qv_head + helpers + qv_snippet + code[idx_jv - 2:]
        print("[5] Upgraded Qv with responsive Folder Grid & full-width photo view")
    else:
        print("[5] WARNING: Could not find Qv bounds for replacement")

    # 6. Add Folders button in sidebar B1
    b1_fav_target = ',!P&&a.jsx("span",{className:"truncate",children:"Favorites"})]}),'
    b1_folders_btn = ',!P&&a.jsx("span",{className:"truncate",children:"Favorites"})]}),a.jsxs("button",{onClick:()=>{u("folders")},className:`w-full h-10 px-3 rounded-lg flex items-center gap-3 text-xs font-semibold transition-colors cursor-pointer ${d==="folders"?Z?"bg-blue-50 text-blue-700 font-bold border border-blue-200":"bg-[#1a2336] text-white font-bold border border-[#2d3a54]":Z?"text-slate-700 hover:bg-slate-200":"text-slate-300 hover:bg-white/5 hover:text-white"}`,"title":"Folders & Storage Grid",children:[a.jsx(jn,{className:"w-4 h-4 flex-shrink-0 text-amber-500"}),!P&&a.jsx("span",{className:"truncate",children:"Folders"})]}),'
    if b1_fav_target in code:
        code = code.replace(b1_fav_target, b1_folders_btn, 1)
        print("[6] Added direct Folders button in sidebar B1")
    else:
        print("[6] WARNING: b1_fav_target not found")

    # 7. OMIT Cull Studio from Standard App
    # 7a: Hide Cull Studio button in header U1
    cull_u1_target = 'y&&a.jsxs("button",{onClick:y,className:`flex items-center gap-1.5'
    cull_u1_repl = '!1&&a.jsxs("button",{onClick:y,className:`flex items-center gap-1.5'
    if cull_u1_target in code:
        code = code.replace(cull_u1_target, cull_u1_repl, 1)
        print("[7 a] Omitted Cull Studio button from Header U1")
    else:
        print("[7 a] WARNING: cull_u1_target not found")

    # 7b: Hide Cull Studio button in sidebar B1
    cull_b1_target = 'y&&a.jsxs("button",{onClick:y,className:`w-full h-10 px-3 rounded-lg flex items-center justify-between'
    cull_b1_repl = '!1&&a.jsxs("button",{onClick:y,className:`w-full h-10 px-3 rounded-lg flex items-center justify-between'
    if cull_b1_target in code:
        code = code.replace(cull_b1_target, cull_b1_repl, 1)
        print("[7 b] Omitted Cull Studio button from Sidebar B1")
    else:
        print("[7 b] WARNING: cull_b1_target not found")

    # 7c: Hide Cull Studio button in timeline ov
    cull_ov_target = 'A&&a.jsxs("button",{onClick:()=>{Pe.length>0?'
    cull_ov_repl = '!1&&a.jsxs("button",{onClick:()=>{Pe.length>0?'
    if cull_ov_target in code:
        code = code.replace(cull_ov_target, cull_ov_repl, 1)
        print("[7 c] Omitted Cull Studio button from Timeline ov")
    else:
        print("[7 c] WARNING: cull_ov_target not found")

    # 8. Clean Branding for Standard: "Galaxsee" instead of "Galaxsee Pro"
    code = code.replace('title:"Galaxsee Pro by Alumungandr"', 'title:"Galaxsee by Alumungandr"')
    code = code.replace('children:"Galaxsee Pro"', 'children:"Galaxsee"')
    code = code.replace('STUDIO EDITION', 'STANDARD EDITION')
    code = code.replace('Galaxsee Pro v1.0', 'Galaxsee v1.0')
    print("[8] Updated branding to Standard Galaxsee")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Finished patching {file_path}. New length: {len(code)} (delta: {len(code) - orig_len})")

if __name__ == "__main__":
    patch_file("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js")
    patch_file("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build/assets/assets/index-DpfNch1h.js")
