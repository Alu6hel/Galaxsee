import sys

def main():
    src_file = "web_app_dist/assets/index-DpfNch1h.js"
    with open(src_file, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Add triggerHaptic before we
    haptic_fn = """function triggerHaptic(t){try{if(typeof window<"u"){if(window.GalaxseeAndroid&&typeof window.GalaxseeAndroid.performHaptic==="function"){window.GalaxseeAndroid.performHaptic(t||"light");return}if(window.AndroidBridge&&typeof window.AndroidBridge.performHaptic==="function"){window.AndroidBridge.performHaptic(t||"light");return}if(typeof navigator<"u"&&navigator.vibrate){if(t==="reject")navigator.vibrate([25,30,25]);else if(t==="keep"||t==="confirm")navigator.vibrate(40);else navigator.vibrate(15);}}}catch{}}window.__galaxseeHaptic=triggerHaptic;"""

    target_we = "const we={playShutter:()=>{const d=Xi();if(!d)return;const u=d.createOscillator(),"
    replacement_we = haptic_fn + 'const we={playShutter:()=>{triggerHaptic("confirm");const d=Xi();if(!d)return;const u=d.createOscillator(),'
    assert target_we in code, "target_we not found!"
    code = code.replace(target_we, replacement_we, 1)

    # In we.playFavorite, playDelete, playToggle, playKeypad
    code = code.replace('playFavorite:d=>{const u=Xi();', 'playFavorite:d=>{triggerHaptic(d?"keep":"light");const u=Xi();', 1)
    code = code.replace('playDelete:()=>{const d=Xi();', 'playDelete:()=>{triggerHaptic("reject");const d=Xi();', 1)
    code = code.replace('playToggle:()=>{const d=Xi();', 'playToggle:()=>{triggerHaptic("light");const d=Xi();', 1)
    code = code.replace('playKeypad:()=>{const d=Xi();', 'playKeypad:()=>{triggerHaptic("light");const d=Xi();', 1)

    # 2. rv double tap (100% focus crop centered at tap point)
    target_rv_be = "Be=()=>{I>1.1?(U(1),ae({x:0,y:0})):U(2.5),we.playKeypad()}"
    replacement_rv_be = """Be=(tapX,tapY)=>{if(I>1.1){U(1);ae({x:0,y:0});triggerHaptic("light");we.playKeypad()}else{const natW=d.width||(Ue.current?Ue.current.naturalWidth:0)||1920,cliW=Ue.current?Ue.current.clientWidth:window.innerWidth,tgtScale=Math.max(2,Math.min(5,Math.round((natW/Math.max(cliW,1))*10)/10||2.5));U(tgtScale);if(typeof tapX==="number"&&typeof tapY==="number"){const ox=(window.innerWidth/2-tapX)*(tgtScale-1),oy=(window.innerHeight/2-tapY)*(tgtScale-1);ae({x:Math.max(-window.innerWidth*1.2,Math.min(window.innerWidth*1.2,ox)),y:Math.max(-window.innerHeight*1.2,Math.min(window.innerHeight*1.2,oy))})}else{ae({x:0,y:0})}triggerHaptic("confirm");we.playFavorite(!0)}}"""
    assert target_rv_be in code, "target_rv_be not found!"
    code = code.replace(target_rv_be, replacement_rv_be, 1)

    target_rv_la = "$e-qe.current.lastTapTime<300&&Be();"
    assert target_rv_la in code, "target_rv_la not found!"
    code = code.replace(target_rv_la, "$e-qe.current.lastTapTime<300&&Be(qe.current.startTouchPos.x,qe.current.startTouchPos.y);", 1)

    target_rv_dbl = "onDoubleClick:()=>{Be()}"
    assert target_rv_dbl in code, "target_rv_dbl not found!"
    code = code.replace(target_rv_dbl, "onDoubleClick:e=>{Be(e.clientX,e.clientY)}", 1)

    # 3. cv double tap (inline viewer 100% crop centered at tap)
    target_cv_dbl = "se-ge.current.lastTapTime<300&&(D>1.1?(I(1),P({x:0,y:0})):I(2.5),we.playKeypad());"
    replacement_cv_dbl = """se-ge.current.lastTapTime<300&&(D>1.1?(I(1),P({x:0,y:0}),triggerHaptic("light"),we.playKeypad()):(()=>{const natW=d.width||1920,cliW=window.innerWidth||1,tgtScale=Math.max(2,Math.min(5,Math.round((natW/cliW)*10)/10||2.5));I(tgtScale);const ox=(window.innerWidth/2-(ge.current.lastTouchPos?.x||window.innerWidth/2))*(tgtScale-1),oy=(window.innerHeight/2-(ge.current.lastTouchPos?.y||window.innerHeight/2))*(tgtScale-1);P({x:ox,y:oy});triggerHaptic("confirm");we.playFavorite(!0);})());"""
    assert target_cv_dbl in code, "target_cv_dbl not found!"
    code = code.replace(target_cv_dbl, replacement_cv_dbl, 1)

    # 4. ov thumbnail src (use compressed 384px thumbnail instead of full-res RAW/JPEG)
    target_src = "src:u>=4?Re.thumbnailUrl:Re.previewUrl||Re.url"
    assert target_src in code, "target_src not found!"
    code = code.replace(target_src, "src:Re.thumbnailUrl||Re.previewUrl||Re.url", 1)

    # 5. Cull Studio (xy) swipeCardState and horizontal swipe gestures
    target_menu = "const [showProMenu, setShowProMenu] = M.useState(false);"
    replacement_menu = target_menu + "\n  const [swipeCardState, setSwipeCardState] = M.useState({ targetId: null, dx: 0 });"
    assert target_menu in code, "target_menu not found!"
    code = code.replace(target_menu, replacement_menu, 1)

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
    assert target_touch in code, "target_touch not found!"
    code = code.replace(target_touch, replacement_touch, 1)

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

    assert target_slot_img in code, "target_slot_img not found!"
    code = code.replace(target_slot_img, replacement_slot_img, 1)

    # 6. Add safe-area padding to TopBar header (U1)
    target_header_cls = 'className:`h-12 w-full flex items-center justify-between px-3 select-none z-40'
    assert target_header_cls in code, "target_header_cls not found!"
    code = code.replace(target_header_cls, 'className:`h-12 w-full flex items-center justify-between px-3 safe-top-padding select-none z-40', 1)

    # Write back to web_app_dist and android_build assets
    with open("web_app_dist/assets/index-DpfNch1h.js", "w", encoding="utf-8") as f:
        f.write(code)

    with open("android_build/assets/assets/index-DpfNch1h.js", "w", encoding="utf-8") as f:
        f.write(code)

    print("SUCCESS: index-DpfNch1h.js updated in both web_app_dist and android_build!")

if __name__ == "__main__":
    main()
