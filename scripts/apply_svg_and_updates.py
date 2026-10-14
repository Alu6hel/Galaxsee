#!/usr/bin/env python3
import os
import sys

def patch_pro():
    file_path = "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js"
    print(f"[Pro] Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)

    # 1. Replace Kv
    idx_kv = code.find("Kv=async(d,u)=>new Promise")
    idx_xv = code.find("Xv=({photos:d,isOpen:u,onClose:h})")
    assert idx_kv != -1, "Kv start not found"
    assert idx_xv != -1, "Xv start not found"

    new_kv = """Kv=window.__galaxsee_Kv=async(d,u)=>new Promise(async(h,m)=>{
  try{
    const g=document.createElement("canvas"),w=await mh(g,d.url,d.title||d.url);
    let y=w.width,k=w.height;
    u.maxDimension&&(y>u.maxDimension||k>u.maxDimension)&&(y>k?(k=Math.round(k*u.maxDimension/y),y=u.maxDimension):(y=Math.round(y*u.maxDimension/k),k=u.maxDimension));
    const _=document.createElement("canvas");
    _.width=y,_.height=k;
    const x=_.getContext("2d");
    if(!x){m(new Error("Failed to get canvas context"));return}
    (u.targetFormat==="image/jpeg"||u.targetFormat==="image/bmp")&&(x.fillStyle="#FFFFFF",x.fillRect(0,0,y,k));
    x.drawImage(g,0,0,y,k);

    if(u.targetFormat==="image/svg+xml"){
      const origW=y,origH=k,mode=u.vectorMode||"pure",colorCount=u.colorCount||16,fidelity=u.fidelity||640;
      let traceW=origW,traceH=origH;
      if(traceW>fidelity||traceH>fidelity){
        traceW>traceH?(traceH=Math.max(16,Math.round(traceH*fidelity/traceW)),traceW=fidelity):(traceW=Math.max(16,Math.round(traceW*fidelity/traceH)),traceH=fidelity);
      }
      const tc=document.createElement("canvas");
      tc.width=traceW,tc.height=traceH;
      const tctx=tc.getContext("2d");
      if(!tctx){m(new Error("Failed to get trace context"));return}
      tctx.drawImage(g,0,0,traceW,traceH);
      const imgData=tctx.getImageData(0,0,traceW,traceH),data=imgData.data;
      const scaleX=origW/traceW,scaleY=origH/traceH;

      let svgBody="";
      if(mode==="silhouette"){
        const threshold=u.threshold!==void 0?u.threshold:128;
        const runs=[];
        for(let py=0;py<traceH;py++){
          let startX=-1;
          for(let px=0;px<traceW;px++){
            const idx=(py*traceW+px)*4,a=data[idx+3],lum=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2];
            if(a>40&&lum<threshold){if(startX===-1)startX=px;}
            else{if(startX!==-1){runs.push({y:py,x1:startX,x2:px});startX=-1;}}
          }
          if(startX!==-1)runs.push({y:py,x1:startX,x2:traceW});
        }
        const openRects=new Map(),rects=[];
        let curY=-1;
        for(const r of runs){
          const key=r.x1+","+r.x2;
          if(r.y!==curY){
            for(const[k2,rec]of openRects.entries()){if(rec.y+rec.h<r.y){rects.push(rec);openRects.delete(k2);}}
            curY=r.y;
          }
          if(openRects.has(key)){
            const ex=openRects.get(key);
            if(ex.y+ex.h===r.y){ex.h+=1;continue;}
            else{rects.push(ex);openRects.delete(key);}
          }
          openRects.set(key,{x1:r.x1,x2:r.x2,y:r.y,h:1});
        }
        for(const rec of openRects.values())rects.push(rec);
        const pathD=rects.map(r=>`M ${+(r.x1*scaleX).toFixed(1)} ${+(r.y*scaleY).toFixed(1)} h ${+((r.x2-r.x1)*scaleX).toFixed(1)} v ${+(r.h*scaleY).toFixed(1)} h -${+((r.x2-r.x1)*scaleX).toFixed(1)} Z`).join(" ");
        svgBody=`<path fill="${u.fillColor||"#0f172a"}" d="${pathD}" shape-rendering="geometricPrecision"/>`;
      }else if(mode==="hybrid"){
        const rasterUrl=_.toDataURL("image/webp",0.92);
        const runs=[];
        for(let py=0;py<traceH;py+=2){
          let startX=-1;
          for(let px=0;px<traceW;px+=2){
            const idx=(py*traceW+px)*4,a=data[idx+3],lum=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2];
            if(a>60&&lum<85){if(startX===-1)startX=px;}
            else{if(startX!==-1){runs.push({y:py,x1:startX,x2:px});startX=-1;}}
          }
          if(startX!==-1)runs.push({y:py,x1:startX,x2:traceW});
        }
        const pathD=runs.map(r=>`M ${+(r.x1*scaleX).toFixed(1)} ${+(r.y*scaleY).toFixed(1)} h ${+((r.x2-r.x1)*scaleX).toFixed(1)} v ${+(2*scaleY).toFixed(1)} h -${+((r.x2-r.x1)*scaleX).toFixed(1)} Z`).join(" ");
        svgBody=`<g id="raster-base"><image href="${rasterUrl}" x="0" y="0" width="${origW}" height="${origH}" preserveAspectRatio="xMidYMid meet"/></g>`+(pathD?`<g id="vector-accents" opacity="0.4"><path fill="#020617" d="${pathD}"/></g>`:"");
      }else{
        const samples=[];
        const step=Math.max(1,Math.floor((traceW*traceH)/1500));
        for(let i=0;i<data.length;i+=4*step){if(data[i+3]>60)samples.push([data[i],data[i+1],data[i+2]]);}
        const palette=[];
        if(samples.length<=colorCount){for(let i=0;i<samples.length;i++)palette.push(samples[i]);}
        else{
          const sStep=Math.floor(samples.length/colorCount);
          for(let i=0;i<colorCount;i++)palette.push(samples[i*sStep]);
          for(let iter=0;iter<2;iter++){
            const sums=palette.map(()=>[0,0,0,0]);
            for(let i=0;i<samples.length;i++){
              const[sr,sg,sb]=samples[i];
              let bD=Infinity,bI=0;
              for(let p=0;p<palette.length;p++){
                const[pr,pg,pb]=palette[p],d2=(sr-pr)*(sr-pr)+(sg-pg)*(sg-pg)+(sb-pb)*(sb-pb);
                if(d2<bD){bD=d2;bI=p;}
              }
              sums[bI][0]+=sr;sums[bI][1]+=sg;sums[bI][2]+=sb;sums[bI][3]++;
            }
            for(let p=0;p<palette.length;p++){
              if(sums[p][3]>0)palette[p]=[Math.round(sums[p][0]/sums[p][3]),Math.round(sums[p][1]/sums[p][3]),Math.round(sums[p][2]/sums[p][3])];
            }
          }
        }
        const pixelColors=new Int16Array(traceW*traceH);
        for(let i=0,p=0;i<data.length;i+=4,p++){
          if(data[i+3]<40){pixelColors[p]=-1;continue;}
          const r=data[i],g=data[i+1],b=data[i+2];
          let bD=Infinity,bI=0;
          for(let pal=0;pal<palette.length;pal++){
            const[pr,pg,pb]=palette[pal],d2=(r-pr)*(r-pr)+(g-pg)*(g-pg)+(b-pb)*(b-pb);
            if(d2<bD){bD=d2;bI=pal;}
          }
          pixelColors[p]=bI;
        }
        const hex=rgb=>"#"+rgb.map(c=>Math.min(255,Math.max(0,c)).toString(16).padStart(2,"0")).join("");
        const pathLayers=[];
        for(let pal=0;pal<palette.length;pal++){
          const runs=[];
          for(let py=0;py<traceH;py++){
            let startX=-1;
            for(let px=0;px<traceW;px++){
              if(pixelColors[py*traceW+px]===pal){if(startX===-1)startX=px;}
              else{if(startX!==-1){runs.push({y:py,x1:startX,x2:px});startX=-1;}}
            }
            if(startX!==-1)runs.push({y:py,x1:startX,x2:traceW});
          }
          const openRects=new Map(),rects=[];
          let curY=-1;
          for(const r of runs){
            const key=r.x1+","+r.x2;
            if(r.y!==curY){
              for(const[k2,rec]of openRects.entries()){if(rec.y+rec.h<r.y){rects.push(rec);openRects.delete(k2);}}
              curY=r.y;
            }
            if(openRects.has(key)){
              const ex=openRects.get(key);
              if(ex.y+ex.h===r.y){ex.h+=1;continue;}
              else{rects.push(ex);openRects.delete(key);}
            }
            openRects.set(key,{x1:r.x1,x2:r.x2,y:r.y,h:1});
          }
          for(const rec of openRects.values())rects.push(rec);
          if(rects.length>0){
            const pathD=rects.map(r=>`M ${+(r.x1*scaleX).toFixed(1)} ${+(r.y*scaleY).toFixed(1)} h ${+((r.x2-r.x1)*scaleX).toFixed(1)} v ${+(r.h*scaleY).toFixed(1)} h -${+((r.x2-r.x1)*scaleX).toFixed(1)} Z`).join(" ");
            pathLayers.push(`<path fill="${hex(palette[pal])}" d="${pathD}" shape-rendering="crispEdges"/>`);
          }
        }
        svgBody=`<g id="vector-layers">\\n${pathLayers.join("\\n")}\\n</g>`;
      }

      const fullSvg=`<?xml version="1.0" encoding="UTF-8"?>\\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${origW} ${origH}" width="${origW}" height="${origH}">\\n<!-- Galaxsee Pro Algorithmic Vector Engine (Mode: ${mode}) -->\\n${svgBody}\\n</svg>`;
      const blob=new Blob([fullSvg],{type:"image/svg+xml;charset=utf-8"});
      const dataUrl=URL.createObjectURL(blob);
      const filename=`${(d.title||"image").replace(/\\.[^/.]+$/,"")}_vector.svg`;
      const origSize=d.fileSize||blob.size;
      const savedPercentage=origSize>0?Math.max(0,Math.round((origSize-blob.size)/origSize*100)):0;
      h({photoId:d.id,originalSize:origSize,newSize:blob.size,savedPercentage,blob,dataUrl,svgText:fullSvg,filename,mimeType:"image/svg+xml"});
      return;
    }

    _.toBlob(T=>{
      if(!T){
        const ae=_.toDataURL("image/png");
        fetch(ae).then(H=>H.blob()).then(H=>{
          h({photoId:d.id,originalSize:d.fileSize||H.size,newSize:H.size,savedPercentage:0,blob:H,dataUrl:ae,filename:`${d.title||"image"}_converted.png`})
        }).catch(m);
        return;
      }
      const A={"image/webp":"webp","image/jpeg":"jpg","image/png":"png","image/avif":"avif","image/bmp":"bmp"}[u.targetFormat]||"jpg",
            I=`${(d.title||"converted").replace(/\\.[^/.]+$/,"")}_converted.${A}`,
            U=URL.createObjectURL(T),
            P=Math.max(0,Math.round(((d.fileSize||T.size)-T.size)/Math.max(1,d.fileSize||T.size)*100));
      h({photoId:d.id,originalSize:d.fileSize||T.size,newSize:T.size,savedPercentage:P,blob:T,dataUrl:U,filename:I});
    },u.targetFormat,u.quality);
  }catch(g){m(g)}
})"""

    # 2. Replace Xv
    idx_wv = code.find("Wv=({photos:d,isOpen:u,onClose:h,onApplyBatchRename:m")
    assert idx_wv != -1, "Wv start not found"

    new_xv = """Xv=({photos:d,isOpen:u,onClose:h})=>{
  const[m,g]=M.useState("image/webp"),
       [w,y]=M.useState(.85),
       [k,_]=M.useState(void 0),
       [x,T]=M.useState(!1),
       [N,A]=M.useState([]),
       [D,I]=M.useState(0),
       [vMode,setVMode]=M.useState("pure"),
       [vColors,setVColors]=M.useState(16),
       [vFidelity,setVFidelity]=M.useState(640);

  if(!u)return null;

  const U=async()=>{
    T(!0),A([]),we.playShutter();
    const X=[];
    for(let $=0;$<d.length;$++){
      I($+1);
      try{
        const me=await Kv(d[$],{targetFormat:m,quality:w,maxDimension:k,vectorMode:vMode,colorCount:vColors,fidelity:vFidelity});
        X.push(me);
      }catch(me){
        console.error("Conversion failed for photo:",d[$].id,me);
      }
    }
    A(X),T(!1),we.playFavorite(!0);
  };

  const P=X=>{
    if(window.GalaxseeAndroid&&typeof window.GalaxseeAndroid.saveFileToDevice==="function"){
      try{
        window.GalaxseeAndroid.saveFileToDevice(X.filename,X.svgText||X.dataUrl,X.mimeType||"image/svg+xml");
      }catch(err){
        console.error("Native save failed:",err);
      }
    }
    const $=document.createElement("a");
    $.href=X.dataUrl,$.download=X.filename,$.click();
  };

  const ae=()=>{N.forEach(X=>P(X))};
  const H=d.reduce((X,$)=>X+$.fileSize,0);
  const E=N.reduce((X,$)=>X+$.newSize,0);
  const Z=H>0?Math.max(0,Math.round((H-E)/H*100)):0;
  const K=X=>X<1024*1024?`${(X/1024).toFixed(1)} KB`:`${(X/(1024*1024)).toFixed(2)} MB`;

  return a.jsx("div",{className:"fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-center justify-center p-4 select-none animate-fade-in font-[\x27Plus_Jakarta_Sans\x27,sans-serif]",children:a.jsxs("div",{className:"w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]",children:[
    a.jsxs("div",{className:"h-16 px-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/60",children:[
      a.jsxs("div",{className:"flex items-center gap-3",children:[
        a.jsx("div",{className:"p-2 rounded-xl bg-emerald-500/10 text-emerald-400",children:a.jsx(rr,{className:"w-5 h-5"})}),
        a.jsxs("div",{children:[
          a.jsx("h2",{className:"text-base font-bold text-white",children:"Format Converter & SVG Vector Studio"}),
          a.jsxs("p",{className:"text-xs text-slate-400",children:["Convert ",d.length," ",d.length===1?"file":"files"," to SVG vector or modern formats"]})
        ]})
      ]}),
      a.jsx("button",{onClick:h,className:"p-2 rounded-full hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer",children:a.jsx(Xt,{className:"w-5 h-5"})})
    ]}),
    a.jsxs("div",{className:"p-6 space-y-5 overflow-y-auto",children:[
      a.jsxs("div",{children:[
        a.jsx("label",{className:"block text-xs font-bold text-slate-300 mb-2",children:"Target File Format"}),
        a.jsx("div",{className:"grid grid-cols-2 sm:grid-cols-3 gap-2.5",children:[
          {id:"image/svg+xml",label:"SVG Vector",desc:"Scalable Contours & XML Paths"},
          {id:"image/webp",label:"WebP",desc:"Google Modern & Compact"},
          {id:"image/jpeg",label:"JPEG",desc:"Universal Photo Compatibility"},
          {id:"image/png",label:"PNG",desc:"Lossless & Transparent"},
          {id:"image/avif",label:"AVIF",desc:"Next-Gen AV1 10-bit HDR"},
          {id:"image/bmp",label:"BMP",desc:"Uncompressed Windows Bitmap"}
        ].map(X=>a.jsxs("button",{key:X.id,onClick:()=>g(X.id),className:`p-3 rounded-2xl border text-left transition-all cursor-pointer ${m===X.id?"bg-emerald-600/20 border-emerald-500 text-white shadow-lg":"bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"}`,children:[
          a.jsx("div",{className:"text-xs font-bold",children:X.label}),
          a.jsx("div",{className:"text-[10px] text-slate-400",children:X.desc})
        ]}))})
      ]}),
      m==="image/svg+xml"?a.jsxs("div",{className:"p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-4",children:[
        a.jsxs("div",{children:[
          a.jsx("label",{className:"block text-xs font-semibold text-slate-300 mb-1.5",children:"Vector Engine Mode"}),
          a.jsx("div",{className:"grid grid-cols-3 gap-2",children:[
            {id:"pure",label:"Pure Vector",desc:"Color Contours"},
            {id:"silhouette",label:"Silhouette",desc:"Monochrome Logo"},
            {id:"hybrid",label:"Hybrid",desc:"Raster + Vector"}
          ].map(X=>a.jsxs("button",{key:X.id,onClick:()=>setVMode(X.id),className:`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${vMode===X.id?"bg-emerald-600 text-white border-emerald-500 shadow-md":"bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800"}`,children:[
            a.jsx("div",{className:"text-xs font-bold",children:X.label}),
            a.jsx("div",{className:"text-[10px] opacity-75",children:X.desc})
          ]}))})
        ]}),
        vMode==="pure"&&a.jsxs("div",{className:"pt-2 border-t border-slate-800",children:[
          a.jsx("label",{className:"block text-xs font-semibold text-slate-300 mb-1.5",children:"Palette Color Quantization"}),
          a.jsx("div",{className:"grid grid-cols-4 gap-2",children:[
            {label:"8 Colors",val:8},{label:"16 Colors",val:16},{label:"32 Colors",val:32},{label:"64 Colors",val:64}
          ].map(X=>a.jsx("button",{key:X.val,onClick:()=>setVColors(X.val),className:`py-1.5 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${vColors===X.val?"bg-emerald-600 text-white border-emerald-500":"bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800"}`,children:X.label}))})
        ]}),
        a.jsxs("div",{className:"pt-2 border-t border-slate-800",children:[
          a.jsx("label",{className:"block text-xs font-semibold text-slate-300 mb-1.5",children:"Detail Analysis Grid"}),
          a.jsx("div",{className:"grid grid-cols-3 gap-2",children:[
            {label:"Standard (640px)",val:640},{label:"Fine (1080px)",val:1080},{label:"Ultra (1440px)",val:1440}
          ].map(X=>a.jsx("button",{key:X.val,onClick:()=>setVFidelity(X.val),className:`py-1.5 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${vFidelity===X.val?"bg-emerald-600 text-white border-emerald-500":"bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800"}`,children:X.label}))})
        ]})
      ]}):a.jsxs("div",{className:"p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-4",children:[
        a.jsxs("div",{children:[
          a.jsxs("div",{className:"flex items-center justify-between text-xs font-semibold text-slate-300 mb-1",children:[
            a.jsx("span",{children:"Output Quality"}),
            a.jsxs("span",{className:"font-mono text-emerald-400 font-bold",children:[Math.round(w*100),"%"]})
          ]}),
          a.jsx("input",{type:"range",min:"0.4",max:"1.0",step:"0.05",value:w,onChange:X=>y(parseFloat(X.target.value)),className:"w-full accent-emerald-500"})
        ]}),
        a.jsxs("div",{className:"pt-2 border-t border-slate-800",children:[
          a.jsx("label",{className:"block text-xs font-semibold text-slate-300 mb-1.5",children:"Max Resolution Limit"}),
          a.jsx("div",{className:"grid grid-cols-4 gap-2",children:[
            {label:"Original",val:void 0},{label:"4K (3840px)",val:3840},{label:"2K (2048px)",val:2048},{label:"FHD (1080px)",val:1080}
          ].map(X=>a.jsx("button",{key:X.label,onClick:()=>_(X.val),className:`py-2 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${k===X.val?"bg-emerald-600 text-white border-emerald-500":"bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800"}`,children:X.label}))})
        ]})
      ]}),
      N.length>0&&a.jsxs("div",{className:"p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 space-y-2",children:[
        a.jsxs("div",{className:"flex items-center justify-between",children:[
          a.jsxs("span",{className:"text-xs font-bold text-white flex items-center gap-1.5",children:[
            a.jsx(Ig,{className:"w-4 h-4 text-emerald-400"}),
            N.length," Files Processed Successfully"
          ]}),
          a.jsxs("span",{className:"px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono text-xs font-bold",children:[
            m==="image/svg+xml"?"Vector SVG Ready":`-${Z}% Saved`
          ]})
        ]}),
        a.jsxs("div",{className:"text-xs text-emerald-200/80 font-mono flex justify-between",children:[
          a.jsxs("span",{children:["Original: ",K(H)]}),
          a.jsx(Rc,{className:"w-3.5 h-3.5 inline"}),
          a.jsxs("span",{children:["Output: ",K(E)]})
        ]})
      ]})
    ]}),
    a.jsxs("div",{className:"p-4 px-6 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between",children:[
      a.jsx("button",{onClick:h,className:"px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-800 cursor-pointer",children:"Close"}),
      N.length>0?a.jsxs("button",{onClick:ae,className:"px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-600/20 cursor-pointer",children:[
        a.jsx(Yl,{className:"w-4 h-4"}),
        "Download All (",N.length,")"
      ]}):a.jsxs("button",{onClick:U,disabled:x,className:"px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-600/20 cursor-pointer",children:[
        a.jsx(ui,{className:`w-4 h-4 ${x?"animate-spin":""}`}),
        x?(m==="image/svg+xml"?`Vectorizing ${D}/${d.length}...`:`Transcoding ${D}/${d.length}...`):(m==="image/svg+xml"?"Vectorize to SVG":"Start Transcoding")
      ]})
    ]})
  ]})})
}"""

    code = code[:idx_kv] + new_kv + ",\n" + new_xv + ",\n" + code[idx_wv:]
    print(f"[Pro] Successfully replaced Kv and Xv. Length delta: {len(code) - orig_len}")

    # 2. Expose openFormatConverter in gy
    hook_target = "$e=M.useRef(null);"
    hook_inject = "$e=M.useRef(null);M.useEffect(()=>{window.__galaxsee_openFormatConverter=W=>nt(W);},[]);"
    assert hook_target in code, "hook_target not found"
    code = code.replace(hook_target, hook_inject, 1)
    print("[Pro] Hooked window.__galaxsee_openFormatConverter")

    # 3. Add Convert to SVG Vector to openPhotoContextMenu
    cm_item_target = "label: 'Edit Photo',"
    cm_vector_item = """label: 'Convert to SVG Vector',
            shortcut: 'V',
            action: () => {
                if (typeof window.__galaxsee_openFormatConverter === 'function') {
                    window.__galaxsee_openFormatConverter([photo]);
                }
            }
        },
        {
            icon: '<svg style="width:16px;height:16px;color:#a855f7;" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
            label: 'Edit Photo',"""
    if cm_item_target in code:
        code = code.replace(cm_item_target, cm_vector_item, 1)
        print("[Pro] Added Convert to SVG Vector to context menu")

    # 4. Update W1 in Pro
    code = patch_w1(code, is_pro=True)

    # 5. Context menu label
    cm_old = '"Convert Format"'
    cm_new = '"Convert / Vectorize (SVG)"'
    if cm_old in code:
        code = code.replace(cm_old, cm_new, 1)
        print("[Pro] Updated context menu label")

    # 6. Viewer toolbar title
    vt_old = 'title:"Convert Format (WebP/JPEG/PNG)"'
    vt_new = 'title:"Convert Format & SVG Vector Tracing"'
    if vt_old in code:
        code = code.replace(vt_old, vt_new, 1)
        print("[Pro] Updated viewer toolbar title")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[Pro] Wrote updated bundle to {file_path}")

def patch_w1(code, is_pro=True):
    repo_owner = "Alu6hel"
    repo_name = "Galaxsee-pro" if is_pro else "Galaxsee"
    app_title = "Galaxsee Pro" if is_pro else "Galaxsee"

    # A. Top of W1
    w1_target1 = "const [cloudConnectModal, setCloudConnectModal] = Ju.useState(null);"
    w1_inject1 = """const [cloudConnectModal, setCloudConnectModal] = Ju.useState(null);
  const [updateChecking, setUpdateChecking] = Ju.useState(false);
  const [updateInfo, setUpdateInfo] = Ju.useState(null);
  const [updateProgress, setUpdateProgress] = Ju.useState(null);
  const [updateError, setUpdateError] = Ju.useState("");
  const [showUpdateModal, setShowUpdateModal] = Ju.useState(false);

  Ju.useEffect(() => {
    const onChecked = (e) => {
      setUpdateChecking(false);
      if (e.detail) {
        if (e.detail.error) {
          setUpdateError(e.detail.error);
        } else {
          setUpdateError("");
          setUpdateInfo(e.detail);
        }
        setShowUpdateModal(true);
      }
    };
    const onProgress = (e) => {
      if (e.detail) setUpdateProgress(e.detail);
    };
    const onError = (e) => {
      if (e.detail && e.detail.error) setUpdateError(e.detail.error);
      setUpdateProgress(null);
    };
    window.addEventListener("galaxseeUpdateChecked", onChecked);
    window.addEventListener("galaxseeUpdateProgress", onProgress);
    window.addEventListener("galaxseeUpdateError", onError);
    return () => {
      window.removeEventListener("galaxseeUpdateChecked", onChecked);
      window.removeEventListener("galaxseeUpdateProgress", onProgress);
      window.removeEventListener("galaxseeUpdateError", onError);
    };
  }, []);

  const handleCheckUpdates = async () => {
    setUpdateChecking(true);
    setUpdateError("");
    setUpdateProgress(null);
    try { we.playToggle(); } catch {}
    const repoOwner = "REPO_OWNER";
    const repoName = "REPO_NAME";
    if (window.GalaxseeAndroid && typeof window.GalaxseeAndroid.checkForUpdates === "function") {
      window.GalaxseeAndroid.checkForUpdates(repoOwner, repoName);
    } else {
      try {
        const resp = await fetch("https://api.github.com/repos/" + repoOwner + "/" + repoName + "/releases/latest");
        if (!resp.ok) throw new Error("HTTP Status " + resp.status);
        const data = await resp.json();
        const tagName = (data.tag_name || "1.0.0").replace(/^v/, "").trim();
        const currentVersion = "1.0.0";
        let apkUrl = "", apkSize = 0;
        if (data.assets && Array.isArray(data.assets)) {
          const apk = data.assets.find(a => a.name && a.name.endsWith(".apk"));
          if (apk) { apkUrl = apk.browser_download_url; apkSize = apk.size; }
        }
        const isNewer = tagName !== currentVersion;
        setUpdateInfo({
          currentVersion,
          latestVersion: data.tag_name || "1.0.0",
          releaseName: data.name || ("APP_TITLE " + data.tag_name),
          releaseNotes: data.body || "Performance improvements and new features.",
          apkUrl,
          apkSize,
          isNewer
        });
        setShowUpdateModal(true);
      } catch (err) {
        setUpdateError(err.message || String(err));
        setShowUpdateModal(true);
      } finally {
        setUpdateChecking(false);
      }
    }
  };

  const handleInstallUpdate = () => {
    if (!updateInfo || !updateInfo.apkUrl) return;
    try { we.playShutter(); } catch {}
    if (window.GalaxseeAndroid && typeof window.GalaxseeAndroid.downloadAndInstallUpdate === "function") {
      window.GalaxseeAndroid.downloadAndInstallUpdate(updateInfo.apkUrl);
    } else {
      window.open(updateInfo.apkUrl, "_blank");
    }
  };
""".replace("REPO_OWNER", repo_owner).replace("REPO_NAME", repo_name).replace("APP_TITLE", app_title)

    assert w1_target1 in code, "w1_target1 not found"
    code = code.replace(w1_target1, w1_inject1, 1)

    # B. Prominent Settings Card directly above "About Galaxsee" section
    w1_target2 = 'a.jsxs("div",{className:"space-y-4",children:[a.jsx("h2",{className:`text-xs font-bold ${O?"text-slate-500":"text-slate-400"}`,children:"About Galaxsee, All Rights Reserved & Licensing"}),'
    w1_card = """a.jsxs("div",{className:"space-y-4",children:[
  a.jsx("h2",{className:`text-xs font-bold ${O?"text-slate-500":"text-slate-400"}`,children:"Application Updates & Version"}),
  a.jsx("div",{className:"space-y-3",children:
    a.jsxs("div",{className:`p-5 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${O?"bg-white border-slate-200 shadow-sm":"bg-[#0c101d] border-slate-800/80"}`,children:[
      a.jsxs("div",{className:"space-y-1.5",children:[
        a.jsxs("div",{className:"flex items-center gap-2 font-bold",children:[
          a.jsx(ui,{className:"w-4 h-4 text-emerald-500"}),
          a.jsx("span",{className:O?"text-slate-900":"text-white",children:"APP_TITLE"}),
          a.jsx("span",{className:"px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400",children:"v1.0.0"})
        ]}),
        a.jsx("p",{className:"text-xs text-slate-400 max-w-md",children:"Check for the latest gallery updates, algorithmic optimizations, and security releases directly from official repositories."})
      ]}),
      a.jsxs("button",{onClick:handleCheckUpdates,disabled:updateChecking,className:"px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 transition-all shadow-md cursor-pointer shrink-0 self-start sm:self-auto",children:[
        a.jsx(ui,{className:`w-3.5 h-3.5 ${updateChecking?"animate-spin":""}`}),
        a.jsx("span",{children:updateChecking?"Checking...":"Check for Updates"})
      ]})
    ]})
  })
]}),""".replace("APP_TITLE", app_title) + w1_target2

    assert w1_target2 in code, "w1_target2 not found"
    code = code.replace(w1_target2, w1_card, 1)

    # C. Update modal at bottom of W1
    w1_target3 = ',P&&a.jsx("div",{className:"fixed inset-0 z-50 bg-black/80 backdrop-blur-md'
    w1_modal = """,showUpdateModal&&a.jsx("div",{className:"fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fade-in font-['Plus_Jakarta_Sans',sans-serif]",children:a.jsxs("div",{className:"max-w-lg w-full rounded-3xl bg-[#0e1422] border border-slate-700 text-slate-100 flex flex-col overflow-hidden shadow-2xl",children:[a.jsxs("div",{className:"p-5 border-b border-slate-800 flex items-center justify-between bg-black/30",children:[a.jsxs("div",{className:"flex items-center gap-2.5",children:[a.jsx(Bc,{className:"w-5 h-5 text-emerald-400"}),a.jsxs("div",{children:[a.jsx("h3",{className:"text-sm font-bold text-white",children:"APP_TITLE Update"}),a.jsx("p",{className:"text-[11px] text-slate-400",children:"Official Release & Package Verification"})]})]}),a.jsx("button",{onClick:()=>setShowUpdateModal(!1),className:"p-1.5 rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition-colors cursor-pointer",children:a.jsx(Xt,{className:"w-5 h-5"})})]}),a.jsxs("div",{className:"p-6 space-y-4 text-xs leading-relaxed",children:[updateError?a.jsxs("div",{className:"p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-1",children:[a.jsx("div",{className:"font-bold",children:"Update Check Status"}),a.jsx("div",{children:updateError})]}):updateInfo?a.jsxs("div",{className:"space-y-4",children:[a.jsxs("div",{className:"flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800",children:[a.jsxs("div",{children:[a.jsx("span",{className:"text-slate-400 block text-[11px]",children:"Current Installed"}),a.jsxs("span",{className:"font-mono font-bold text-white",children:["v",updateInfo.currentVersion]})]}),a.jsx(Rc,{className:"w-4 h-4 text-slate-500"}),a.jsxs("div",{children:[a.jsx("span",{className:"text-slate-400 block text-[11px]",children:"Latest Available"}),a.jsx("span",{className:`font-mono font-bold ${updateInfo.isNewer?"text-emerald-400":"text-blue-400"}`,children:updateInfo.latestVersion})]}),a.jsx("span",{className:`px-2.5 py-1 rounded-full text-[10px] font-bold ${updateInfo.isNewer?"bg-emerald-500/20 text-emerald-300":"bg-blue-500/20 text-blue-300"}`,children:updateInfo.isNewer?"Update Ready":"Up to Date"})]}),a.jsxs("div",{className:"space-y-1.5",children:[a.jsx("div",{className:"font-bold text-white",children:updateInfo.releaseName||"Release Highlights"}),a.jsx("div",{className:"p-3 rounded-xl bg-black/30 border border-white/5 font-mono text-[11px] text-slate-300 max-h-36 overflow-y-auto whitespace-pre-wrap",children:updateInfo.releaseNotes||"Performance enhancements and bug fixes."})]}),updateInfo.apkSize>0&&a.jsxs("div",{className:"text-[11px] text-slate-400 flex items-center justify-between",children:[a.jsx("span",{children:"Download Package Size"}),a.jsxs("span",{className:"font-mono font-bold text-slate-200",children:[(updateInfo.apkSize/(1024*1024)).toFixed(2)," MB"]})]}),updateProgress&&a.jsxs("div",{className:"space-y-1.5 pt-2",children:[a.jsxs("div",{className:"flex justify-between text-[11px] font-mono",children:[a.jsx("span",{className:"text-emerald-400",children:"Downloading APK..."}),a.jsxs("span",{className:"text-white font-bold",children:[updateProgress.percent>=0?`${updateProgress.percent}%`:`${(updateProgress.bytes/1048576).toFixed(1)} MB`]})]}),a.jsx("div",{className:"w-full h-2 rounded-full bg-slate-800 overflow-hidden",children:a.jsx("div",{className:"h-full bg-emerald-500 transition-all duration-200",style:{width:`${Math.max(5,updateProgress.percent||0)}%`}})})]})]}):a.jsx("div",{className:"text-center py-6 text-slate-400",children:"No update details available."})]}),a.jsxs("div",{className:"p-4 border-t border-slate-800 bg-black/30 flex items-center justify-between",children:[a.jsx("button",{onClick:()=>setShowUpdateModal(!1),className:"px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-800 transition-colors cursor-pointer",children:"Close"}),updateInfo&&updateInfo.apkUrl&&a.jsxs("button",{onClick:handleInstallUpdate,disabled:!!updateProgress,className:"px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-600/20 cursor-pointer",children:[a.jsx(Yl,{className:"w-4 h-4"}),a.jsx("span",{children:updateProgress?"Installing...":"Download & Install Update"})]})]})]})})""".replace("APP_TITLE", app_title) + w1_target3

    assert w1_target3 in code, "w1_target3 not found"
    code = code.replace(w1_target3, w1_modal, 1)

    print(f"[{'Pro' if is_pro else 'Standard'}] Patched W1 updater components successfully")
    return code

def patch_standard():
    file_path = "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js"
    print(f"[Standard] Reading {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)
    code = patch_w1(code, is_pro=False)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[Standard] Wrote updated bundle to {file_path}. Delta: {len(code) - orig_len}")

if __name__ == "__main__":
    patch_pro()
    patch_standard()
    print("All patches completed successfully!")
