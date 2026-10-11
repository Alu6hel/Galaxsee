#!/usr/bin/env python3
import sys
import os
import subprocess

def patch_bundle(file_path):
    print(f"\n=======================================================")
    print(f"PATCHING: {file_path}")
    print(f"=======================================================")
    
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} does not exist, skipping.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    orig_len = len(code)

    # 1. Header Brand Logo Unification in U1
    # Replace ALU company logo with Galaxsee cosmic logo
    target_logo_def = 'I=D?"./light alu logo.svg":"./dark alu company logo.svg"'
    repl_logo_def = 'I="./icon-512.svg"'
    if target_logo_def in code:
        code = code.replace(target_logo_def, repl_logo_def, 1)
        print("[1a] Patched header brand logo definition to ./icon-512.svg")
    else:
        print("[1a] Note: target_logo_def not found or already patched")

    target_logo_img = 'a.jsx("img",{src:I,alt:"Alu Logo",onError:E=>{E.currentTarget.src=D?"./light alu logo.png":"./dark alu company logo.png"},className:"w-full h-full object-contain"})'
    repl_logo_img = 'a.jsx("img",{src:I,alt:"Galaxsee Logo",onError:E=>{E.currentTarget.src="./app_icon_512.png"},className:"w-full h-full object-contain"})'
    if target_logo_img in code:
        code = code.replace(target_logo_img, repl_logo_img, 1)
        print("[1b] Patched header brand logo image tag with fallback to ./app_icon_512.png")
    else:
        print("[1b] Note: target_logo_img not found or already patched")

    # 2. Photo Viewer (cv) Active Photo Tracking & Back Button Accessibility
    target_cv_effect = 'M.useEffect(()=>{I(1),P({x:0,y:0}),H(0)},[d.id]);'
    repl_cv_effect = 'M.useEffect(()=>{I(1),P({x:0,y:0}),H(0);if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=d.id;}},[d.id]);'
    if target_cv_effect in code:
        code = code.replace(target_cv_effect, repl_cv_effect, 1)
        print("[2a] Patched cv active photo tracking on d.id change")
    else:
        print("[2a] Note: target_cv_effect not found or already patched")

    target_cv_back = 'a.jsxs("button",{onClick:()=>{we.playKeypad(),h()},className:`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors'
    repl_cv_back = 'a.jsxs("button",{title:"Back to Grid","aria-label":"Back to Grid",onClick:()=>{we.playKeypad(),h()},className:`galaxsee-back-btn flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors'
    if target_cv_back in code:
        code = code.replace(target_cv_back, repl_cv_back, 1)
        print("[2b] Patched cv Back button with accessibility title, aria-label, and galaxsee-back-btn class")
    else:
        print("[2b] Note: target_cv_back not found or already patched")

    # 3. Photo Grid (ov) Scroll Container onScroll Tracker
    target_ov_scroller = 'return a.jsxs("div",{ref:R,onMouseDown:J,'
    repl_ov_scroller = 'return a.jsxs("div",{ref:R,onScroll:$e=>{if(typeof window<"u"&&!window.__galaxsee_is_restoring_scroll){if($e.currentTarget.scrollTop>0)window.__galaxsee_last_grid_scroll=$e.currentTarget.scrollTop;}},onMouseDown:J,'
    if target_ov_scroller in code:
        code = code.replace(target_ov_scroller, repl_ov_scroller, 1)
        print("[3] Added onScroll position tracker to ov ref:R container")
    else:
        print("[3] Note: target_ov_scroller not found or already patched")

    # 4. Photo Card Click & Double Click in ov
    target_ov_click = 'onClick:$e=>{v||$e.shiftKey||$e.metaKey||$e.ctrlKey?($e.stopPropagation(),we.playKeypad(),_(Re.id,$e.shiftKey)):m(Re)},onDoubleClick:$e=>{$e.stopPropagation();m(Re)}'
    repl_ov_click = 'onClick:$e=>{if(v||$e.shiftKey||$e.metaKey||$e.ctrlKey){$e.stopPropagation();we.playKeypad();_(Re.id,$e.shiftKey);}else{if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=Re.id;if(R.current&&R.current.scrollTop>0)window.__galaxsee_last_grid_scroll=R.current.scrollTop;window.__galaxsee_is_restoring_scroll=true;}m(Re);}},onDoubleClick:$e=>{$e.stopPropagation();if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=Re.id;if(R.current&&R.current.scrollTop>0)window.__galaxsee_last_grid_scroll=R.current.scrollTop;window.__galaxsee_is_restoring_scroll=true;}m(Re);}'
    if target_ov_click in code:
        code = code.replace(target_ov_click, repl_ov_click, 1)
        print("[4] Attached last viewed photo and scroll capture to ov card onClick & onDoubleClick")
    else:
        print("[4] Note: target_ov_click not found or already patched")

    # 5. Dynamic Batch Expansion & Multi-Pass Scroll Restoration in ov
    target_ov_batch = 'nt=M.useRef(new Map),[renderLimit,setRenderLimit]=M.useState(60);M.useEffect(()=>{setRenderLimit(60);},[d,ue,B]);'
    repl_ov_batch = (
        'nt=M.useRef(new Map),'
        '[renderLimit,setRenderLimit]=M.useState(()=>{'
        'if(typeof window<"u"&&window.__galaxsee_last_viewed_photo_id&&Ue){'
        'const pIdx=Ue.findIndex(p=>p.id===window.__galaxsee_last_viewed_photo_id);'
        'if(pIdx>=60)return Math.min(100000,pIdx+40);'
        '}return 60;});'
        'M.useEffect(()=>{'
        'if(typeof window<"u"&&window.__galaxsee_is_restoring_scroll)return;'
        'setRenderLimit(60);'
        '},[d,ue,B]);'
        'M.useLayoutEffect(()=>{'
        'const targetScroll=typeof window<"u"?window.__galaxsee_last_grid_scroll:null;'
        'const targetId=typeof window<"u"?window.__galaxsee_last_viewed_photo_id:null;'
        'if(!targetScroll&&!targetId)return;'
        'window.__galaxsee_is_restoring_scroll=true;'
        'if(targetId&&Ue){'
        'const pIdx=Ue.findIndex(p=>p.id===targetId);'
        'if(pIdx>=0){setRenderLimit(prev=>Math.max(prev,pIdx+40));}'
        '}'
        'const doRestore=()=>{'
        'const scroller=R.current;'
        'if(!scroller)return false;'
        'let handled=false;'
        'if(targetId&&nt.current&&nt.current.has(targetId)){'
        'const el=nt.current.get(targetId);'
        'if(el){'
        'const sr=scroller.getBoundingClientRect();'
        'const er=el.getBoundingClientRect();'
        'if(er.top<sr.top||er.bottom>sr.bottom){'
        'const diff=(er.top-sr.top)-(sr.height/2-er.height/2);'
        'scroller.scrollTop+=diff;'
        '}'
        'handled=true;'
        '}'
        '}'
        'if(!handled&&typeof targetScroll==="number"&&targetScroll>0){'
        'scroller.scrollTop=targetScroll;'
        'handled=true;'
        '}'
        'return handled;'
        '};'
        'doRestore();'
        'const af=requestAnimationFrame(()=>{'
        'doRestore();'
        'const t1=setTimeout(()=>{'
        'doRestore();'
        'window.__galaxsee_is_restoring_scroll=false;'
        '},120);'
        'return()=>clearTimeout(t1);'
        '});'
        'return()=>{'
        'cancelAnimationFrame(af);'
        'window.__galaxsee_is_restoring_scroll=false;'
        '};'
        '},[]);'
    )
    if target_ov_batch in code:
        code = code.replace(target_ov_batch, repl_ov_batch, 1)
        print("[5] Replaced ov batching and implemented dynamic expansion & multi-pass useLayoutEffect scroll restoration")
    else:
        print("[5] Note: target_ov_batch not found or already patched")

    # 6. Storage Folders View (Qv) Persistence & Photo Click Memory
    target_qv_state = 'const x=g==="light"||g==="light_galaxsee"||g==="blue_sky",[T,N]=M.useState(null),'
    repl_qv_state = (
        'const x=g==="light"||g==="light_galaxsee"||g==="blue_sky",'
        '[T,_N_raw]=M.useState(()=>{try{return window.__galaxsee_active_folder||null}catch{return null}}),'
        'N=M.useCallback(val=>{_N_raw(val);if(typeof window<"u")window.__galaxsee_active_folder=val;},[]),'
    )
    if target_qv_state in code:
        code = code.replace(target_qv_state, repl_qv_state, 1)
        print("[6a] Wrapped Qv folder state [T,N] with window.__galaxsee_active_folder persistence")
    else:
        print("[6a] Note: target_qv_state not found or already patched")

    target_qv_photo_click = 'onClick: () => u(V),'
    repl_qv_photo_click = 'onClick: () => { if(typeof window<"u"){window.__galaxsee_last_viewed_photo_id=V.id;window.__galaxsee_active_folder=T;} u(V); },'
    if target_qv_photo_click in code:
        code = code.replace(target_qv_photo_click, repl_qv_photo_click, 1)
        print("[6b] Linked Qv photo card click to active photo ID & folder memory")
    else:
        print("[6b] Note: target_qv_photo_click not found or already patched")

    # Write patched file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    new_len = len(code)
    print(f"Finished patching: {orig_len} -> {new_len} ({new_len - orig_len:+d} bytes)")

    # Verify node syntax
    res = subprocess.run(["node", "-c", file_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FATAL: Syntax validation failed for {file_path}:")
        print(res.stderr)
        sys.exit(1)
    else:
        print(f"VERIFICATION SUCCESS: 0 syntax errors in {file_path}!")

if __name__ == "__main__":
    targets = [
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/web_app_dist/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee/android_build/assets/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/web_app_dist/assets/index-DpfNch1h.js",
        "/home/davidalujones/.gemini/antigravity/scratch/Galaxsee_standard/android_build/assets/assets/index-DpfNch1h.js",
    ]
    if len(sys.argv) > 1:
        targets = sys.argv[1:]

    for t in targets:
        patch_bundle(t)
    print("\nALL TARGETS PATCHED AND VERIFIED CLEANLY!")
