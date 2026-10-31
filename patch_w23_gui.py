# patch_w23_gui.py - fixes the cramped top bar and bottom buttons on narrow phones.
# What was wrong: with the pixel font, the top bar (world name, online count, reset timer) did not fit on a phone-wide
# screen, so its words wrapped onto 2-3 lines and bumped into the logo and the sound / find me buttons; the four bottom
# buttons wrapped too ("laser / off"); and the minimap's little legend was hidden behind the bottom bar.
# What it does: the top bar never wraps; on screens 480 px wide or less the words "online" and "resets" are dropped (the
# paw icon and the countdown say the same thing), and on screens 350 px or less the small logo is hidden so the bar fits;
# the bottom buttons get a slightly smaller size and never wrap; the minimap sits a little higher; and the name-your-cat start screen can now scroll on short screens (landscape phones) so
# nothing is cut off when it gets taller.
# Wide screens look exactly the same as before. Works on top of any earlier patches. All-or-nothing, idempotent.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()

def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written.")
        sys.exit(1)
    return text.replace(old, new)

if "/*_gui23*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)

CSS = ("/*_gui23*/.hpill{max-width:calc(100vw - 24px);min-width:0;flex-shrink:1}.hpill span{white-space:nowrap}.hbar .hbtn{white-space:nowrap}"
       "@media (max-width:480px){.hwide{display:none}.hpill{gap:8px!important;padding:6px 10px!important}.hbar{gap:6px!important;padding:12px 8px 18px!important}.hbar .hbtn{font-size:7px!important;padding:9px 9px!important}}"
       "@media (max-width:350px){.hlogo{display:none}.htop{justify-content:center!important}}\n        ")
src = swap(src, ".hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}", CSS + ".hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}", "css")
src = swap(src, '<div style={{position:"fixed",top:0,left:0,right:0,zIndex:10,pointerEvents:"none",display:"flex",justifyContent:"space-between",',
    '<div className="htop" style={{position:"fixed",top:0,left:0,right:0,zIndex:10,pointerEvents:"none",display:"flex",justifyContent:"space-between",', "top bar")
src = swap(src, '<span style={{fontSize:9,color:"#ff4444",textShadow:"0 0 12px rgba(255,50,50,0.55)",letterSpacing:1}}>fikfuk.wtf</span>',
    '<span className="hlogo" style={{fontSize:9,color:"#ff4444",textShadow:"0 0 12px rgba(255,50,50,0.55)",letterSpacing:1}}>fikfuk.wtf</span>', "logo")
src = swap(src, '<div style={{display:"flex",gap:12,alignItems:"center",padding:"6px 12px",background:"rgba(8,8,16,0.55)"',
    '<div className="hpill" style={{display:"flex",gap:12,alignItems:"center",padding:"6px 12px",background:"rgba(8,8,16,0.55)"', "pill")
src = swap(src, "🐾 {onlineCount} online</span>", '🐾 {onlineCount}<span className="hwide"> online</span></span>', "online word")
src = swap(src, "resets {fmtCountdown(resetIn)}</span>", '<span className="hwide">resets </span>{fmtCountdown(resetIn)}</span>', "resets word")
src = swap(src, '<div style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",', '<div className="hbar" style={{position:"fixed",bottom:0,left:0,right:0,zIndex:20,display:"flex",', "bottom bar")
src = swap(src, 'background:"#080810",zIndex:100,padding:20}}>', 'background:"#080810",zIndex:100,padding:20,overflowY:"auto"}}>', "start screen scrolls")
src = swap(src, 'maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22}}>', 'maxWidth:360,width:"100%",display:"flex",flexDirection:"column",gap:22,margin:"auto"}}>', "start card safe centre")
src = swap(src, "MM_Y=H-MM_H-70;", "MM_Y=H-MM_H-96;", "minimap")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 11 edits applied.")
