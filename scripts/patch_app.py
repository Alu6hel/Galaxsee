#!/usr/bin/env python3
import sys

def patch_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Confetti Disabling
    target_export = "h.exports=function(){return F().apply(this,arguments)},h.exports.reset=function(){F().reset()},h.exports.create=R,h.exports.shapeFromPath=V,h.exports.shapeFromText=Ce"
    repl_export = "const _noConfetti=Object.assign((()=>Promise.resolve()),{reset:()=>{},create:()=>(()=>Promise.resolve()),shapeFromPath:()=>{},shapeFromText:()=>{}});h.exports=_noConfetti;h.exports.reset=()=>{};h.exports.create=()=>_noConfetti;h.exports.shapeFromPath=()=>{};h.exports.shapeFromText=()=>{}"
    if target_export in code:
        code = code.replace(target_export, repl_export, 1)
        print("[1/6 a] Neutralized canvas-confetti library export")

    target_fu = "const Fu=eh.exports;eh.exports.create;"
    repl_fu = "const Fu=Object.assign((()=>Promise.resolve()),{reset:()=>{},create:()=>(()=>Promise.resolve()),shapeFromPath:()=>{},shapeFromText:()=>{}});eh.exports=Fu;eh.exports.create=Fu.create;if(typeof window<\"u\"){window.confetti=Fu;}"
    if target_fu in code:
        code = code.replace(target_fu, repl_fu, 1)
        print("[1/6 b] Disabled confetti (Fu)")

    # 2. Sound Removal & Haptic Integration
    # Define triggerHaptic and replace we audio oscillators with silent haptic triggers
    target_we_start = 'function Xi(){try{if(!Il){const d=window.AudioContext||window.webkitAudioContext;d&&(Il=new d)}return Il&&Il.state==="suspended"&&Il.resume(),Il}catch{return null}}const we={'
    replacement_we = '''function triggerHaptic(t){try{if(typeof window<"u"){if(window.GalaxseeAndroid&&typeof window.GalaxseeAndroid.performHaptic==="function"){window.GalaxseeAndroid.performHaptic(t||"light");return}if(window.AndroidBridge&&typeof window.AndroidBridge.performHaptic==="function"){window.AndroidBridge.performHaptic(t||"light");return}if(typeof navigator<"u"&&navigator.vibrate){if(t==="reject")navigator.vibrate([25,30,25]);else if(t==="keep"||t==="confirm")navigator.vibrate(40);else navigator.vibrate(15);}}}catch{}}window.__galaxseeHaptic=triggerHaptic;function Xi(){return null;}const we={playShutter:()=>{triggerHaptic("confirm")},playFavorite:d=>{triggerHaptic(d?"keep":"light")},playDelete:()=>{triggerHaptic("reject")},playVaultUnlock:()=>{triggerHaptic("confirm")},playUnlock:()=>{triggerHaptic("confirm")},playFocus:()=>{triggerHaptic("light")},playKeypad:()=>{triggerHaptic("light")},playToggle:()=>{triggerHaptic("light")},_disabled:true,'''
    
    if target_we_start in code:
        code = code.replace(target_we_start, replacement_we, 1)
        print("[2/6] Silenced all sound oscillators & added native haptic triggers")
    else:
        print("[2/6] Warning: target_we_start not found")

    # 3. Grid Thumbnail & Virtualization optimization
    target_src = "src:u>=4?Re.thumbnailUrl:Re.previewUrl||Re.url"
    replacement_src = "src:Re.thumbnailUrl||Re.previewUrl||Re.url"
    if target_src in code:
        code = code.replace(target_src, replacement_src, 1)
        print("[3/6] Updated grid thumbnails to load downsampled 384px thumbnails")
    else:
        print("[3/6] Warning: target_src not found")

    # 4. Photo Viewer (rv and cv) Double-Tap 100% Focus Crop & Pinch-to-Zoom
    target_rv_be = "Be=()=>{I>1.1?(U(1),ae({x:0,y:0})):U(2.5),we.playKeypad()}"
    replacement_rv_be = '''Be=(tapX,tapY)=>{if(I>1.1){U(1);ae({x:0,y:0});triggerHaptic("light");}else{const natW=d.width||(Ue.current?Ue.current.naturalWidth:0)||1920,cliW=Ue.current?Ue.current.clientWidth:window.innerWidth,tgtScale=Math.max(2,Math.min(5,Math.round((natW/Math.max(cliW,1))*10)/10||2.5));U(tgtScale);if(typeof tapX==="number"&&typeof tapY==="number"){const ox=(window.innerWidth/2-tapX)*(tgtScale-1),oy=(window.innerHeight/2-tapY)*(tgtScale-1);ae({x:Math.max(-window.innerWidth*1.2,Math.min(window.innerWidth*1.2,ox)),y:Math.max(-window.innerHeight*1.2,Math.min(window.innerHeight*1.2,oy))});}else{ae({x:0,y:0});}triggerHaptic("confirm");}}'''
    if target_rv_be in code:
        code = code.replace(target_rv_be, replacement_rv_be, 1)
        print("[4/6 a] Added 100% crop center-on-tap in fullscreen viewer (rv)")
    else:
        print("[4/6 a] Warning: target_rv_be not found")

    target_rv_la = "$e-qe.current.lastTapTime<300&&Be();"
    if target_rv_la in code:
        code = code.replace(target_rv_la, "$e-qe.current.lastTapTime<300&&Be(qe.current.startTouchPos.x,qe.current.startTouchPos.y);", 1)
        print("[4/6 b] Linked tap coords to double-tap handler in rv")
    else:
        print("[4/6 b] Warning: target_rv_la not found")

    target_rv_dbl = "onDoubleClick:()=>{Be()}"
    if target_rv_dbl in code:
        code = code.replace(target_rv_dbl, "onDoubleClick:e=>{Be(e.clientX,e.clientY)}", 1)
        print("[4/6 c] Linked mouse double-click coords in rv")
    else:
        print("[4/6 c] Warning: target_rv_dbl not found")

    target_cv_dbl = "se-ge.current.lastTapTime<300&&(D>1.1?(I(1),P({x:0,y:0})):I(2.5),we.playKeypad());"
    replacement_cv_dbl = '''se-ge.current.lastTapTime<300&&(D>1.1?(I(1),P({x:0,y:0}),triggerHaptic("light")):(function(){const natW=d.width||1920,cliW=window.innerWidth||1,tgtScale=Math.max(2,Math.min(5,Math.round((natW/cliW)*10)/10||2.5));I(tgtScale);const ox=(window.innerWidth/2-(ge.current.lastTouchPos?.x||window.innerWidth/2))*(tgtScale-1),oy=(window.innerHeight/2-(ge.current.lastTouchPos?.y||window.innerHeight/2))*(tgtScale-1);P({x:ox,y:oy});triggerHaptic("confirm");})());'''
    if target_cv_dbl in code:
        code = code.replace(target_cv_dbl, replacement_cv_dbl, 1)
        print("[4/6 d] Added 100% crop center-on-tap in detail viewer (cv)")
    else:
        print("[4/6 d] Warning: target_cv_dbl not found")

    # In cv touch start, save lastTouchPos
    target_cv_touch_start = "X({x:oe.clientX-U.x,y:oe.clientY-U.y});ge.current.startTime=Date.now();ge.current.initialDist=0;"
    replacement_cv_touch_start = "X({x:oe.clientX-U.x,y:oe.clientY-U.y});ge.current.lastTouchPos={x:oe.clientX,y:oe.clientY};ge.current.startTime=Date.now();ge.current.initialDist=0;"
    if target_cv_touch_start in code:
        code = code.replace(target_cv_touch_start, replacement_cv_touch_start, 1)
        print("[4/6 e] Captured tap coords on cv touch start")

    # 5. Mobile Swipe Gestures in Cull Studio (xy)
    target_menu = "const [showProMenu, setShowProMenu] = M.useState(false);"
    replacement_menu = target_menu + "\n  const [swipeCardState, setSwipeCardState] = M.useState({ targetId: null, dx: 0 });"
    if target_menu in code and "const [swipeCardState, setSwipeCardState]" not in code:
        code = code.replace(target_menu, replacement_menu, 1)
        print("[5/6 a] Added swipeCardState in xy")

    target_touch = """  const handleTouchStart = (e, photoId) => {
    const cur = getSlotTransform(photoId);
    if (e.touches.length === 1) {
      activeDrag.current = {
        isDragging: true,
        targetId: photoId,
        startX: e.touches[0].clientX,
        startY: e.touches[0].clientY,
        origX: cur.x,
        origY: cur.y,
        origScale: cur.scale,
        touchDist: null
      };
    } else if (e.touches.length === 2) {
      const dist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
      const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      activeDrag.current = {
        isDragging: true,
        targetId: photoId,
        startX: midX,
        startY: midY,
        origX: cur.x,
        origY: cur.y,
        origScale: cur.scale,
        touchDist: dist
      };
    }
  };

  const handleTouchMove = (e) => {
    if (!activeDrag.current.isDragging || !activeDrag.current.targetId) return;
    const { targetId, startX, startY, origX, origY, origScale, touchDist } = activeDrag.current;
    if (e.touches.length === 1 && touchDist === null) {
      const dx = e.touches[0].clientX - startX;
      const dy = e.touches[0].clientY - startY;
      applyTransform(targetId, origX + dx, origY + dy, origScale, true);
    } else if (e.touches.length === 2 && touchDist !== null) {
      const dist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
      const ratio = dist / (touchDist || 1);
      const newScale = Math.max(0.5, Math.min(6, origScale * ratio));
      const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      const dx = midX - startX;
      const dy = midY - startY;
      applyTransform(targetId, origX + dx, origY + dy, newScale, true);
    }
  };

  const handleTouchEnd = (e) => {
    if (e.touches.length === 0) {
      activeDrag.current.isDragging = false;
      activeDrag.current.targetId = null;
      activeDrag.current.touchDist = null;
    } else if (e.touches.length === 1 && activeDrag.current.targetId) {
      const cur = getSlotTransform(activeDrag.current.targetId);
      activeDrag.current = {
        isDragging: true,
        targetId: activeDrag.current.targetId,
        startX: e.touches[0].clientX,
        startY: e.touches[0].clientY,
        origX: cur.x,
        origY: cur.y,
        origScale: cur.scale,
        touchDist: null
      };
    }
  };"""

    replacement_touch = """  const handleTouchStart = (e, photoId) => {
    const cur = getSlotTransform(photoId);
    if (e.touches.length === 1) {
      activeDrag.current = {
        isDragging: true,
        targetId: photoId,
        startX: e.touches[0].clientX,
        startY: e.touches[0].clientY,
        origX: cur.x,
        origY: cur.y,
        origScale: cur.scale,
        touchDist: null,
        swipeActive: false,
        swipeDx: 0
      };
    } else if (e.touches.length === 2) {
      const dist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
      const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      activeDrag.current = {
        isDragging: true,
        targetId: photoId,
        startX: midX,
        startY: midY,
        origX: cur.x,
        origY: cur.y,
        origScale: cur.scale,
        touchDist: dist,
        swipeActive: false,
        swipeDx: 0
      };
    }
  };

  const handleTouchMove = (e) => {
    if (!activeDrag.current.isDragging || !activeDrag.current.targetId) return;
    const { targetId, startX, startY, origX, origY, origScale, touchDist } = activeDrag.current;
    if (e.touches.length === 1 && touchDist === null) {
      const dx = e.touches[0].clientX - startX;
      const dy = e.touches[0].clientY - startY;
      if (origScale <= 1.15 && (Math.abs(dx) > 12 || activeDrag.current.swipeActive)) {
        if (Math.abs(dx) > Math.abs(dy) * 0.75 || activeDrag.current.swipeActive) {
          activeDrag.current.swipeActive = true;
          activeDrag.current.swipeDx = dx;
          setSwipeCardState({ targetId, dx });
          const el = R.current.get(targetId);
          if (el) {
            const rot = Math.max(-14, Math.min(14, dx * 0.05));
            el.style.transform = "translate3d(" + dx + "px, " + (dy * 0.15) + "px, 0px) rotate(" + rot + "deg)";
            el.style.transition = "none";
          }
          return;
        }
      }
      applyTransform(targetId, origX + dx, origY + dy, origScale, true);
    } else if (e.touches.length === 2 && touchDist !== null) {
      const dist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
      const ratio = dist / (touchDist || 1);
      const newScale = Math.max(0.5, Math.min(6, origScale * ratio));
      const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      const dx = midX - startX;
      const dy = midY - startY;
      applyTransform(targetId, origX + dx, origY + dy, newScale, true);
    }
  };

  const handleTouchEnd = (e) => {
    if (activeDrag.current.swipeActive && activeDrag.current.targetId) {
      const targetId = activeDrag.current.targetId;
      const dx = activeDrag.current.swipeDx || 0;
      activeDrag.current.swipeActive = false;
      activeDrag.current.swipeDx = 0;
      setSwipeCardState({ targetId: null, dx: 0 });
      const el = R.current.get(targetId);
      if (dx > 60) {
        if (el) {
          el.style.transition = "transform 0.2s ease-out, opacity 0.2s ease-out";
          el.style.transform = "translate3d(350px, 0px, 0px) rotate(16deg)";
          el.style.opacity = "0";
        }
        if (typeof triggerHaptic === "function") triggerHaptic("keep");
        setTimeout(() => {
          if (el) {
            el.style.transition = "none";
            el.style.transform = "translate3d(0px, 0px, 0px) scale(1)";
            el.style.opacity = "1";
          }
          j(targetId, "keep");
        }, 160);
        return;
      } else if (dx < -60) {
        if (el) {
          el.style.transition = "transform 0.2s ease-out, opacity 0.2s ease-out";
          el.style.transform = "translate3d(-350px, 0px, 0px) rotate(-16deg)";
          el.style.opacity = "0";
        }
        if (typeof triggerHaptic === "function") triggerHaptic("reject");
        setTimeout(() => {
          if (el) {
            el.style.transition = "none";
            el.style.transform = "translate3d(0px, 0px, 0px) scale(1)";
            el.style.opacity = "1";
          }
          j(targetId, "reject");
        }, 160);
        return;
      } else {
        if (el) {
          el.style.transition = "transform 0.2s ease-out";
          el.style.transform = "translate3d(0px, 0px, 0px) scale(1)";
        }
      }
    }
    if (e.touches.length === 0) {
      activeDrag.current.isDragging = false;
      activeDrag.current.targetId = null;
      activeDrag.current.touchDist = null;
      activeDrag.current.swipeActive = false;
      activeDrag.current.swipeDx = 0;
    } else if (e.touches.length === 1 && activeDrag.current.targetId) {
      const cur = getSlotTransform(activeDrag.current.targetId);
      activeDrag.current = {
        isDragging: true,
        targetId: activeDrag.current.targetId,
        startX: e.touches[0].clientX,
        startY: e.touches[0].clientY,
        origX: cur.x,
        origY: cur.y,
        origScale: cur.scale,
        touchDist: null,
        swipeActive: false,
        swipeDx: 0
      };
    }
  };"""

    if target_touch in code:
        code = code.replace(target_touch, replacement_touch, 1)
        print("[5/6 b] Replaced touch handlers with swipe gestures in xy")
    else:
        print("[5/6 b] Warning: target_touch not found in xy")

    target_slot_img = """              a.jsx("div", {
                className: "flex-1 relative overflow-hidden flex items-center justify-center p-2 pointer-events-none select-none",
                children: a.jsx("div", {
                  ref: nt => { nt ? R.current.set(te.id, nt) : R.current.delete(te.id); },
                  style: { transform: "translate3d(0px, 0px, 0px) scale(1)" },
                  className: "relative w-full h-full flex items-center justify-center pointer-events-none select-none",
                  children: a.jsx("img", {
                    src: te.previewUrl || te.url,
                    alt: te.title,
                    draggable: !1,
                    className: "max-h-full max-w-full object-contain select-none"
                  })
                })
              }),"""

    replacement_slot_img = """              a.jsxs("div", {
                className: "flex-1 relative overflow-hidden flex items-center justify-center p-2 pointer-events-none select-none",
                children: [
                  swipeCardState.targetId === te.id && swipeCardState.dx > 25 && a.jsx("div", {
                    className: "cull-swipe-badge-keep",
                    style: { opacity: Math.min(1, (swipeCardState.dx - 15) / 35) },
                    children: "KEEP ✓"
                  }),
                  swipeCardState.targetId === te.id && swipeCardState.dx < -25 && a.jsx("div", {
                    className: "cull-swipe-badge-reject",
                    style: { opacity: Math.min(1, (-swipeCardState.dx - 15) / 35) },
                    children: "REJECT ✕"
                  }),
                  a.jsx("div", {
                    ref: nt => { nt ? R.current.set(te.id, nt) : R.current.delete(te.id); },
                    style: { transform: "translate3d(0px, 0px, 0px) scale(1)" },
                    className: "relative w-full h-full flex items-center justify-center pointer-events-none select-none",
                    children: a.jsx("img", {
                      src: te.previewUrl || te.url,
                      alt: te.title,
                      draggable: !1,
                      className: "max-h-full max-w-full object-contain select-none"
                    })
                  })
                ]
              }),"""

    if target_slot_img in code:
        code = code.replace(target_slot_img, replacement_slot_img, 1)
        print("[5/6 c] Added swipe badges inside slot card in xy")
    else:
        print("[5/6 c] Warning: target_slot_img not found in xy")

    # 6. Safe area insets on sidebar aside
    target_sidebar = 'aside",{"data-tour":"sidebar-nav",className:`flex flex-col justify-between py-2 select-none'
    replacement_sidebar = 'aside",{"data-tour":"sidebar-nav",className:`flex flex-col justify-between py-2 safe-bottom-padding select-none'
    if target_sidebar in code:
        code = code.replace(target_sidebar, replacement_sidebar, 1)
        print("[6/6] Added safe-bottom-padding to sidebar navigation")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Patch applied successfully to", filepath)

if __name__ == "__main__":
    patch_js("web_app_dist/assets/index-DpfNch1h.js")
