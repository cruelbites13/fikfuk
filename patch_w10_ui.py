# patch_w10_ui.py - calmer, more polished controls (same buttons, same behaviour, nothing new on screen):
# - buttons become soft glass pills: rounded, a faint top highlight, blur behind them, lift on hover, press on tap
#   (they keep their own colours: red laser, red confess, blue letter, amber tag)
# - the top-right info (world, online, reset timer, day/night) sits in one quiet pill; the world name takes the world's colour
# - minimap: rounded frame in the world's colour, portal rings shown as small purple circles, and the tiny colour legend
#   fades away after the first half minute so the screen stays clean
# Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "/*_ui10*/" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "const PORTALS=" not in src:
    print("ABORT: apply patch_w3_portals.py first. Nothing written."); sys.exit(1)
def swap(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {n}. Nothing written."); sys.exit(1)
    return text.replace(old, new)

src = swap(src, ".hbtn{transition:background .15s,box-shadow .15s;cursor:pointer;font-family:'Press Start 2P',monospace;}",
 ".hbtn{transition:transform .12s,filter .15s,box-shadow .15s;cursor:pointer;font-family:'Press Start 2P',monospace;border-radius:12px!important;border-width:1px!important;"
 "backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);background-image:linear-gradient(180deg,rgba(255,255,255,0.10),rgba(255,255,255,0) 60%)!important;"
 "-webkit-tap-highlight-color:transparent;}/*_ui10*/", "button css")
src = swap(src, ".hbtn:hover{background:rgba(255,50,50,0.2)!important;box-shadow:0 0 20px rgba(255,50,50,0.55)!important;}",
 ".hbtn:hover{filter:brightness(1.35);transform:translateY(-1px);}.hbtn:active{transform:translateY(1px) scale(.98);filter:brightness(1.1);}", "button hover")
src = swap(src, '<div style={{display:"flex",gap:12,alignItems:"center"}}>',
 '<div style={{display:"flex",gap:12,alignItems:"center",padding:"6px 12px",background:"rgba(8,8,16,0.55)",border:"1px solid rgba(255,255,255,0.08)",borderRadius:999,backdropFilter:"blur(8px)",WebkitBackdropFilter:"blur(8px)"}}>', "info pill")
src = swap(src, '<span style={{fontSize:7,color:"rgba(255,255,255,0.45)"}}>{worldName}</span>',
 '<span style={{fontSize:7,color:({"Malkuth Gate":"#b9b1f0","Glass Garden":"#e0c0ff","Root Archive":"#8fd070"})[worldName]||"#fff",textShadow:"0 0 8px currentColor"}}>{worldName}</span>', "world name colour")

src = swap(src, 'ctx.fillStyle="rgba(0,0,0,0.7)";ctx.strokeStyle="rgba(255,50,50,0.3)";ctx.lineWidth=1;',
 'const _ac=({malkuth:"150,140,255",yesod:"225,175,255",netzach:"130,225,130"})[WORLD_ID]||"150,140,255";'
 'ctx.fillStyle="rgba(6,6,16,0.72)";ctx.strokeStyle="rgba("+_ac+",0.5)";ctx.lineWidth=1.5;', "minimap colours")
src = swap(src, "ctx.fillRect(MM_X,MM_Y,MM_W,MM_H);ctx.strokeRect(MM_X,MM_Y,MM_W,MM_H);",
 "rrect(ctx,MM_X,MM_Y,MM_W,MM_H,8);ctx.fill();ctx.stroke();"
 'ctx.fillStyle="rgba("+_ac+",0.05)";ctx.fillRect(MM_X+3,MM_Y+3,MM_W-6,(MM_H-6)/2);', "minimap frame")
src = swap(src, 'ctx.strokeStyle="rgba(255,255,255,0.2)";ctx.strokeRect(vpx,vpy,vpw,vph);',
 'ctx.strokeStyle="rgba(255,255,255,0.2)";ctx.strokeRect(vpx,vpy,vpw,vph);'
 '{const _pp=PORTALS[WORLD_ID]||{};ctx.lineWidth=1.5;ctx.strokeStyle="rgba(200,150,255,0.95)";for(const _k in _pp){ctx.beginPath();ctx.arc(MM_X+(_pp[_k][0]/WORLD_W)*MM_W,MM_Y+(_pp[_k][1]/WORLD_H)*MM_H,2.5,0,Math.PI*2);ctx.stroke();}ctx.lineWidth=1;}', "portal dots")
src = swap(src, "legend.forEach((l,i)=>{", "ctx.globalAlpha=Math.max(0,Math.min(1,(1500-s.frame)/300));legend.forEach((l,i)=>{", "legend fade")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 8 edits applied (glass buttons, info pill, minimap frame, portal dots, fading legend).")
