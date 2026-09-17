import os

def update_bundle(file_path, is_pro=True):
    print(f"Updating {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    orig_len = len(code)

    # 1. Audio Engine
    target_xi = """let Il=null;
function isAppAudioMuted(){
  try{return typeof localStorage!=="undefined"&&localStorage.getItem("galaxsee_sound_muted")==="true";}catch{return false;}
}
window.__galaxsee_isAudioMuted=isAppAudioMuted;
function Xi(){
  try{
    if(isAppAudioMuted()) return null;
    if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d);}
    return Il&&Il.state==="suspended"&&Il.resume(),Il;
  }catch{return null;}
}"""
    repl_xi = """let Il=null;
function isAppAudioMuted(){
  try{return typeof localStorage!=="undefined"&&localStorage.getItem("galaxsee_sound_muted")==="true";}catch{return false;}
}
window.__galaxsee_isAudioMuted=isAppAudioMuted;
if(typeof window!=="undefined"){
  window.addEventListener("galaxsee_sound_toggled",(e)=>{
    try{
      const m=isAppAudioMuted();
      if(m&&Il&&Il.state==="running")Il.suspend();
      document.querySelectorAll("video,audio").forEach(el=>{el.muted=m;});
    }catch(err){}
  });
  document.addEventListener("play",(e)=>{
    if(isAppAudioMuted()&&e.target&&(e.target.tagName==="VIDEO"||e.target.tagName==="AUDIO")){
      e.target.muted=true;
    }
  },true);
}
function Xi(){
  try{
    if(isAppAudioMuted()) return null;
    if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d);}
    return Il&&Il.state==="suspended"&&Il.resume(),Il;
  }catch{return null;}
}"""
    assert target_xi in code, "target_xi not found"
    code = code.replace(target_xi, repl_xi, 1)

    # 2. Header Mute Button Styling
    target_mute_hdr = """a.jsx("button", {
      type: "button",
      onClick: toggleSound,
      className: `p-2 rounded-lg transition-colors mr-1 cursor-pointer ${soundMuted ? (D ? "bg-rose-100 text-rose-700 hover:bg-rose-200 shadow-sm" : "bg-rose-950/60 text-rose-400 border border-rose-500/40 hover:bg-rose-900/60 shadow-sm") : (D ? "hover:bg-slate-100 text-slate-600 hover:text-slate-900" : "hover:bg-white/10 text-slate-300 hover:text-white")}`,
      title: soundMuted ? "Audio Muted — Click to Enable Sounds" : "Sounds Enabled — Click to Mute Audio",
      "aria-label": soundMuted ? "Unmute Application Sound" : "Mute Application Sound",
      children: a.jsx("span", { className: "text-sm leading-none", children: soundMuted ? "🔇" : "🔊" })
    }),"""

    repl_mute_hdr = """a.jsx("button", {
      type: "button",
      onClick: toggleSound,
      className: `p-2 rounded-lg transition-all mr-1.5 cursor-pointer flex items-center justify-center ${soundMuted ? "bg-rose-600 text-white shadow-md shadow-rose-600/40 hover:bg-rose-500" : (x === "light" ? "hover:bg-slate-100 text-slate-600 hover:text-slate-900" : "hover:bg-white/10 text-slate-300 hover:text-white")}`,
      title: soundMuted ? "All Sounds Muted — Click to Enable Audio" : "Sounds Enabled — Click to Mute All Sounds",
      "aria-label": soundMuted ? "Unmute Application Audio" : "Mute All Application Audio",
      children: a.jsx("span", { className: "text-sm leading-none select-none", children: soundMuted ? "🔇" : "🔊" })
    }),"""
    assert target_mute_hdr in code, "target_mute_hdr not found"
    code = code.replace(target_mute_hdr, repl_mute_hdr, 1)

    # 3. Settings Card Title
    target_card_title = 'a.jsx("div",{className:`text-xs font-bold ${O?"text-slate-900":"text-white"}`,children:"Application Sound & Audio Feedback"})'
    repl_card_title = 'a.jsx("div",{className:`text-xs font-bold ${O?"text-slate-900":"text-white"}`,children:"Mute All Sounds from App"})'
    assert target_card_title in code, "target_card_title not found"
    code = code.replace(target_card_title, repl_card_title, 1)

    # 4. Crop initial state: { x: 0.05, y: 0.05, w: 0.9, h: 0.9 }
    target_crop_state = "const [cropRect, setCropRect] = M.useState({ x: 0, y: 0, w: 1, h: 1 });"
    repl_crop_state = "const [cropRect, setCropRect] = M.useState({ x: 0.05, y: 0.05, w: 0.9, h: 0.9 });"
    assert target_crop_state in code, "target_crop_state not found"
    code = code.replace(target_crop_state, repl_crop_state, 1)

    # 5. v() Dm call: render full image when w === "crop", so user can drag handles freely over reference image
    target_v_dm = 'ae?Dm(J,Ie,Fl(),Tc,0,!1,!1,"Free",{x:0,y:0,w:1,h:1}):Dm(J,Ie,x,N,$,De,je,K,cropRect)'
    repl_v_dm = 'ae?Dm(J,Ie,Fl(),Tc,0,!1,!1,"Free",{x:0,y:0,w:1,h:1}):Dm(J,Ie,x,N,$,De,je,K,w==="crop"?{x:0,y:0,w:1,h:1}:cropRect)'
    assert target_v_dm in code, "target_v_dm not found"
    code = code.replace(target_v_dm, repl_v_dm, 1)

    # 6. ke save handler pre-save Dm execution
    target_ke = 'ke=J=>{if(R(!1),we.playShutter(),!ce.current)return;const Ie=ce.current,ze=Ie.toDataURL("image/jpeg",.95);'
    repl_ke = 'ke=J=>{if(R(!1),we.playShutter(),!ce.current)return;if(ce.current&&V.current)Dm(ce.current,V.current,x,N,$,De,je,K,cropRect);const Ie=ce.current,ze=Ie.toDataURL("image/jpeg",.95);'
    assert target_ke in code, "target_ke not found"
    code = code.replace(target_ke, repl_ke, 1)

    # 7. Crop toolbar Apply and Reset buttons
    target_reset_btn = '''a.jsx("button", {
        type: "button",
        onClick: () => setCropRect({ x: 0, y: 0, w: 1, h: 1 }),
        className: "px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 font-bold text-xs flex items-center gap-1 transition-all cursor-pointer shrink-0",
        title: "Reset Crop Selection to Full Image",
        children: [a.jsx("span", { children: "↺" }), a.jsx("span", { children: "Reset Crop" })]
      }),'''

    repl_crop_btns = '''a.jsx("button", {
        type: "button",
        onClick: () => y("adjust"),
        className: "px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-1 shadow-md transition-all cursor-pointer shrink-0",
        title: "Apply Crop and Return to Adjustments",
        children: [a.jsx("span", { children: "✓" }), a.jsx("span", { children: "Apply Crop" })]
      }),
      a.jsx("button", {
        type: "button",
        onClick: () => { setCropRect({ x: 0.05, y: 0.05, w: 0.9, h: 0.9 }); X("Free"); },
        className: "px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 font-bold text-xs flex items-center gap-1 transition-all cursor-pointer shrink-0",
        title: "Reset Crop Selection to Full Image",
        children: [a.jsx("span", { children: "↺" }), a.jsx("span", { children: "Reset Crop" })]
      }),'''
    assert target_reset_btn in code, "target_reset_btn not found"
    code = code.replace(target_reset_btn, repl_crop_btns, 1)

    # 8. Crop overlay: remove overflow-hidden so handles and badge never get clipped
    target_overlay_cls = 'className: "absolute inset-0 select-none overflow-hidden touch-none",'
    repl_overlay_cls = 'className: "absolute inset-0 select-none touch-none pointer-events-auto",'
    assert target_overlay_cls in code, "target_overlay_cls not found"
    code = code.replace(target_overlay_cls, repl_overlay_cls, 1)

    # 9. Corner handles styling: make larger and add z-30
    target_corner_handles = 'corner === "nw" ? "-top-2 -left-2 cursor-nwse-resize" :'
    if target_corner_handles in code:
        code = code.replace(
            'className: `absolute w-4 h-4 bg-white border-2 border-blue-600 rounded-full shadow-lg ${',
            'className: `absolute w-5 h-5 bg-white border-2 border-blue-600 rounded-full shadow-2xl z-30 ${',
            1
        )
        code = code.replace('-top-2 -left-2', '-top-2.5 -left-2.5', 1)
        code = code.replace('-top-2 -right-2', '-top-2.5 -right-2.5', 1)
        code = code.replace('-bottom-2 -left-2', '-bottom-2.5 -left-2.5', 1)
        code = code.replace('-bottom-2 -right-2', '-bottom-2.5 -right-2.5', 1)

    # 10. Edge handles styling: add z-30
    code = code.replace(
        'className: "absolute -top-1.5 left-1/2 -translate-x-1/2 w-6 h-2.5 bg-white border border-blue-600 rounded-full cursor-ns-resize shadow-md",',
        'className: "absolute -top-1.5 left-1/2 -translate-x-1/2 w-8 h-3 bg-white border border-blue-600 rounded-full cursor-ns-resize shadow-md z-30",',
        1
    )
    code = code.replace(
        'className: "absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-6 h-2.5 bg-white border border-blue-600 rounded-full cursor-ns-resize shadow-md",',
        'className: "absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-8 h-3 bg-white border border-blue-600 rounded-full cursor-ns-resize shadow-md z-30",',
        1
    )
    code = code.replace(
        'className: "absolute -left-1.5 top-1/2 -translate-y-1/2 h-6 w-2.5 bg-white border border-blue-600 rounded-full cursor-ew-resize shadow-md",',
        'className: "absolute -left-1.5 top-1/2 -translate-y-1/2 h-8 w-3 bg-white border border-blue-600 rounded-full cursor-ew-resize shadow-md z-30",',
        1
    )
    code = code.replace(
        'className: "absolute -right-1.5 top-1/2 -translate-y-1/2 h-6 w-2.5 bg-white border border-blue-600 rounded-full cursor-ew-resize shadow-md",',
        'className: "absolute -right-1.5 top-1/2 -translate-y-1/2 h-8 w-3 bg-white border border-blue-600 rounded-full cursor-ew-resize shadow-md z-30",',
        1
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Successfully updated {file_path}. New length: {len(code)} (delta: {len(code) - orig_len})")

if __name__ == "__main__":
    # Run on Galaxsee Pro
    update_bundle("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js", is_pro=True)
    update_bundle("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/android_build/assets/assets/index-DpfNch1h.js", is_pro=True)

    # Run on Galaxsee Standard
    update_bundle("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js", is_pro=False)
    update_bundle("/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build/assets/assets/index-DpfNch1h.js", is_pro=False)
