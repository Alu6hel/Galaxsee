with open("web_app_dist/assets/index-DpfNch1h.js", "r", encoding="utf-8") as f:
    text = f.read()

idx_qv = text.find("Qv=({photos:")
idx_jv = text.find("Jv=({isOpen:")
idx_ret = text.find('return a.jsxs("div",{className:`flex-1 flex overflow-hidden font-[\'Plus_Jakarta_Sans\',sans-serif]', idx_qv)

with open("test_full_qv.js", "r", encoding="utf-8") as f:
    qv_content = f.read().strip()
if qv_content.startswith("const res = "):
    qv_content = "return " + qv_content[len("const res = "):]
if qv_content.endswith(";"):
    qv_content = qv_content[:-1]

qv_head = text[idx_qv:idx_ret]
qv_head = qv_head.replace('[T,N]=M.useState("This PC/Pictures"),', '[T,N]=M.useState(null),[folderSearch,setFolderSearch]=M.useState(""),[folderSortBy,setFolderSortBy]=M.useState("date-desc"),[showFolderSortMenu,setShowFolderSortMenu]=M.useState(!1),')

qv_eff_old = 'M.useEffect(()=>{const V=[],Ce=j=>{for(const v of j)v.photoCount>0&&V.push(v.path),v.children&&Ce(v.children)};if(Ce(R),V.length>0&&!V.includes(T)){const j=V.find(v=>v==="This PC/Pictures")||V[0];N(j)}},[R,T]);'
qv_eff_new = 'M.useEffect(()=>{if(T){const V=[],Ce=j=>{for(const v of j)v.photoCount>0&&V.push(v.path),v.children&&Ce(v.children)};Ce(R);if(V.length>0&&!V.includes(T)){N(null);}}},[R,T]);'
qv_head = qv_head.replace(qv_eff_old, qv_eff_new)

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
full_qv = "const " + qv_head + helpers + qv_content + text[885981:idx_jv-1] + ";"
with open("test_full_qv_assembled.js", "w", encoding="utf-8") as f:
    f.write(full_qv)
print("Wrote test_full_qv_assembled.js")
